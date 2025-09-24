from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Grano, Mercaderia, TipoMercaderia, EstadoMercaderia,
    ClasificacionCalidad, EstadoClasificacion, TicketAjuste
)
from .serializers import GranoSerializer, MercaderiaSerializer
from almacenamiento.models import (
    Ubicacion, Almacenaje, Stock, TipoPresentacion, UnidadMedida, 
    PesoUnitarioReferencia, FactorConversion, ReglaAlmacenajePresentacion,
    TipoAlmacenaje, EstadoAlmacenaje
)

# ==========================================
# VISTAS WEB (Templates)
# ==========================================

def dashboard(request):
    """Dashboard principal de mercaderías"""
    # Estadísticas generales
    total_mercaderias = Mercaderia.objects.filter(estado='ACTIVO').count()
    total_granos = Grano.objects.filter(activo=True).count()
    total_ubicaciones = Ubicacion.objects.filter(activo=True).count()
    total_almacenajes = Almacenaje.objects.filter(activo=True).count()
    
    # Estadísticas de clasificación
    total_clasificaciones = ClasificacionCalidad.objects.count()
    clasificaciones_pendientes = ClasificacionCalidad.objects.filter(
        estado=EstadoClasificacion.REGISTRADO
    ).count()
    
    # Estadísticas adicionales para el dashboard mejorado
    from datetime import datetime, timedelta
    from django.db.models import Avg
    
    # Clasificaciones del mes actual
    primer_dia_mes = datetime.now().replace(day=1)
    clasificaciones_mes = ClasificacionCalidad.objects.filter(
        fecha_registro__gte=primer_dia_mes
    ).count()
    
    # Tickets de ajuste pendientes
    tickets_ajuste_pendientes = TicketAjuste.objects.filter(
        aplicado=False
    ).count()
    
    # Stocks con clasificación pendiente
    stocks_pendientes = Stock.objects.filter(
        clasificaciones__isnull=True,
        cantidad_kg__gt=0
    ).count()
    
    # Eficiencia promedio de clasificaciones (clasificaciones completadas vs totales)
    clasificaciones_completadas = ClasificacionCalidad.objects.filter(
        estado=EstadoClasificacion.VERIFICADO
    ).count()
    total_no_registradas = ClasificacionCalidad.objects.exclude(
        estado=EstadoClasificacion.REGISTRADO
    ).count()
    eficiencia_promedio = (clasificaciones_completadas / total_no_registradas * 100) if total_no_registradas > 0 else 0
    
    # Stock total por grano
    stock_por_grano = Stock.objects.select_related('mercaderia__grano').values(
        'mercaderia__grano__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')[:10]
    
    # Stock por ubicación
    stock_por_ubicacion = Stock.objects.select_related('ubicacion').values(
        'ubicacion__id', 'ubicacion__nombre', 'ubicacion__tipo'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')[:10]
    
    # Mercaderías recientes
    mercaderias_recientes = Mercaderia.objects.select_related('grano').filter(
        estado='ACTIVO'
    ).order_by('-fecha_ingreso')[:10]
    
    # Almacenajes con mayor utilización
    almacenajes_utilizados = Stock.objects.select_related('almacenaje', 'ubicacion').values(
        'almacenaje__codigo', 'ubicacion__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')[:10]
    
    context = {
        'total_mercaderias': total_mercaderias,
        'total_granos': total_granos,
        'total_ubicaciones': total_ubicaciones,
        'total_almacenajes': total_almacenajes,
        'total_clasificaciones': total_clasificaciones,
        'clasificaciones_pendientes': clasificaciones_pendientes,
        'clasificaciones_mes': clasificaciones_mes,
        'tickets_ajuste_pendientes': tickets_ajuste_pendientes,
        'stocks_pendientes': stocks_pendientes,
        'eficiencia_promedio': round(eficiencia_promedio, 1),
        'stock_por_grano': stock_por_grano,
        'stock_por_ubicacion': stock_por_ubicacion,
        'mercaderias_recientes': mercaderias_recientes,
        'almacenajes_utilizados': almacenajes_utilizados,
    }
    
    return render(request, 'mercaderias/dashboard.html', context)


def granos_list(request):
    """Lista de granos con filtros y paginación"""
    granos = Grano.objects.filter(activo=True)
    
    # Filtros
    search = request.GET.get('search', '')
    if search:
        granos = granos.filter(
            Q(nombre__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(codigo__icontains=search)
        )
    
    # Ordenamiento
    sort_by = request.GET.get('sort', 'nombre')
    if sort_by in ['nombre', 'codigo', 'fecha_creacion']:
        if request.GET.get('order') == 'desc':
            sort_by = f'-{sort_by}'
        granos = granos.order_by(sort_by)
    else:
        granos = granos.order_by('nombre')
    
    # Agregar información de stock por grano
    for grano in granos:
        grano.total_stock = Stock.objects.filter(
            mercaderia__grano=grano
        ).aggregate(total=Sum('cantidad_kg'))['total'] or 0
        grano.total_mercaderias = Mercaderia.objects.filter(
            grano=grano, estado='ACTIVO'
        ).count()
    
    # Paginación
    paginator = Paginator(granos, 20)  # 20 granos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_filters': {
            'search': search,
            'sort': request.GET.get('sort', 'nombre'),
            'order': request.GET.get('order', 'asc'),
        }
    }
    
    return render(request, 'mercaderias/granos_list.html', context)


