"""
Vistas para el sistema de tickets de transporte - Flujo real del negocio.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json

from .models import Ticket, TipoMovimiento, EstadoTicket, DetalleMercaderia, AnalisisMercaderia
from .forms import TicketForm, DetalleMercaderiaFormSet


@login_required
def dashboard_tickets(request):
    """Dashboard principal de tickets."""
    
    # Estadísticas básicas
    total_tickets = Ticket.objects.count()
    
    # Tickets por estado
    tickets_por_estado = Ticket.objects.values(
        'estado__nombre', 'estado__color'
    ).annotate(cantidad=Count('id')).order_by('estado__nombre')
    
    # Tickets recientes (últimos 10)
    tickets_recientes = Ticket.objects.select_related(
        'tipo_movimiento', 'estado', 'creado_por', 'chofer', 'origen', 'destinatario'
    ).prefetch_related('detalle_mercaderias__mercaderia').order_by('-fecha_creacion')[:10]
    
    # Estadísticas del mes actual
    hoy = timezone.now().date()
    primer_dia_mes = hoy.replace(day=1)
    
    recepciones_mes = Ticket.objects.filter(
        tipo_movimiento__codigo='REC',
        fecha_creacion__date__gte=primer_dia_mes
    ).count()
    
    envios_mes = Ticket.objects.filter(
        tipo_movimiento__codigo='ENV',
        fecha_creacion__date__gte=primer_dia_mes
    ).count()
    
    # Tickets pendientes (sin pesos completos o sin análisis)
    pendientes = Ticket.objects.filter(
        Q(peso_bruto__isnull=True) | Q(peso_tara__isnull=True) |
        Q(detalle_mercaderias__analisis_realizado=False)
    ).distinct().count()
    
    # Tickets sin salir (para recepciones)
    sin_salir = Ticket.objects.filter(
        tipo_movimiento__codigo='REC',
        fecha_salida__isnull=True
    ).count()
    
    # Datos para gráficos (últimos 6 meses)
    import calendar
    meses_atras = 6
    chart_labels = []
    chart_recepciones = []
    chart_envios = []
    
    for i in range(meses_atras - 1, -1, -1):
        fecha = hoy - timedelta(days=30 * i)
        mes_inicio = fecha.replace(day=1)
        if fecha.month == 12:
            mes_fin = fecha.replace(year=fecha.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            mes_fin = fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)
        
        chart_labels.append(f"{calendar.month_name[fecha.month][:3]} {fecha.year}")
        
        recepciones = Ticket.objects.filter(
            tipo_movimiento__codigo='REC',
            fecha_creacion__date__gte=mes_inicio,
            fecha_creacion__date__lte=mes_fin
        ).count()
        
        envios = Ticket.objects.filter(
            tipo_movimiento__codigo='ENV',
            fecha_creacion__date__gte=mes_inicio,
            fecha_creacion__date__lte=mes_fin
        ).count()
        
        chart_recepciones.append(recepciones)
        chart_envios.append(envios)
    
    # Datos para gráfico de estados
    estados_labels = []
    estados_data = []
    estados_colors = []
    
    for estado in tickets_por_estado:
        estados_labels.append(estado['estado__nombre'])
        estados_data.append(estado['cantidad'])
        estados_colors.append(estado['estado__color'])
    
    stats = {
        'total_tickets': total_tickets,
        'recepciones_mes': recepciones_mes,
        'envios_mes': envios_mes,
        'pendientes': pendientes,
        'sin_salir': sin_salir,
    }
    
    context = {
        'stats': stats,
        'tickets_por_estado': tickets_por_estado,
        'tickets_recientes': tickets_recientes,
        'chart_labels': json.dumps(chart_labels),
        'chart_recepciones': json.dumps(chart_recepciones),
        'chart_envios': json.dumps(chart_envios),
        'estados_labels': json.dumps(estados_labels),
        'estados_data': json.dumps(estados_data),
        'estados_colors': json.dumps(estados_colors),
    }
    
    return render(request, 'tickets/dashboard.html', context)


@login_required
def lista_tickets(request):
    """Lista paginada de tickets con filtros."""
    
    tickets = Ticket.objects.select_related(
        'tipo_movimiento', 'estado', 'creado_por', 'chofer', 'origen', 'destinatario'
    ).prefetch_related('detalle_mercaderias__mercaderia')
    
    # Filtros
    q = request.GET.get('q')
    if q:
        tickets = tickets.filter(
            Q(numero_ticket__icontains=q) |
            Q(patente_camion__icontains=q) |
            Q(chofer__nombre__icontains=q) |
            Q(origen__razon_social__icontains=q) |
            Q(destinatario__razon_social__icontains=q) |
            Q(detalle_mercaderias__mercaderia__nombre__icontains=q)
        ).distinct()
    
    tipo = request.GET.get('tipo')
    if tipo:
        tickets = tickets.filter(tipo_movimiento__codigo=tipo)
    
    estado = request.GET.get('estado')
    if estado:
        tickets = tickets.filter(estado__codigo=estado)
    
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        tickets = tickets.filter(fecha_creacion__date__gte=fecha_desde)
    
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        tickets = tickets.filter(fecha_creacion__date__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(tickets.order_by('-fecha_creacion'), 15)
    page = request.GET.get('page')
    tickets_paginados = paginator.get_page(page)
    
    # Datos para filtros
    tipos_movimiento = TipoMovimiento.objects.filter(activo=True)
    estados = EstadoTicket.objects.filter(activo=True)
    
    context = {
        'tickets': tickets_paginados,
        'tipos_movimiento': tipos_movimiento,
        'estados': estados,
    }
    
    return render(request, 'tickets/lista_tickets.html', context)


@login_required
def crear_ticket(request):
    """Crear nuevo ticket de transporte."""
    
    if request.method == 'POST':
        # Obtener tipo de movimiento desde el botón seleccionado
        tipo_movimiento_codigo = request.POST.get('tipo_movimiento_codigo')
        
        if not tipo_movimiento_codigo:
            messages.error(request, 'Debe seleccionar un tipo de movimiento (Recepción o Envío).')
            return redirect('tickets:crear_ticket')
        
        try:
            tipo_movimiento = TipoMovimiento.objects.get(codigo=tipo_movimiento_codigo, activo=True)
        except TipoMovimiento.DoesNotExist:
            messages.error(request, 'Tipo de movimiento no válido.')
            return redirect('tickets:crear_ticket')
        
        # Crear datos del POST para el formulario
        form_data = request.POST.copy()
        form_data['tipo_movimiento'] = tipo_movimiento.pk
        
        form = TicketForm(form_data)
        formset = DetalleMercaderiaFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Crear ticket
            ticket = form.save(commit=False)
            ticket.creado_por = request.user
            
            # Asignar estado inicial automáticamente
            estado_inicial = EstadoTicket.objects.filter(es_inicial=True).first()
            if estado_inicial:
                ticket.estado = estado_inicial
            else:
                # Crear estado inicial si no existe
                estado_inicial, created = EstadoTicket.objects.get_or_create(
                    codigo='ING',
                    defaults={
                        'nombre': 'Ingresado',
                        'descripcion': 'Ticket recién ingresado al sistema',
                        'es_inicial': True,
                        'color': '#28a745'
                    }
                )
                ticket.estado = estado_inicial
            
            ticket.save()
            
            # Guardar mercaderías
            formset.instance = ticket
            formset.save()
            
            messages.success(request, f'Ticket {ticket.numero_ticket} creado exitosamente con {formset.total_form_count()} mercadería(s).')
            return redirect('tickets:detalle_ticket', pk=ticket.pk)
        else:
            # Recargar la página con errores
            if not form.is_valid():
                messages.error(request, 'Error en los datos del ticket. Revise los campos.')
            if not formset.is_valid():
                messages.error(request, 'Error en los datos de mercaderías. Revise las mercaderías.')
            
            # Obtener datos para recargar el formulario
            tipos_movimiento = TipoMovimiento.objects.filter(activo=True).order_by('codigo')
            
            # Obtener datos para los selectores
            from transportes.models import Chofer
            from cuentas.models import cuenta
            from mercaderias.models import Mercaderia, ClasificacionCalidad
            from almacenamiento.models import Almacenaje
            
            try:
                choferes = Chofer.objects.filter(activo=True)
            except:
                choferes = Chofer.objects.all()
            
            try:
                cuentas = cuenta.objects.filter(activo=True)
            except:
                cuentas = cuenta.objects.all()
            
            try:
                mercaderias = Mercaderia.objects.filter(activo=True)
            except:
                mercaderias = Mercaderia.objects.all()
            
            try:
                calidades = ClasificacionCalidad.objects.filter(activo=True)
            except:
                calidades = ClasificacionCalidad.objects.all()
            
            try:
                ubicaciones = Almacenaje.objects.filter(activo=True)
            except:
                ubicaciones = Almacenaje.objects.all()
            
            context = {
                'form': form,
                'formset': formset,
                'tipos_movimiento': tipos_movimiento,
                'choferes': choferes,
                'cuentas': cuentas,
                'mercaderias': mercaderias,
                'calidades': calidades,
                'ubicaciones': ubicaciones,
                'tipo_seleccionado': tipo_movimiento_codigo,
                'form_data': request.POST,
            }
            
            return render(request, 'tickets/crear_ticket.html', context)
    
    else:
        # Formulario vacío para GET
        form = TicketForm()
        formset = DetalleMercaderiaFormSet()
    
    # Obtener tipos de movimiento activos
    tipos_movimiento = TipoMovimiento.objects.filter(activo=True).order_by('codigo')
    
    # Crear tipos básicos si no existen
    if not tipos_movimiento.exists():
        TipoMovimiento.objects.create(
            codigo='REC',
            nombre='Recepción',
            descripcion='Recepción de mercadería',
            activo=True,
            requiere_origen=False,
            requiere_destinatario=True
        )
        TipoMovimiento.objects.create(
            codigo='ENV',
            nombre='Envío', 
            descripcion='Envío de mercadería',
            activo=True,
            requiere_origen=True,
            requiere_destinatario=False
        )
        tipos_movimiento = TipoMovimiento.objects.filter(activo=True).order_by('codigo')
    
    # Obtener datos para los selectores
    from transportes.models import Chofer
    from cuentas.models import cuenta
    from mercaderias.models import Mercaderia, ClasificacionCalidad
    from almacenamiento.models import Almacenaje
    
    try:
        choferes = Chofer.objects.filter(activo=True)
    except:
        choferes = Chofer.objects.all()
    
    try:
        cuentas = cuenta.objects.filter(activo=True)
    except:
        cuentas = cuenta.objects.all()
    
    try:
        mercaderias = Mercaderia.objects.filter(activo=True)
    except:
        mercaderias = Mercaderia.objects.all()
    
    try:
        calidades = ClasificacionCalidad.objects.filter(activo=True)
    except:
        calidades = ClasificacionCalidad.objects.all()
    
    try:
        ubicaciones = Almacenaje.objects.filter(activo=True)
    except:
        ubicaciones = Almacenaje.objects.all()
    
    context = {
        'form': form,
        'formset': formset,
        'tipos_movimiento': tipos_movimiento,
        'choferes': choferes,
        'cuentas': cuentas,
        'mercaderias': mercaderias,
        'calidades': calidades,
        'ubicaciones': ubicaciones,
    }
    
    return render(request, 'tickets/crear_ticket.html', context)



@login_required
def detalle_ticket(request, pk):
    """Detalle completo de un ticket."""
    
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'tipo_movimiento', 'estado', 'creado_por', 'chofer', 
            'cuenta_transporte', 'origen', 'destinatario'
        ).prefetch_related(
            'detalle_mercaderias__mercaderia',
            'detalle_mercaderias__calidad_clasificacion',
            'detalle_mercaderias__ubicacion_almacenaje',
            'detalle_mercaderias__analisis',
            'comentarios__autor',
            'archivos__subido_por'
        ),
        pk=pk
    )
    
    context = {
        'ticket': ticket,
    }
    
    return render(request, 'tickets/detalle_ticket.html', context)


@login_required
@require_http_methods(["POST"])
def actualizar_pesos(request, pk):
    """Actualizar pesos del ticket (bruto/tara)."""
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Verificar que el ticket permite edición
    if not ticket.estado.permite_edicion:
        return JsonResponse({
            'success': False,
            'error': 'El ticket no permite modificaciones en su estado actual.'
        })
    
    try:
        peso_bruto = request.POST.get('peso_bruto')
        peso_tara = request.POST.get('peso_tara')
        
        if peso_bruto:
            ticket.peso_bruto = float(peso_bruto)
        
        if peso_tara:
            ticket.peso_tara = float(peso_tara)
        
        ticket.save()  # El peso_neto se calcula automáticamente
        
        return JsonResponse({
            'success': True,
            'peso_neto': float(ticket.peso_neto) if ticket.peso_neto else None,
            'message': 'Pesos actualizados correctamente.'
        })
        
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': 'Error en los datos de peso proporcionados.'
        })


@login_required
@require_http_methods(["POST"])
def marcar_salida(request, pk):
    """Marcar fecha de salida del camión."""
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if ticket.fecha_salida:
        return JsonResponse({
            'success': False,
            'error': 'El camión ya tiene registrada su salida.'
        })
    
    ticket.fecha_salida = timezone.now()
    ticket.save()
    
    return JsonResponse({
        'success': True,
        'fecha_salida': ticket.fecha_salida.strftime('%d/%m/%Y %H:%M'),
        'message': 'Salida registrada correctamente.'
    })


@login_required
def realizar_analisis(request, detalle_id):
    """Vista para realizar análisis de una mercadería específica."""
    
    detalle = get_object_or_404(DetalleMercaderia, pk=detalle_id)
    
    if request.method == 'POST':
        # Procesar formulario de análisis
        humedad = request.POST.get('humedad')
        proteina = request.POST.get('proteina')
        grasa = request.POST.get('grasa')
        observaciones = request.POST.get('observaciones_analisis', '')
        aprobado = request.POST.get('aprobado') == 'on'
        
        # Crear registro de análisis
        analisis = AnalisisMercaderia.objects.create(
            detalle_mercaderia=detalle,
            analista=request.user,
            humedad=humedad if humedad else None,
            proteina=proteina if proteina else None,
            grasa=grasa if grasa else None,
            observaciones_analisis=observaciones,
            aprobado=aprobado
        )
        
        # Marcar análisis como realizado
        detalle.analisis_realizado = True
        detalle.fecha_analisis = timezone.now()
        detalle.analizado_por = request.user
        detalle.save()
        
        messages.success(request, f'Análisis registrado para {detalle.mercaderia.nombre}.')
        return redirect('tickets:detalle_ticket', pk=detalle.ticket.pk)
    
    context = {
        'detalle': detalle,
    }
    
    return render(request, 'tickets/realizar_analisis.html', context)


@login_required
def estadisticas_avanzadas(request):
    """Estadísticas avanzadas y reportes."""
    
    # Aquí puedes agregar análisis más complejos
    context = {
        'titulo': 'Estadísticas Avanzadas'
    }
    
    return render(request, 'tickets/estadisticas.html', context)