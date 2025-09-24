from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.forms import ModelForm, inlineformset_factory
from django import forms
from django.utils import timezone
from decimal import Decimal
from mercaderias.models import (
    ClasificacionCalidad, DetalleCalidad, TicketAjuste,
    TipoClasificacion, EstadoClasificacion, TipoAjuste, Calidad
)
from almacenamiento.models import Stock, Ubicacion, Almacenaje

# ==========================================
# VISTAS WEB PARA CLASIFICACIÓN DE CALIDADES
# ==========================================

def seleccionar_stock(request):
    """
    Vista para seleccionar qué stock clasificar
    """
    # Obtener parámetros de filtro
    ubicacion_id = request.GET.get('ubicacion')
    grano_search = request.GET.get('grano', '').strip()
    
    # Consulta base: stock disponible (cantidad > 0)
    stocks = Stock.objects.filter(cantidad_kg__gt=0)
    
    # Filtros
    if ubicacion_id:
        stocks = stocks.filter(almacenaje__ubicacion_id=ubicacion_id)
    
    if grano_search:
        stocks = stocks.filter(
            Q(mercaderia__grano__nombre__icontains=grano_search) |
            Q(mercaderia__grano__codigo__icontains=grano_search)
        )
    
    # Optimizar consulta
    stocks = stocks.select_related(
        'mercaderia__grano',
        'almacenaje__ubicacion'
    ).order_by('-fecha_actualizacion')
    
    # Paginación
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Ubicaciones para el filtro
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'page_obj': page_obj,
        'ubicaciones': ubicaciones,
        'ubicacion_id': ubicacion_id,
        'grano_search': grano_search,
    }
    
    return render(request, 'mercaderias/clasificacion/seleccionar_stock.html', context)


def panel_clasificacion(request):
    """
    Panel principal/dashboard de clasificación
    """
    # Estadísticas generales
    stats = {
        'total_clasificaciones': ClasificacionCalidad.objects.count(),
        'pendientes_verificacion': ClasificacionCalidad.objects.filter(
            estado=EstadoClasificacion.REGISTRADO
        ).count(),
        'tickets_pendientes': TicketAjuste.objects.filter(aplicado=False).count(),
        'clasificaciones_mes': ClasificacionCalidad.objects.filter(
            fecha_registro__month=timezone.now().month,
            fecha_registro__year=timezone.now().year
        ).count(),
    }
    
    # Clasificaciones recientes
    clasificaciones_recientes = ClasificacionCalidad.objects.select_related(
        'stock_origen__mercaderia__grano'
    ).order_by('-fecha_creacion')[:10]
    
    # Clasificaciones pendientes de verificación
    pendientes = ClasificacionCalidad.objects.filter(
        estado=EstadoClasificacion.REGISTRADO
    ).select_related('stock_origen__mercaderia__grano')[:5]
    
    # Tickets pendientes
    tickets_pendientes = TicketAjuste.objects.filter(
        aplicado=False
    ).select_related('stock_afectado__mercaderia__grano')[:5]
    
    context = {
        'stats': stats,
        'clasificaciones_recientes': clasificaciones_recientes,
        'pendientes': pendientes,
        'tickets_pendientes': tickets_pendientes,
    }
    
    return render(request, 'mercaderias/clasificacion/panel.html', context)


def lista_clasificaciones(request):
    """
    Lista paginada de clasificaciones con filtros
    """
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    tipo_filtro = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Query base
    clasificaciones = ClasificacionCalidad.objects.select_related(
        'stock_origen__mercaderia__grano'
    )
    
    # Aplicar filtros
    if estado_filtro:
        clasificaciones = clasificaciones.filter(estado=estado_filtro)
    
    if tipo_filtro:
        clasificaciones = clasificaciones.filter(tipo_clasificacion=tipo_filtro)
    
    if fecha_desde:
        clasificaciones = clasificaciones.filter(fecha_registro__gte=fecha_desde)
    
    if fecha_hasta:
        clasificaciones = clasificaciones.filter(fecha_registro__lte=fecha_hasta)
    
    # Ordenar
    clasificaciones = clasificaciones.order_by('-fecha_registro', '-fecha_creacion')
    
    # Paginación
    paginator = Paginator(clasificaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estados': EstadoClasificacion.choices,
        'tipos': TipoClasificacion.choices,
    }
    
    return render(request, 'mercaderias/clasificacion/lista_clasificaciones.html', context)