def grano_detail(request, pk):
    """Detalle de un grano específico"""
    grano = get_object_or_404(Grano, pk=pk)
    
    # Mercaderías de este grano
    mercaderias = Mercaderia.objects.filter(grano=grano).select_related('grano')
    
    # Stock total del grano
    total_stock = Stock.objects.filter(mercaderia__grano=grano).aggregate(
        total=Sum('cantidad_kg')
    )['total'] or 0
    
    # Stock por ubicación para este grano
    stock_por_ubicacion = Stock.objects.filter(
        mercaderia__grano=grano
    ).select_related('ubicacion').values(
        'ubicacion__id', 'ubicacion__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')
    
    context = {
        'grano': grano,
        'mercaderias': mercaderias,
        'total_stock': total_stock,
        'stock_por_ubicacion': stock_por_ubicacion,
    }
    
    return render(request, 'mercaderias/grano_detail.html', context)


def mercaderias_list(request):
    """Lista de mercaderías con filtros"""
    # Obtener parámetros de filtro
    grano_id = request.GET.get('grano')
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    search = request.GET.get('search')
    
    # Query base
    queryset = Mercaderia.objects.select_related('grano').all()
    
    # Aplicar filtros
    if grano_id:
        queryset = queryset.filter(grano_id=grano_id)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if estado:
        queryset = queryset.filter(estado=estado)
    if search:
        queryset = queryset.filter(
            Q(grano__nombre__icontains=search) |
            Q(propietario_nombre__icontains=search) |
            Q(observaciones__icontains=search)
        )
    
    # Ordenar
    queryset = queryset.order_by('-fecha_ingreso')
    
    # Paginación
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    granos = Grano.objects.filter(activo=True).order_by('nombre')
    tipos = TipoMercaderia.choices
    estados = EstadoMercaderia.choices
    
    context = {
        'page_obj': page_obj,
        'granos': granos,
        'tipos': tipos,
        'estados': estados,
        'current_filters': {
            'grano': grano_id,
            'tipo': tipo,
            'estado': estado,
            'search': search,
        }
    }
    
    return render(request, 'mercaderias/mercaderias_list.html', context)


def mercaderia_detail(request, pk):
    """Detalle de una mercadería específica"""
    mercaderia = get_object_or_404(Mercaderia, pk=pk)
    
    # Stocks relacionados con esta mercadería
    stocks = Stock.objects.filter(mercaderia=mercaderia).select_related(
        'ubicacion', 'almacenaje'
    ).order_by('ubicacion__nombre', 'almacenaje__codigo')
    
    # Total en stock
    total_stock = stocks.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    
    context = {
        'mercaderia': mercaderia,
        'stocks': stocks,
        'total_stock': total_stock,
    }
    
    return render(request, 'mercaderias/mercaderia_detail.html', context)


