"""
Vistas para el módulo de transportes.
Gestión de camiones, choferes, viajes y tickets de balanza.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
import json

from .models import TipoCamion, Camion, Chofer, Viaje, TicketBalanza
from .forms import (
    CamionForm, ChoferForm, ViajeForm, TicketBalanzaForm,
    TipoCamionForm, BusquedaCamionForm, BusquedaChoferForm
)


@login_required
def dashboard_transportes(request):
    """Dashboard principal del módulo de transportes."""
    from django.utils import timezone
    from datetime import timedelta
    
    # Estadísticas generales
    total_camiones = Camion.objects.filter(activo=True).count()
    # Como eliminamos el campo estado, consideramos todos los camiones activos como disponibles
    camiones_disponibles = total_camiones
    
    total_choferes = Chofer.objects.filter(activo=True).count()
    choferes_disponibles = Chofer.objects.filter(estado='disponible', activo=True).count()
    
    # Viajes del mes actual
    primer_dia_mes = timezone.now().replace(day=1)
    viajes_mes = Viaje.objects.filter(
        fecha_programada__gte=primer_dia_mes
    ).count()
    
    # Tickets de balanza de hoy
    tickets_hoy = TicketBalanza.objects.filter(
        fecha_pesaje__date=timezone.now().date()
    ).count()
    
    # Alertas de documentación
    alertas = []
    
    # Camiones con VTV vencida
    camiones_vtv_vencida = Camion.objects.filter(
        fecha_vencimiento_vtv__lt=timezone.now().date(),
        activo=True
    ).count()
    if camiones_vtv_vencida > 0:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'{camiones_vtv_vencida} camión(es) con VTV vencida'
        })
    
    # Choferes con licencia vencida
    choferes_licencia_vencida = Chofer.objects.filter(
        fecha_vencimiento_licencia__lt=timezone.now().date(),
        activo=True
    ).count()
    if choferes_licencia_vencida > 0:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'{choferes_licencia_vencida} chofer(es) con licencia vencida'
        })
    
    # Viajes recientes (últimos 10)
    viajes_recientes = Viaje.objects.select_related('camion', 'chofer').order_by('-fecha_programada')[:10]
    
    # Cálculo de porcentajes para mostrar en el dashboard
    porcentaje_disponibles = (camiones_disponibles * 100 / total_camiones) if total_camiones > 0 else 0
    
    # Documentación al día (camiones con VTV y seguro vigentes)
    camiones_doc_ok = Camion.objects.filter(
        activo=True,
        fecha_vencimiento_vtv__gte=timezone.now().date(),
        fecha_vencimiento_seguro__gte=timezone.now().date()
    ).count()
    porcentaje_documentacion = (camiones_doc_ok * 100 / total_camiones) if total_camiones > 0 else 0
    
    context = {
        'total_camiones': total_camiones,
        'camiones_disponibles': camiones_disponibles,
        'total_choferes': total_choferes,
        'choferes_disponibles': choferes_disponibles,
        'viajes_mes': viajes_mes,
        'tickets_hoy': tickets_hoy,
        'alertas': alertas,
        'viajes_recientes': viajes_recientes,
        'porcentaje_disponibles': porcentaje_disponibles,
        'porcentaje_documentacion': porcentaje_documentacion,
        'current_year': timezone.now().year,
    }
    
    return render(request, 'transportes/dashboard.html', context)


# === VISTAS DE CAMIONES ===

@login_required
def lista_camiones(request):
    """Lista de camiones con filtros."""
    form = BusquedaCamionForm(request.GET or None)
    camiones = Camion.objects.filter(activo=True).select_related('cuenta_asociada')
    
    if form.is_valid():
        if form.cleaned_data['busqueda']:
            busqueda = form.cleaned_data['busqueda']
            camiones = camiones.filter(
                Q(patente__icontains=busqueda) |
                Q(acoplado_1__icontains=busqueda) |
                Q(acoplado_2__icontains=busqueda)
            )
        
        if form.cleaned_data['cuenta_asociada']:
            camiones = camiones.filter(cuenta_asociada=form.cleaned_data['cuenta_asociada'])
    
    paginator = Paginator(camiones.order_by('patente'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_camiones': camiones.count(),
    }
    
    return render(request, 'transportes/camiones/lista.html', context)


@login_required
def detalle_camion(request, pk):
    """Detalle de un camión específico."""
    camion = get_object_or_404(Camion, pk=pk)
    
    # Viajes recientes del camión
    viajes_recientes = Viaje.objects.filter(
        camion=camion
    ).order_by('-fecha_programada')[:10]
    
    # Tickets de balanza recientes
    tickets_recientes = TicketBalanza.objects.filter(
        camion=camion
    ).order_by('-fecha_pesaje')[:10]
    
    context = {
        'camion': camion,
        'viajes_recientes': viajes_recientes,
        'tickets_recientes': tickets_recientes,
    }
    
    return render(request, 'transportes/camiones/detalle.html', context)


@login_required
def crear_camion(request):
    """Crear un nuevo camión."""
    if request.method == 'POST':
        form = CamionForm(request.POST)
        if form.is_valid():
            camion = form.save(commit=False)
            camion.creado_por = request.user
            camion.save()
            messages.success(request, f'Camión {camion.patente} creado exitosamente.')
            return redirect('transportes:detalle_camion', pk=camion.pk)
    else:
        form = CamionForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Camión'
    }
    
    return render(request, 'transportes/camiones/form.html', context)


@login_required
def editar_camion(request, pk):
    """Editar un camión existente."""
    camion = get_object_or_404(Camion, pk=pk)
    
    if request.method == 'POST':
        form = CamionForm(request.POST, instance=camion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Camión {camion.patente} actualizado exitosamente.')
            return redirect('transportes:detalle_camion', pk=camion.pk)
    else:
        form = CamionForm(instance=camion)
    
    context = {
        'form': form,
        'camion': camion,
        'titulo': f'Editar Camión {camion.patente}'
    }
    
    return render(request, 'transportes/camiones/form.html', context)


# === VISTAS DE CHOFERES ===

@login_required
def lista_choferes(request):
    """Lista de choferes con filtros."""
    form = BusquedaChoferForm(request.GET or None)
    choferes = Chofer.objects.filter(activo=True).select_related('camion_asignado')
    
    if form.is_valid():
        if form.cleaned_data['busqueda']:
            busqueda = form.cleaned_data['busqueda']
            choferes = choferes.filter(
                Q(nombre__icontains=busqueda) |
                Q(apellido__icontains=busqueda) |
                Q(dni__icontains=busqueda) |
                Q(legajo__icontains=busqueda)
            )
        
        if form.cleaned_data['estado']:
            choferes = choferes.filter(estado=form.cleaned_data['estado'])
        
        if form.cleaned_data['tipo_licencia']:
            choferes = choferes.filter(tipo_licencia=form.cleaned_data['tipo_licencia'])
    
    paginator = Paginator(choferes.order_by('apellido', 'nombre'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_choferes': choferes.count(),
    }
    
    return render(request, 'transportes/choferes/lista.html', context)


@login_required
def detalle_chofer(request, pk):
    """Detalle de un chofer específico."""
    chofer = get_object_or_404(Chofer, pk=pk)
    
    # Viajes recientes del chofer
    viajes_recientes = Viaje.objects.filter(
        chofer=chofer
    ).order_by('-fecha_programada')[:10]
    
    context = {
        'chofer': chofer,
        'viajes_recientes': viajes_recientes,
    }
    
    return render(request, 'transportes/choferes/detalle.html', context)


@login_required
def crear_chofer(request):
    """Crear un nuevo chofer."""
    if request.method == 'POST':
        form = ChoferForm(request.POST)
        if form.is_valid():
            chofer = form.save(commit=False)
            chofer.creado_por = request.user
            chofer.save()
            messages.success(request, f'Chofer {chofer.nombre_completo} creado exitosamente.')
            return redirect('transportes:detalle_chofer', pk=chofer.pk)
    else:
        form = ChoferForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Chofer'
    }
    
    return render(request, 'transportes/choferes/form.html', context)


@login_required
def editar_chofer(request, pk):
    """Editar un chofer existente."""
    chofer = get_object_or_404(Chofer, pk=pk)
    
    if request.method == 'POST':
        form = ChoferForm(request.POST, instance=chofer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Chofer {chofer.nombre_completo} actualizado exitosamente.')
            return redirect('transportes:detalle_chofer', pk=chofer.pk)
    else:
        form = ChoferForm(instance=chofer)
    
    context = {
        'form': form,
        'chofer': chofer,
        'titulo': f'Editar Chofer {chofer.nombre_completo}'
    }
    
    return render(request, 'transportes/choferes/form.html', context)


# === VISTAS DE VIAJES ===

@login_required
def lista_viajes(request):
    """Lista de viajes con filtros."""
    viajes = Viaje.objects.all().select_related('camion', 'chofer', 'cliente')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        viajes = viajes.filter(estado=estado)
    
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        viajes = viajes.filter(fecha_programada__gte=fecha_desde)
    
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        viajes = viajes.filter(fecha_programada__lte=fecha_hasta)
    
    paginator = Paginator(viajes.order_by('-fecha_programada'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estados': Viaje.ESTADO_CHOICES,
        'estado_actual': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'transportes/viajes/lista.html', context)


@login_required
def detalle_viaje(request, pk):
    """Detalle de un viaje específico."""
    viaje = get_object_or_404(Viaje, pk=pk)
    
    # Tickets de balanza asociados
    tickets = TicketBalanza.objects.filter(viaje=viaje).order_by('fecha_pesaje')
    
    context = {
        'viaje': viaje,
        'tickets': tickets,
    }
    
    return render(request, 'transportes/viajes/detalle.html', context)


@login_required
def crear_viaje(request):
    """Crear un nuevo viaje."""
    if request.method == 'POST':
        form = ViajeForm(request.POST)
        if form.is_valid():
            viaje = form.save(commit=False)
            viaje.creado_por = request.user
            viaje.save()
            messages.success(request, f'Viaje {viaje.numero_viaje} creado exitosamente.')
            return redirect('transportes:detalle_viaje', pk=viaje.pk)
    else:
        form = ViajeForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Viaje'
    }
    
    return render(request, 'transportes/viajes/form.html', context)


# === VISTAS DE TICKETS DE BALANZA ===

@login_required
def lista_tickets(request):
    """Lista de tickets de balanza con filtros."""
    tickets = TicketBalanza.objects.all().select_related('camion', 'chofer', 'cliente_carga', 'viaje')
    
    # Filtros
    tipo_pesaje = request.GET.get('tipo_pesaje')
    if tipo_pesaje:
        tickets = tickets.filter(tipo_pesaje=tipo_pesaje)
    
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        tickets = tickets.filter(fecha_pesaje__gte=fecha_desde)
    
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        tickets = tickets.filter(fecha_pesaje__lte=fecha_hasta)
    
    paginator = Paginator(tickets.order_by('-fecha_pesaje'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipos_pesaje': TicketBalanza.TIPO_PESAJE_CHOICES,
        'tipo_actual': tipo_pesaje,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'transportes/tickets/lista.html', context)


@login_required
def detalle_ticket(request, pk):
    """Detalle de un ticket de balanza específico."""
    ticket = get_object_or_404(TicketBalanza, pk=pk)
    
    context = {
        'ticket': ticket,
    }
    
    return render(request, 'transportes/tickets/detalle.html', context)


@login_required
def crear_ticket(request):
    """Crear un nuevo ticket de balanza."""
    if request.method == 'POST':
        form = TicketBalanzaForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creado_por = request.user
            ticket.save()
            messages.success(request, f'Ticket {ticket.numero_ticket} creado exitosamente.')
            return redirect('transportes:detalle_ticket', pk=ticket.pk)
    else:
        form = TicketBalanzaForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Ticket de Balanza'
    }
    
    return render(request, 'transportes/tickets/form.html', context)


# === VISTAS AJAX ===

@login_required
def ajax_camiones_disponibles(request):
    """Retorna camiones disponibles para AJAX."""
    camiones = Camion.objects.filter(
        estado='disponible',
        activo=True
    ).values('id_camion', 'patente', 'marca', 'modelo')
    
    return JsonResponse({
        'camiones': list(camiones)
    })


@login_required
def ajax_choferes_disponibles(request):
    """Retorna choferes disponibles para AJAX."""
    choferes = Chofer.objects.filter(
        estado='disponible',
        activo=True
    ).values('id_chofer', 'nombre', 'apellido', 'legajo')
    
    return JsonResponse({
        'choferes': list(choferes)
    })


@login_required
@require_http_methods(["POST"])
def cambiar_estado_viaje(request, pk):
    """Cambiar el estado de un viaje vía AJAX."""
    viaje = get_object_or_404(Viaje, pk=pk)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in dict(Viaje.ESTADO_CHOICES):
        viaje.estado = nuevo_estado
        
        # Actualizar fechas según el estado
        if nuevo_estado == 'en_curso' and not viaje.fecha_inicio_real:
            viaje.fecha_inicio_real = timezone.now()
        elif nuevo_estado == 'completado' and not viaje.fecha_fin_real:
            viaje.fecha_fin_real = timezone.now()
        
        viaje.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Estado del viaje actualizado a {viaje.get_estado_display()}'
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Estado inválido'
    })
