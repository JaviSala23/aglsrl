from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from .models import Ubicacion, Almacenaje, Stock, TipoAlmacenaje, EstadoAlmacenaje
from .forms import UbicacionForm, AlmacenajeForm


def dashboard(request):
    """Dashboard principal de almacenamiento"""
    # Estadísticas generales
    total_ubicaciones = Ubicacion.objects.filter(activo=True).count()
    total_almacenajes = Almacenaje.objects.filter(activo=True).count()
    almacenajes_ocupados = Stock.objects.filter(cantidad_kg__gt=0).values('almacenaje').distinct().count()
    total_stock = Stock.objects.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    
    # Stock por ubicación
    stock_por_ubicacion = Stock.objects.select_related('ubicacion').values(
        'ubicacion__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')[:10]
    
    # Ocupación por tipo de almacenaje
    ocupacion_tipos = Stock.objects.select_related('almacenaje').values(
        'almacenaje__tipo'
    ).annotate(
        total_kg=Sum('cantidad_kg'),
        count_almacenajes=Count('almacenaje', distinct=True)
    ).order_by('-total_kg')
    
    # Ubicaciones más utilizadas
    ubicaciones_activas = Stock.objects.select_related('ubicacion').values(
        'ubicacion__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg'),
        count_almacenajes=Count('almacenaje', distinct=True)
    ).order_by('-total_kg')[:10]
    
    context = {
        'total_ubicaciones': total_ubicaciones,
        'total_almacenajes': total_almacenajes,
        'almacenajes_ocupados': almacenajes_ocupados,
        'total_stock': total_stock,
        'stock_por_ubicacion': stock_por_ubicacion,
        'ocupacion_tipos': ocupacion_tipos,
        'ubicaciones_activas': ubicaciones_activas,
    }
    
    return render(request, 'almacenamiento/dashboard.html', context)