def stocks_list(request):
    """Lista de stocks con filtros avanzados"""
    # Obtener parámetros de filtro
    ubicacion_id = request.GET.get('ubicacion')
    grano_id = request.GET.get('grano')
    tipo_almacenaje = request.GET.get('tipo_almacenaje')
    search = request.GET.get('search')
    
    # Query base
    queryset = Stock.objects.select_related(
        'ubicacion', 'almacenaje', 'mercaderia', 'mercaderia__grano'
    ).filter(cantidad_kg__gt=0)
    
    # Aplicar filtros
    if ubicacion_id:
        queryset = queryset.filter(ubicacion_id=ubicacion_id)
    if grano_id:
        queryset = queryset.filter(mercaderia__grano_id=grano_id)
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
    granos = Grano.objects.filter(activo=True).order_by('nombre')
    tipos_almacenaje = TipoAlmacenaje.choices
    
    # Totales
    total_stock = queryset.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'ubicaciones': ubicaciones,
        'granos': granos,
        'tipos_almacenaje': tipos_almacenaje,
        'total_stock': total_stock,
        'current_filters': {
            'ubicacion': ubicacion_id,
            'grano': grano_id,
            'tipo_almacenaje': tipo_almacenaje,
            'search': search,
        }
    }
    
    return render(request, 'mercaderias/stocks_list.html', context)


# ==========================================
# VISTAS AJAX
# ==========================================

def dashboard_data(request):
    """Datos para gráficos del dashboard (AJAX)"""
    # Stock por grano (para gráfico de torta)
    stock_granos = list(Stock.objects.select_related('mercaderia__grano').values(
        'mercaderia__grano__nombre'
    ).annotate(
        total=Sum('cantidad_kg')
    ).order_by('-total')[:10])
    
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
        total=Sum('cantidad_kg')
    ).order_by('-total'))
    
    return JsonResponse({
        'stock_granos': stock_granos,
        'stock_ubicaciones': stock_ubicaciones,
        'stock_tipos': stock_tipos,
    })


# ==========================================
# API REST (ViewSets)
# ==========================================

class GranoViewSet(viewsets.ModelViewSet):
    """ViewSet para Granos"""
    queryset = Grano.objects.all()
    serializer_class = GranoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo']
    ordering_fields = ['nombre', 'codigo']
    ordering = ['nombre']


class MercaderiaViewSet(viewsets.ModelViewSet):
    """ViewSet para Mercaderías"""
    queryset = Mercaderia.objects.select_related('grano').all()
    serializer_class = MercaderiaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['grano__nombre', 'propietario_nombre']
    ordering_fields = ['fecha_ingreso', 'grano__nombre']
    ordering = ['-fecha_ingreso']
    
    @action(detail=True, methods=['get'])
    def stocks(self, request, pk=None):
        """Obtener stocks de una mercadería específica"""
        mercaderia = self.get_object()
        stocks = Stock.objects.filter(mercaderia=mercaderia).select_related(
            'ubicacion', 'almacenaje'
        )
        
        data = []
        for stock in stocks:
            data.append({
                'id': stock.id,
                'ubicacion': stock.ubicacion.nombre,
                'almacenaje': stock.almacenaje.codigo,
                'cantidad_kg': float(stock.cantidad_kg),
                'fecha_actualizacion': stock.fecha_actualizacion.isoformat(),
            })
        
        return Response(data)


def api_stock_por_grano(request):
    """API para gráfico de stock por grano"""
    data = Stock.objects.values(
        'mercaderia__grano__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')
    
    return JsonResponse({
        'labels': [item['mercaderia__grano__nombre'] for item in data],
        'data': [float(item['total_kg']) for item in data]
    })


def api_stock_por_ubicacion(request):
    """API para gráfico de stock por ubicación"""
    data = Stock.objects.values(
        'ubicacion__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')
    
    return JsonResponse({
        'labels': [item['ubicacion__nombre'] for item in data],
        'data': [float(item['total_kg']) for item in data]
    })


# ==========================================
# FORMULARIOS
# ==========================================

class GranoForm(ModelForm):
    class Meta:
        model = Grano
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Soja, Maíz, Trigo...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del grano...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre del Grano',
            'descripcion': 'Descripción',
            'activo': 'Activo'
        }


