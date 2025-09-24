from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    TipoGrano, CalidadGrado, Mercaderia, Ubicacion, Almacenaje, 
    Stock, TipoPresentacion, UnidadMedida, PesoUnitarioReferencia,
    FactorConversion, ReglaAlmacenajePresentacion
)

# ==========================================
# VISTAS WEB (Templates)
# ==========================================

def dashboard(request):
    """Dashboard principal de mercaderías"""
    # Estadísticas generales
    total_mercaderias = Mercaderia.objects.filter(activo=True).count()
    total_stock_kg = Stock.objects.aggregate(total=Sum('cantidad_kg'))['total'] or 0
    total_ubicaciones = Ubicacion.objects.filter(activo=True).count()
    total_almacenajes = Almacenaje.objects.filter(activo=True).count()
    
    # Stock por tipo de grano
    stock_por_grano = Stock.objects.values(
        'mercaderia__grano__nombre',
        'mercaderia__grano__codigo'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')
    
    # Stock por ubicación
    stock_por_ubicacion = Stock.objects.values(
        'ubicacion__nombre',
        'ubicacion__tipo'
    ).annotate(
        total_kg=Sum('cantidad_kg'),
        total_almacenajes=Sum('almacenaje__id', distinct=True)
    ).order_by('-total_kg')
    
    # Almacenajes por tipo
    almacenajes_por_tipo = Almacenaje.objects.values('tipo').annotate(
        count=Sum('id')
    ).order_by('tipo')
    
    context = {
        'total_mercaderias': total_mercaderias,
        'total_stock_kg': total_stock_kg,
        'total_stock_tn': total_stock_kg / 1000 if total_stock_kg else 0,
        'total_ubicaciones': total_ubicaciones,
        'total_almacenajes': total_almacenajes,
        'stock_por_grano': stock_por_grano,
        'stock_por_ubicacion': stock_por_ubicacion,
        'almacenajes_por_tipo': almacenajes_por_tipo,
    }
    
    return render(request, 'mercaderias/dashboard.html', context)


def mercaderias_list(request):
    """Lista de mercaderías con filtros"""
    mercaderias = Mercaderia.objects.filter(activo=True).select_related(
        'grano', 'calidad_grado'
    ).prefetch_related('stocks')
    
    # Filtros
    grano_id = request.GET.get('grano')
    calidad_id = request.GET.get('calidad')
    search = request.GET.get('search')
    
    if grano_id:
        mercaderias = mercaderias.filter(grano_id=grano_id)
    if calidad_id:
        mercaderias = mercaderias.filter(calidad_grado_id=calidad_id)
    if search:
        mercaderias = mercaderias.filter(
            Q(grano__nombre__icontains=search) |
            Q(calidad_grado__descripcion__icontains=search) |
            Q(observaciones__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(mercaderias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para los filtros del template
    tipos_grano = TipoGrano.objects.filter(activo=True).order_by('nombre')
    calidades = CalidadGrado.objects.filter(activo=True).order_by('descripcion')
    
    context = {
        'page_obj': page_obj,
        'tipos_grano': tipos_grano,
        'calidades': calidades,
        'grano_id': int(grano_id) if grano_id else None,
        'calidad_id': int(calidad_id) if calidad_id else None,
        'search': search or '',
    }
    
    return render(request, 'mercaderias/mercaderias_list.html', context)


def mercaderia_detail(request, pk):
    """Detalle de una mercadería"""
    mercaderia = get_object_or_404(Mercaderia, pk=pk)
    stocks = mercaderia.stocks.select_related(
        'ubicacion', 'almacenaje'
    ).order_by('ubicacion__nombre', 'almacenaje__codigo')
    
    context = {
        'mercaderia': mercaderia,
        'stocks': stocks,
    }
    
    return render(request, 'mercaderias/mercaderia_detail.html', context)


def ubicaciones_list(request):
    """Lista de ubicaciones"""
    ubicaciones = Ubicacion.objects.filter(activo=True).prefetch_related(
        'almacenajes', 'stocks'
    ).annotate(
        total_stock=Sum('stocks__cantidad_kg'),
        total_almacenajes=Sum('almacenajes__id', distinct=True)
    ).order_by('nombre')
    
    # Filtro por tipo
    tipo = request.GET.get('tipo')
    if tipo:
        ubicaciones = ubicaciones.filter(tipo=tipo)
    
    context = {
        'ubicaciones': ubicaciones,
        'tipo_selected': tipo,
        'tipos_ubicacion': Ubicacion.TipoUbicacion.choices,
    }
    
    return render(request, 'mercaderias/ubicaciones_list.html', context)


def ubicacion_detail(request, pk):
    """Detalle de una ubicación"""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    almacenajes = ubicacion.almacenajes.filter(activo=True).prefetch_related(
        'stocks__mercaderia__grano', 'stocks__mercaderia__calidad_grado'
    ).annotate(
        total_stock=Sum('stocks__cantidad_kg')
    ).order_by('codigo')
    
    # Stock total por grano en esta ubicación
    stock_por_grano = Stock.objects.filter(
        ubicacion=ubicacion
    ).values(
        'mercaderia__grano__nombre'
    ).annotate(
        total_kg=Sum('cantidad_kg')
    ).order_by('-total_kg')
    
    context = {
        'ubicacion': ubicacion,
        'almacenajes': almacenajes,
        'stock_por_grano': stock_por_grano,
    }
    
    return render(request, 'mercaderias/ubicacion_detail.html', context)


def stocks_list(request):
    """Lista de stocks con filtros avanzados"""
    stocks = Stock.objects.select_related(
        'ubicacion', 'almacenaje', 'mercaderia__grano', 'mercaderia__calidad_grado'
    ).filter(cantidad_kg__gt=0).order_by(
        'ubicacion__nombre', 'almacenaje__codigo'
    )
    
    # Filtros
    ubicacion_id = request.GET.get('ubicacion')
    grano_id = request.GET.get('grano')
    tipo_almacenaje = request.GET.get('tipo_almacenaje')
    
    if ubicacion_id:
        stocks = stocks.filter(ubicacion_id=ubicacion_id)
    if grano_id:
        stocks = stocks.filter(mercaderia__grano_id=grano_id)
    if tipo_almacenaje:
        stocks = stocks.filter(almacenaje__tipo=tipo_almacenaje)
    
    # Paginación
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para filtros del template
    ubicaciones = Ubicacion.objects.filter(activo=True).order_by('nombre')
    tipos_grano = TipoGrano.objects.filter(activo=True).order_by('nombre')
    tipos_almacenaje = Almacenaje.TipoAlmacenaje.choices
    
    context = {
        'page_obj': page_obj,
        'ubicaciones': ubicaciones,
        'tipos_grano': tipos_grano,
        'tipos_almacenaje': tipos_almacenaje,
        'ubicacion_id': int(ubicacion_id) if ubicacion_id else None,
        'grano_id': int(grano_id) if grano_id else None,
        'tipo_almacenaje': tipo_almacenaje,
    }
    
    return render(request, 'mercaderias/stocks_list.html', context)


# ==========================================
# AJAX APIs
# ==========================================

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


def api_almacenajes_por_ubicacion(request, ubicacion_id):
    """API para obtener almacenajes de una ubicación"""
    almacenajes = Almacenaje.objects.filter(
        ubicacion_id=ubicacion_id, activo=True
    ).values('id', 'codigo', 'tipo').order_by('codigo')
    
    return JsonResponse({
        'almacenajes': list(almacenajes)
    })