def ubicaciones_list(request):
    """Lista de ubicaciones con filtros y búsqueda"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    from .forms import UbicacionForm
    
    ubicaciones_list = Ubicacion.objects.prefetch_related('almacenajes', 'stocks').all().order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        ubicaciones_list = ubicaciones_list.filter(
            Q(nombre__icontains=search) |
            Q(encargado__username__icontains=search) |
            Q(encargado__first_name__icontains=search) |
            Q(encargado__last_name__icontains=search) |
            Q(direccion__icontains=search)
        )
    
    # Filtro por tipo
    tipo_filter = request.GET.get('tipo', '')
    if tipo_filter:
        ubicaciones_list = ubicaciones_list.filter(tipo=tipo_filter)
    
    # Filtro por estado
    activo_filter = request.GET.get('activo', '')
    if activo_filter:
        ubicaciones_list = ubicaciones_list.filter(activo=(activo_filter == 'true'))
    
    # Paginación
    paginator = Paginator(ubicaciones_list, 12)
    page_number = request.GET.get('page')
    ubicaciones = paginator.get_page(page_number)
    
    context = {
        'ubicaciones': ubicaciones,
        'search': search,
        'tipo_filter': tipo_filter,
        'activo_filter': activo_filter,
        'total_ubicaciones': ubicaciones_list.count(),
    }
    
    return render(request, 'almacenamiento/ubicaciones_list.html', context)


def ubicacion_detail(request, pk):
    """Detalle de una ubicación específica"""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    
    # Almacenajes de esta ubicación
    almacenajes = Almacenaje.objects.filter(ubicacion=ubicacion, activo=True).order_by('codigo')
    
    # Stock por almacenaje
    stocks = Stock.objects.filter(ubicacion=ubicacion).select_related(
        'almacenaje', 'mercaderia', 'mercaderia__grano'
    ).order_by('almacenaje__codigo', 'mercaderia__grano__nombre')
    
    # Total en stock
    total_stock = stocks.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    
    context = {
        'ubicacion': ubicacion,
        'almacenajes': almacenajes,
        'stocks': stocks,
        'total_stock': total_stock,
    }
    
    return render(request, 'almacenamiento/ubicacion_detail.html', context)


def almacenajes_list(request):
    """Lista de almacenajes con filtros"""
    # Obtener parámetros de filtro
    ubicacion_id = request.GET.get('ubicacion')
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    search = request.GET.get('search')
    
    # Query base
    queryset = Almacenaje.objects.select_related('ubicacion').filter(activo=True)
    
    # Aplicar filtros
    if ubicacion_id:
        queryset = queryset.filter(ubicacion_id=ubicacion_id)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if estado:
        queryset = queryset.filter(estado=estado)
    if search:
        queryset = queryset.filter(
            Q(codigo__icontains=search) |
            Q(ubicacion__nombre__icontains=search) |
            Q(observaciones__icontains=search)
        )
    
    # Ordenar
    queryset = queryset.order_by('ubicacion__nombre', 'codigo')
    
    # Agregar información de stock
    for almacenaje in queryset:
        almacenaje.stock_actual = Stock.objects.filter(almacenaje=almacenaje).aggregate(
            total=Sum('cantidad_kg')
        )['total'] or 0
    
    # Paginación
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    tipos = TipoAlmacenaje.choices
    estados = EstadoAlmacenaje.choices
    
    context = {
        'page_obj': page_obj,
        'ubicaciones': ubicaciones,
        'tipos': tipos,
        'estados': estados,
        'current_filters': {
            'ubicacion': ubicacion_id,
            'tipo': tipo,
            'estado': estado,
            'search': search,
        }
    }
    
    return render(request, 'almacenamiento/almacenajes_list.html', context)


def almacenaje_detail(request, pk):
    """Detalle de un almacenaje específico"""
    almacenaje = get_object_or_404(Almacenaje, pk=pk)
    
    # Stocks en este almacenaje
    stocks = Stock.objects.filter(almacenaje=almacenaje).select_related(
        'mercaderia', 'mercaderia__grano'
    ).order_by('mercaderia__grano__nombre')
    
    # Total en stock
    total_stock = stocks.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    
    # Capacidad utilizada (si tiene capacidad definida)
    porcentaje_ocupacion = None
    if almacenaje.capacidad_kg and total_stock > 0:
        porcentaje_ocupacion = (total_stock / almacenaje.capacidad_kg) * 100
    
    context = {
        'almacenaje': almacenaje,
        'stocks': stocks,
        'total_stock': total_stock,
        'porcentaje_ocupacion': porcentaje_ocupacion,
    }
    
    return render(request, 'almacenamiento/almacenaje_detail.html', context)


def stocks_list(request):
    """Lista de stocks con filtros avanzados"""
    # Obtener parámetros de filtro
    ubicacion_id = request.GET.get('ubicacion')
    tipo_almacenaje = request.GET.get('tipo_almacenaje')
    search = request.GET.get('search')
    
    # Query base
    queryset = Stock.objects.select_related(
        'ubicacion', 'almacenaje', 'mercaderia', 'mercaderia__grano'
    ).filter(cantidad_kg__gt=0)
    
    # Aplicar filtros
    if ubicacion_id:
        queryset = queryset.filter(ubicacion_id=ubicacion_id)
    if tipo_almacenaje:
        queryset = queryset.filter(almacenaje__tipo=tipo_almacenaje)
    if search:
        queryset = queryset.filter(
            Q(ubicacion__nombre__icontains=search) |
            Q(almacenaje__codigo__icontains=search) |
            Q(mercaderia__grano__nombre__icontains=search)
        )
    
    # Ordenar
    queryset = queryset.order_by('ubicacion__nombre', 'almacenaje__codigo')
    
    # Paginación
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    tipos_almacenaje = TipoAlmacenaje.choices
    
    # Totales
    total_stock = queryset.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'ubicaciones': ubicaciones,
        'tipos_almacenaje': tipos_almacenaje,
        'total_stock': total_stock,
        'current_filters': {
            'ubicacion': ubicacion_id,
            'tipo_almacenaje': tipo_almacenaje,
            'search': search,
        }
    }
    
    return render(request, 'almacenamiento/stocks_list.html', context)


def dashboard_data(request):
    """Datos para gráficos del dashboard (AJAX)"""
    # Stock por ubicación (para gráfico de barras)
    stock_ubicaciones = list(Stock.objects.select_related('ubicacion').values(
        'ubicacion__nombre'
    ).annotate(
        total=Sum('cantidad_kg')
    ).order_by('-total')[:10])
    
    # Estadísticas por tipo de almacenaje
    stock_tipos = list(Stock.objects.select_related('almacenaje').values(
        'almacenaje__tipo'
    ).annotate(
        total=Sum('cantidad_kg'),
        count=Count('almacenaje', distinct=True)
    ).order_by('-total'))
    
    # Ocupación por ubicación
    ocupacion_ubicaciones = list(Stock.objects.select_related('ubicacion').values(
        'ubicacion__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg'),
        count_almacenajes=Count('almacenaje', distinct=True)
    ).order_by('-total_kg')[:10])
    
    return JsonResponse({
        'stock_ubicaciones': stock_ubicaciones,
        'stock_tipos': stock_tipos,
        'ocupacion_ubicaciones': ocupacion_ubicaciones,
    })


# ==========================================
# VISTAS CRUD PARA UBICACIONES
# ==========================================

def crear_ubicacion(request):
    """Vista para crear una nueva ubicación"""
    from django.contrib import messages
    from django.http import JsonResponse
    from .forms import UbicacionForm
    
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            ubicacion = form.save()
            messages.success(request, f'Ubicación "{ubicacion.nombre}" creada exitosamente.')
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Ubicación "{ubicacion.nombre}" creada exitosamente.',
                    'ubicacion_id': ubicacion.id,
                    'ubicacion_nombre': ubicacion.nombre
                })
            
            return redirect('almacenamiento:ubicaciones_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = UbicacionForm()
    
    context = {
        'form': form,
        'title': 'Crear Nueva Ubicación',
        'submit_text': 'Crear Ubicación'
    }
    
    return render(request, 'almacenamiento/crear_ubicacion.html', context)


def editar_ubicacion(request, pk):
    """Vista para editar una ubicación existente"""
    from django.contrib import messages
    from django.http import JsonResponse
    from .forms import UbicacionForm
    
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            ubicacion = form.save()
            messages.success(request, f'Ubicación "{ubicacion.nombre}" actualizada exitosamente.')
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Ubicación "{ubicacion.nombre}" actualizada exitosamente.'
                })
            
            return redirect('almacenamiento:ubicaciones_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = UbicacionForm(instance=ubicacion)
    
    context = {
        'form': form,
        'ubicacion': ubicacion,
        'title': f'Editar Ubicación: {ubicacion.nombre}',
        'submit_text': 'Actualizar Ubicación'
    }
    
    return render(request, 'almacenamiento/crear_ubicacion.html', context)


def eliminar_ubicacion(request, pk):
    """Vista para eliminar una ubicación"""
    from django.contrib import messages
    from django.http import JsonResponse
    
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    
    if request.method == 'POST':
        # Verificar si la ubicación tiene almacenajes o stocks asociados
        if ubicacion.almacenajes.exists() or ubicacion.stocks.exists():
            messages.error(request, f'No se puede eliminar la ubicación "{ubicacion.nombre}" porque tiene almacenajes o stocks asociados.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'No se puede eliminar la ubicación "{ubicacion.nombre}" porque tiene almacenajes o stocks asociados.'
                })
        else:
            nombre_ubicacion = ubicacion.nombre
            ubicacion.delete()
            messages.success(request, f'Ubicación "{nombre_ubicacion}" eliminada exitosamente.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Ubicación "{nombre_ubicacion}" eliminada exitosamente.'
                })
        
        return redirect('almacenamiento:ubicaciones_list')
    
    # Calcular datos para mostrar en el modal de confirmación
    total_almacenajes = ubicacion.almacenajes.count()
    total_stocks = ubicacion.stocks.count()
    
    context = {
        'ubicacion': ubicacion,
        'total_almacenajes': total_almacenajes,
        'total_stocks': total_stocks,
    }
    
    return render(request, 'almacenamiento/eliminar_ubicacion.html', context)


def toggle_ubicacion_activo(request, pk):
    """Vista AJAX para activar/desactivar una ubicación"""
    from django.contrib import messages
    from django.http import JsonResponse
    
    if request.method == 'POST':
        ubicacion = get_object_or_404(Ubicacion, pk=pk)
        ubicacion.activo = not ubicacion.activo
        ubicacion.save()
        
        estado_texto = "activada" if ubicacion.activo else "desactivada"
        messages.success(request, f'Ubicación "{ubicacion.nombre}" {estado_texto} exitosamente.')
        
        return JsonResponse({
            'success': True,
            'activo': ubicacion.activo,
            'message': f'Ubicación "{ubicacion.nombre}" {estado_texto} exitosamente.'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


# ==========================================
# VISTAS CRUD PARA ALMACENAJES
# ==========================================

def crear_almacenaje(request):
    """Vista para crear un nuevo almacenaje"""
    from django.contrib import messages
    
    if request.method == 'POST':
        form = AlmacenajeForm(request.POST)
        if form.is_valid():
            almacenaje = form.save()
            messages.success(request, f'Almacenaje "{almacenaje.codigo}" creado exitosamente.')
            return redirect('almacenamiento:almacenajes_list')
    else:
        form = AlmacenajeForm()
        # Si viene con parámetro de ubicación, preseleccionarla
        ubicacion_id = request.GET.get('ubicacion')
        if ubicacion_id:
            try:
                ubicacion = Ubicacion.objects.get(pk=ubicacion_id, activo=True)
                form.fields['ubicacion'].initial = ubicacion
            except Ubicacion.DoesNotExist:
                pass
    
    context = {
        'form': form,
        'titulo': 'Crear Almacenaje',
        'subtitulo': 'Complete la información del nuevo almacenaje',
        'boton_texto': 'Crear Almacenaje',
        'cancelar_url': 'almacenamiento:almacenajes_list'
    }
    
    return render(request, 'almacenamiento/almacenaje_form_with_nav.html', context)


def editar_almacenaje(request, pk):
    """Vista para editar un almacenaje existente"""
    from django.contrib import messages
    from .forms import AlmacenajeForm
    
    almacenaje = get_object_or_404(Almacenaje, pk=pk)
    
    if request.method == 'POST':
        form = AlmacenajeForm(request.POST, instance=almacenaje)
        if form.is_valid():
            almacenaje_actualizado = form.save()
            messages.success(request, f'Almacenaje "{almacenaje_actualizado.codigo}" actualizado exitosamente.')
            return redirect('almacenamiento:almacenajes_list')
    else:
        form = AlmacenajeForm(instance=almacenaje)
    
    context = {
        'form': form,
        'almacenaje': almacenaje,
        'titulo': f'Editar Almacenaje: {almacenaje.codigo}',
        'subtitulo': f'Ubicación: {almacenaje.ubicacion.nombre}',
        'boton_texto': 'Actualizar Almacenaje',
        'cancelar_url': 'almacenamiento:almacenajes_list'
    }
    
    return render(request, 'almacenamiento/almacenaje_form_with_nav.html', context)


def eliminar_almacenaje(request, pk):
    """Vista para eliminar un almacenaje"""
    from django.contrib import messages
    
    almacenaje = get_object_or_404(Almacenaje, pk=pk)
    
    if request.method == 'POST':
        # Verificar si se puede eliminar
        tiene_stocks = Stock.objects.filter(almacenaje=almacenaje, cantidad_kg__gt=0).exists()
        
        if tiene_stocks:
            messages.error(request, f'No se puede eliminar el almacenaje "{almacenaje.codigo}" porque tiene stock activo.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'No se puede eliminar el almacenaje "{almacenaje.codigo}" porque tiene stock activo.'
                })
        else:
            codigo_almacenaje = almacenaje.codigo
            almacenaje.delete()
            messages.success(request, f'Almacenaje "{codigo_almacenaje}" eliminado exitosamente.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Almacenaje "{codigo_almacenaje}" eliminado exitosamente.'
                })
        
        return redirect('almacenamiento:almacenajes_list')
    
    # Calcular datos para mostrar en el modal de confirmación
    stocks_activos = Stock.objects.filter(almacenaje=almacenaje, cantidad_kg__gt=0)
    total_stock = stocks_activos.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    total_registros_stock = Stock.objects.filter(almacenaje=almacenaje).count()
    
    context = {
        'almacenaje': almacenaje,
        'stocks_activos': stocks_activos,
        'total_stock': total_stock,
        'total_registros_stock': total_registros_stock,
        'puede_eliminar': total_stock == 0,
    }
    
    return render(request, 'almacenamiento/eliminar_almacenaje.html', context)


def toggle_almacenaje_activo(request, pk):
    """Vista AJAX para activar/desactivar un almacenaje"""
    from django.contrib import messages
    
    if request.method == 'POST':
        almacenaje = get_object_or_404(Almacenaje, pk=pk)
        
        # Si se va a desactivar, verificar que no tenga stock
        if almacenaje.activo:
            tiene_stock = Stock.objects.filter(almacenaje=almacenaje, cantidad_kg__gt=0).exists()
            if tiene_stock:
                return JsonResponse({
                    'success': False,
                    'message': f'No se puede desactivar el almacenaje "{almacenaje.codigo}" porque tiene stock activo.'
                })
        
        almacenaje.activo = not almacenaje.activo
        almacenaje.save()
        
        estado_texto = "activado" if almacenaje.activo else "desactivado"
        messages.success(request, f'Almacenaje "{almacenaje.codigo}" {estado_texto} exitosamente.')
        
        return JsonResponse({
            'success': True,
            'activo': almacenaje.activo,
            'message': f'Almacenaje "{almacenaje.codigo}" {estado_texto} exitosamente.'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})