class MercaderiaForm(ModelForm):
    class Meta:
        model = Mercaderia
        fields = ['grano', 'tipo', 'propietario_nombre', 'propietario_contacto', 'observaciones', 'estado']
        widgets = {
            'grano': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'propietario_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del propietario...'
            }),
            'propietario_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono, email, etc...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'grano': 'Tipo de Grano',
            'tipo': 'Tipo de Mercadería',
            'propietario_nombre': 'Nombre del Propietario',
            'propietario_contacto': 'Contacto del Propietario',
            'observaciones': 'Observaciones',
            'estado': 'Estado'
        }


# ==========================================
# VISTAS CRUD - GRANOS
# ==========================================

def grano_create(request):
    """Crear nuevo grano"""
    if request.method == 'POST':
        form = GranoForm(request.POST)
        if form.is_valid():
            grano = form.save()
            messages.success(request, f'Grano "{grano.nombre}" creado exitosamente.')
            return redirect('mercaderias:grano_detail', pk=grano.pk)
    else:
        form = GranoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Grano',
        'boton_texto': 'Crear Grano'
    }
    return render(request, 'mercaderias/grano_form.html', context)


def grano_edit(request, pk):
    """Editar grano existente"""
    grano = get_object_or_404(Grano, pk=pk)
    
    if request.method == 'POST':
        form = GranoForm(request.POST, instance=grano)
        if form.is_valid():
            grano = form.save()
            messages.success(request, f'Grano "{grano.nombre}" actualizado exitosamente.')
            return redirect('mercaderias:grano_detail', pk=grano.pk)
    else:
        form = GranoForm(instance=grano)
    
    context = {
        'form': form,
        'grano': grano,
        'titulo': f'Editar Grano: {grano.nombre}',
        'boton_texto': 'Actualizar Grano'
    }
    return render(request, 'mercaderias/grano_form.html', context)


def grano_delete(request, pk):
    """Eliminar grano"""
    grano = get_object_or_404(Grano, pk=pk)
    
    if request.method == 'POST':
        # Verificar si tiene mercaderías asociadas
        mercaderias_count = Mercaderia.objects.filter(grano=grano).count()
        if mercaderias_count > 0:
            messages.error(request, f'No se puede eliminar el grano "{grano.nombre}" porque tiene {mercaderias_count} mercaderías asociadas.')
            return redirect('mercaderias:grano_detail', pk=grano.pk)
        
        nombre = grano.nombre
        grano.delete()
        messages.success(request, f'Grano "{nombre}" eliminado exitosamente.')
        return redirect('mercaderias:granos_list')
    
    # Contar mercaderías asociadas para mostrar advertencia
    mercaderias_count = Mercaderia.objects.filter(grano=grano).count()
    
    context = {
        'grano': grano,
        'mercaderias_count': mercaderias_count
    }
    return render(request, 'mercaderias/grano_delete.html', context)


# ==========================================
# VISTAS CRUD - MERCADERÍAS
# ==========================================

def mercaderia_create(request):
    """Crear nueva mercadería"""
    if request.method == 'POST':
        form = MercaderiaForm(request.POST)
        if form.is_valid():
            mercaderia = form.save()
            messages.success(request, f'Mercadería "{mercaderia}" creada exitosamente.')
            return redirect('mercaderias:mercaderia_detail', pk=mercaderia.pk)
    else:
        form = MercaderiaForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nueva Mercadería',
        'boton_texto': 'Crear Mercadería'
    }
    return render(request, 'mercaderias/mercaderia_form.html', context)


def mercaderia_edit(request, pk):
    """Editar mercadería existente"""
    mercaderia = get_object_or_404(Mercaderia, pk=pk)
    
    if request.method == 'POST':
        form = MercaderiaForm(request.POST, instance=mercaderia)
        if form.is_valid():
            mercaderia = form.save()
            messages.success(request, f'Mercadería "{mercaderia}" actualizada exitosamente.')
            return redirect('mercaderias:mercaderia_detail', pk=mercaderia.pk)
    else:
        form = MercaderiaForm(instance=mercaderia)
    
    context = {
        'form': form,
        'mercaderia': mercaderia,
        'titulo': f'Editar Mercadería: {mercaderia.descripcion}',
        'boton_texto': 'Actualizar Mercadería'
    }
    return render(request, 'mercaderias/mercaderia_form.html', context)