def detalle_clasificacion(request, id):
    """
    Vista de detalle de una clasificación específica
    """
    clasificacion = get_object_or_404(
        ClasificacionCalidad.objects.select_related(
            'stock_origen__mercaderia__grano',
            'stock_origen__mercaderia'
        ),
        id=id
    )
    
    # Detalles con calidades
    detalles = clasificacion.detalles.select_related('calidad', 'ubicacion_especifica').all()
    
    # Tickets generados (si los hay)
    tickets = clasificacion.ajustes_generados.all()
    
    context = {
        'clasificacion': clasificacion,
        'detalles': detalles,
        'tickets': tickets,
    }
    
    return render(request, 'mercaderias/clasificacion/detalle_clasificacion.html', context)


# ==========================================
# FORMULARIOS
# ==========================================

class ClasificacionForm(ModelForm):
    """Formulario para crear/editar clasificación"""
    
    class Meta:
        model = ClasificacionCalidad
        fields = [
            'fecha_registro', 'tipo_clasificacion', 'estado',
            'registrado_por', 'responsable', 'observaciones'
        ]
        widgets = {
            'fecha_registro': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_clasificacion': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'registrado_por': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DetalleCalidadForm(ModelForm):
    """Formulario para detalles de calidad"""
    
    class Meta:
        model = DetalleCalidad
        fields = [
            'calidad', 'cantidad_kg', 'porcentaje', 
            'ubicacion_especifica', 'almacenaje_especifico', 'observaciones'
        ]
        widgets = {
            'calidad': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'ubicacion_especifica': forms.Select(attrs={'class': 'form-select'}),
            'almacenaje_especifico': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# Formset para manejar múltiples detalles
DetalleFormSet = inlineformset_factory(
    ClasificacionCalidad,
    DetalleCalidad,
    form=DetalleCalidadForm,
    extra=3,
    can_delete=True
)


def crear_clasificacion(request, stock_id):
    """
    Crear nueva clasificación para un stock específico
    """
    stock = get_object_or_404(Stock, id=stock_id)
    
    if request.method == 'POST':
        form = ClasificacionForm(request.POST)
        formset = DetalleFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Crear clasificación
            clasificacion = form.save(commit=False)
            clasificacion.stock_origen = stock
            clasificacion.cantidad_stock_original = stock.cantidad_actual
            clasificacion.save()
            
            # Guardar detalles
            formset.instance = clasificacion
            detalles = formset.save()
            
            # Calcular total registrado
            total_registrado = sum(d.cantidad_kg for d in detalles if d.id)
            clasificacion.cantidad_total_registrada = total_registrado
            clasificacion.save()
            
            # Generar ticket de ajuste si hay diferencia
            if clasificacion.tiene_diferencia:
                crear_ticket_ajuste(clasificacion)
            
            messages.success(request, f'Clasificación {clasificacion.codigo} creada correctamente.')
            return redirect('mercaderias:detalle_clasificacion', id=clasificacion.id)
    else:
        # Formulario inicial
        registrado_por = 'Sistema'
        if request.user.is_authenticated:
            registrado_por = request.user.get_full_name() or request.user.username
        
        form = ClasificacionForm(initial={
            'fecha_registro': timezone.now().date(),
            'registrado_por': registrado_por,
        })
        formset = DetalleFormSet()
    
    # Datos para el formulario
    calidades = Calidad.objects.filter(activo=True).order_by('orden_presentacion')
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    almacenajes = Almacenaje.objects.filter(ubicacion__activo=True).select_related('ubicacion')
    
    context = {
        'form': form,
        'formset': formset,
        'stock': stock,
        'calidades': calidades,
        'ubicaciones': ubicaciones,
        'almacenajes': almacenajes,
    }
    
    return render(request, 'mercaderias/clasificacion/crear_clasificacion.html', context)


def editar_clasificacion(request, id):
    """
    Editar clasificación existente
    """
    clasificacion = get_object_or_404(ClasificacionCalidad, id=id)
    
    # Solo se puede editar si está en borrador
    if clasificacion.estado != EstadoClasificacion.BORRADOR:
        messages.error(request, 'Solo se pueden editar clasificaciones en estado BORRADOR.')
        return redirect('mercaderias:detalle_clasificacion', id=id)
    
    if request.method == 'POST':
        form = ClasificacionForm(request.POST, instance=clasificacion)
        formset = DetalleFormSet(request.POST, instance=clasificacion)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            detalles = formset.save()
            
            # Recalcular total
            total_registrado = sum(d.cantidad_kg for d in clasificacion.detalles.all())
            clasificacion.cantidad_total_registrada = total_registrado
            clasificacion.save()
            
            messages.success(request, 'Clasificación actualizada correctamente.')
            return redirect('mercaderias:detalle_clasificacion', id=id)
    else:
        form = ClasificacionForm(instance=clasificacion)
        formset = DetalleFormSet(instance=clasificacion)
    
    # Datos para el formulario
    calidades = Calidad.objects.filter(activo=True).order_by('orden_presentacion')
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    almacenajes = Almacenaje.objects.filter(ubicacion__activo=True).select_related('ubicacion')
    
    context = {
        'form': form,
        'formset': formset,
        'clasificacion': clasificacion,
        'calidades': calidades,
        'ubicaciones': ubicaciones,
        'almacenajes': almacenajes,
    }
    
    return render(request, 'mercaderias/clasificacion/crear_clasificacion.html', context)


def crear_ticket_ajuste(clasificacion):
    """
    Crear ticket de ajuste automático por diferencias
    """
    diferencia = clasificacion.diferencia_cantidad
    
    if abs(diferencia) <= Decimal('0.01'):
        return None
    
    # Determinar tipo de ajuste
    tipo_ajuste = TipoAjuste.BAJA if diferencia > 0 else TipoAjuste.ALTA
    cantidad_ajuste = abs(diferencia)
    
    # Generar número de ticket
    from django.utils import timezone
    fecha = timezone.now()
    ultimo = TicketAjuste.objects.filter(
        numero_ticket__startswith=f"TA-{fecha.strftime('%Y%m')}"
    ).order_by('-numero_ticket').first()
    
    if ultimo:
        numero = int(ultimo.numero_ticket.split('-')[-1]) + 1
    else:
        numero = 1
    
    numero_ticket = f"TA-{fecha.strftime('%Y%m')}-{numero:04d}"
    
    # Crear ticket
    ticket = TicketAjuste.objects.create(
        numero_ticket=numero_ticket,
        tipo_ajuste=tipo_ajuste,
        fecha_ajuste=clasificacion.fecha_registro,
        stock_afectado=clasificacion.stock_origen,
        cantidad_ajuste_kg=cantidad_ajuste,
        motivo=f"Ajuste automático por diferencia en clasificación {clasificacion.codigo}. "
               f"Diferencia detectada: {diferencia}kg",
        clasificacion_origen=clasificacion,
        autorizado_por="Sistema",
        registrado_por=clasificacion.registrado_por
    )
    
    return ticket


# ==========================================
# AJAX / API VIEWS
# ==========================================

def ajax_stock_info(request, stock_id):
    """
    Obtener información de un stock vía AJAX
    """
    try:
        stock = Stock.objects.select_related(
            'mercaderia__grano',
            'mercaderia',
            'almacenaje__ubicacion'
        ).get(id=stock_id)
        
        data = {
            'grano': stock.mercaderia.grano.nombre,
            'proveedor': stock.mercaderia.propietario_nombre if stock.mercaderia.propietario_nombre else 'N/A',
            'cantidad_actual': float(stock.cantidad_kg),
            'ubicacion': stock.almacenaje.ubicacion.nombre if stock.almacenaje else 'N/A',
            'fecha_entrada': stock.fecha_actualizacion.strftime('%d/%m/%Y'),
        }
        
        return JsonResponse(data)
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock no encontrado'}, status=404)


def ajax_almacenajes_por_ubicacion(request):
    """
    Obtener almacenajes de una ubicación específica
    """
    ubicacion_id = request.GET.get('ubicacion_id')
    
    if not ubicacion_id:
        return JsonResponse({'almacenajes': []})
    
    almacenajes = Almacenaje.objects.filter(
        ubicacion_id=ubicacion_id
    ).values('id', 'codigo', 'descripcion')
    
    return JsonResponse({'almacenajes': list(almacenajes)})