def mercaderia_delete(request, pk):
    """Eliminar mercadería"""
    mercaderia = get_object_or_404(Mercaderia, pk=pk)
    
    if request.method == 'POST':
        # Verificar si tiene stocks asociados
        stocks_count = Stock.objects.filter(mercaderia=mercaderia).count()
        if stocks_count > 0:
            messages.error(request, f'No se puede eliminar la mercadería "{mercaderia}" porque tiene {stocks_count} registros de stock asociados.')
            return redirect('mercaderias:mercaderia_detail', pk=mercaderia.pk)
        
        descripcion = str(mercaderia)
        mercaderia.delete()
        messages.success(request, f'Mercadería "{descripcion}" eliminada exitosamente.')
        return redirect('mercaderias:mercaderias_list')
    
    # Contar stocks asociados para mostrar advertencia
    stocks_count = Stock.objects.filter(mercaderia=mercaderia).count()
    
    context = {
        'mercaderia': mercaderia,
        'stocks_count': stocks_count
    }
    return render(request, 'mercaderias/mercaderia_delete.html', context)


# ==========================================
# VISTAS AVANZADAS - STOCKS
# ==========================================

def stocks_filter(request):
    """Vista de filtros avanzados para stocks"""
    # Obtener parámetros de filtro
    planta_galpon = request.GET.get('planta_galpon')
    tipo_almacenamiento = request.GET.get('tipo_almacenamiento')
    ubicacion_id = request.GET.get('ubicacion')
    propietario = request.GET.get('propietario')
    propio_tercero = request.GET.get('propio_tercero')
    grano_id = request.GET.get('grano')
    
    # Query base
    stocks = Stock.objects.select_related(
        'mercaderia__grano', 'mercaderia__propietario_cuenta',
        'ubicacion', 'almacenaje'
    ).all()
    
    # Aplicar filtros
    if planta_galpon:
        stocks = stocks.filter(ubicacion__nombre__icontains=planta_galpon)
    
    if tipo_almacenamiento:
        stocks = stocks.filter(ubicacion__tipo=tipo_almacenamiento)
    
    if ubicacion_id:
        stocks = stocks.filter(ubicacion_id=ubicacion_id)
    
    if propietario:
        stocks = stocks.filter(mercaderia__propietario_nombre__icontains=propietario)
    
    if propio_tercero:
        stocks = stocks.filter(mercaderia__tipo=propio_tercero)
    
    if grano_id:
        stocks = stocks.filter(mercaderia__grano_id=grano_id)
    
    # Paginación
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    # Obtener propietarios únicos de las mercaderías
    propietarios = Mercaderia.objects.values_list('propietario_nombre', flat=True).distinct().exclude(propietario_nombre__isnull=True).exclude(propietario_nombre='')
    granos = Grano.objects.filter(activo=True).order_by('nombre')
    
    # Tipos de almacenamiento únicos
    tipos_almacenamiento = Ubicacion.objects.values_list('tipo', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'stocks': page_obj,
        'ubicaciones': ubicaciones,
        'propietarios': propietarios,
        'granos': granos,
        'tipos_almacenamiento': tipos_almacenamiento,
        'filtros_aplicados': {
            'planta_galpon': planta_galpon,
            'tipo_almacenamiento': tipo_almacenamiento,
            'ubicacion_id': ubicacion_id,
            'propietario': propietario,
            'propio_tercero': propio_tercero,
            'grano_id': grano_id,
        },
        'total_stocks': stocks.count(),
        'total_kg': stocks.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    }
    
    return render(request, 'mercaderias/stocks_filter.html', context)


def stock_detail(request, pk):
    """Detalle de un stock específico"""
    stock = get_object_or_404(Stock.objects.select_related(
        'mercaderia__grano', 'mercaderia__propietario_cuenta',
        'ubicacion', 'almacenaje'
    ), pk=pk)
    
    context = {
        'stock': stock
    }
    return render(request, 'mercaderias/stock_detail.html', context)