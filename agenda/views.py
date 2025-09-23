"""
Vistas para el módulo de agenda y contactos.
"""
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Contacto, TipoContacto, Evento, TipoEvento, Tarea, ComentarioTarea
from .forms import ContactoForm, EventoForm, TareaForm, RespuestaAsignacionForm, ComentarioTareaForm
from cuentas.models import cuenta
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .models import ChatRoom, ChatMembership, ChatMessage


@login_required
def obtener_cuenta_info(request, cuenta_id):
    """Vista AJAX para obtener información de una cuenta."""
    try:
        cuenta_obj = get_object_or_404(cuenta, id_cuenta=cuenta_id, activo=True)
        # Usar nombre_fantasia si existe, sino razon_social
        nombre_empresa = cuenta_obj.nombre_fantasia or cuenta_obj.razon_social
        
        return JsonResponse({
            'success': True,
            'nombre_empresa': nombre_empresa,
            'razon_social': cuenta_obj.razon_social,
            'nombre_fantasia': cuenta_obj.nombre_fantasia,
            'telefono': cuenta_obj.telefono_cuenta,
            'celular': cuenta_obj.celular_cuenta,
            'email': cuenta_obj.email_cuenta,
            'direccion': cuenta_obj.direccion_cuenta,
            'localidad': cuenta_obj.localidad_idlocalidad.nombre_localidad if cuenta_obj.localidad_idlocalidad else '',
            'provincia': cuenta_obj.provincia_idprovincia.nombre_provincia if cuenta_obj.provincia_idprovincia else '',
            'pais': cuenta_obj.pais_id.nombre if cuenta_obj.pais_id else ''
        })
    except cuenta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Cuenta no encontrada'
        })


class DashboardAgendaView(LoginRequiredMixin, TemplateView):
    """Vista del dashboard principal de agenda."""
    template_name = 'agenda/dashboard.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_contactos'] = Contacto.objects.filter(activo=True).count()
        context['contactos_favoritos'] = Contacto.objects.filter(activo=True, favorito=True).count()
        context['total_eventos'] = Evento.objects.filter(activo=True).count()
        context['eventos_hoy'] = Evento.objects.filter(
            activo=True,
            fecha_inicio__date=timezone.now().date()
        ).count()
        context['tareas_pendientes'] = Tarea.objects.filter(
            activa=True,
            estado='pendiente'
        ).count()
        context['tareas_vencidas'] = Tarea.objects.filter(
            activa=True,
            estado='pendiente',
            fecha_vencimiento__lt=timezone.now()
        ).count()
        
        # Próximos eventos (siguiente semana)
        fecha_limite = timezone.now() + timedelta(days=7)
        context['proximos_eventos'] = Evento.objects.filter(
            activo=True,
            fecha_inicio__gte=timezone.now(),
            fecha_inicio__lte=fecha_limite
        ).order_by('fecha_inicio')[:5]
        
        # Contactos recientes
        context['contactos_recientes'] = Contacto.objects.filter(
            activo=True
        ).order_by('-fecha_creacion')[:5]
        
        # Tareas urgentes
        context['tareas_urgentes'] = Tarea.objects.filter(
            activa=True,
            estado='pendiente',
            prioridad='urgente'
        ).order_by('fecha_vencimiento')[:5]
        
        return context


class ListaContactosView(LoginRequiredMixin, ListView):
    """Vista de lista de contactos."""
    model = Contacto
    template_name = 'agenda/lista_contactos.html'
    context_object_name = 'contactos'
    paginate_by = 20
    login_url = 'main:login'
    
    def get_queryset(self):
        queryset = Contacto.objects.filter(activo=True).select_related(
            'tipo_contacto', 'cuenta_relacionada'
        ).order_by('apellido', 'nombre')
        
        # Filtros
        busqueda = self.request.GET.get('q')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(apellido__icontains=busqueda) |
                Q(empresa__icontains=busqueda) |
                Q(email_principal__icontains=busqueda) |
                Q(telefono_principal__icontains=busqueda)
            )
        
        tipo_contacto = self.request.GET.get('tipo_contacto')
        if tipo_contacto:
            queryset = queryset.filter(tipo_contacto=tipo_contacto)
            
        favoritos = self.request.GET.get('favoritos')
        if favoritos == 'true':
            queryset = queryset.filter(favorito=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_contacto'] = TipoContacto.objects.filter(activo=True)
        context['filtros'] = {
            'q': self.request.GET.get('q', ''),
            'tipo_contacto': self.request.GET.get('tipo_contacto', ''),
            'favoritos': self.request.GET.get('favoritos', ''),
        }
        return context


class CrearContactoView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo contacto."""
    model = Contacto
    form_class = ContactoForm
    template_name = 'agenda/crear_contacto.html'
    login_url = 'main:login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Contacto creado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return '/agenda/contactos/'


class DetalleContactoView(LoginRequiredMixin, DetailView):
    """Vista de detalle de contacto."""
    model = Contacto
    template_name = 'agenda/detalle_contacto.html'
    context_object_name = 'contacto'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contacto = self.get_object()
        
        # Obtener eventos recientes relacionados con este contacto
        context['eventos_recientes'] = Evento.objects.filter(
            contactos=contacto,
            activo=True
        ).order_by('-fecha_inicio')[:5]
        
        # Obtener tareas recientes relacionadas con este contacto
        context['tareas_recientes'] = Tarea.objects.filter(
            contacto_relacionado=contacto,
            activa=True
        ).order_by('-fecha_creacion')[:5]
        
        return context


class EditarContactoView(LoginRequiredMixin, UpdateView):
    """Vista para editar contacto."""
    model = Contacto
    form_class = ContactoForm
    template_name = 'agenda/editar_contacto.html'
    login_url = 'main:login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Contacto actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return f'/agenda/contactos/{self.object.pk}/'


class AgendaCalendarioView(LoginRequiredMixin, TemplateView):
    """Vista del calendario de agenda."""
    template_name = 'agenda/calendario.html'
    login_url = 'main:login'


class ListaEventosView(LoginRequiredMixin, ListView):
    """Vista de lista de eventos."""
    model = Evento
    template_name = 'agenda/lista_eventos.html'
    context_object_name = 'eventos'
    paginate_by = 20
    login_url = 'main:login'


class CrearEventoView(LoginRequiredMixin, CreateView):
    """Vista para crear evento."""
    model = Evento
    form_class = EventoForm
    template_name = 'agenda/crear_evento.html'
    login_url = 'main:login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Evento creado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return '/agenda/eventos/'


class DetalleEventoView(LoginRequiredMixin, DetailView):
    """Vista de detalle de evento."""
    model = Evento
    template_name = 'agenda/detalle_evento.html'
    login_url = 'main:login'


class EditarEventoView(LoginRequiredMixin, UpdateView):
    """Vista para editar evento."""
    model = Evento
    template_name = 'agenda/editar_evento.html'
    fields = '__all__'
    login_url = 'main:login'


class ListaTareasView(LoginRequiredMixin, ListView):
    """Vista de lista de tareas."""
    model = Tarea
    template_name = 'agenda/lista_tareas.html'
    context_object_name = 'tareas'
    paginate_by = 20
    login_url = 'main:login'
    
    def get_queryset(self):
        """Obtener tareas creadas por el usuario o asignadas a él."""
        from .models import AsignacionTarea
        user = self.request.user
        
        # Obtener IDs de tareas asignadas al usuario
        tareas_asignadas_ids = AsignacionTarea.objects.filter(
            usuario=user
        ).values_list('tarea_id', flat=True)
        
        return Tarea.objects.filter(
            Q(creado_por=user) | Q(id_tarea__in=tareas_asignadas_ids),
            activa=True
        ).order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from .models import AsignacionTarea
        
        # Tareas por categorías
        context['tareas_creadas'] = Tarea.objects.filter(
            creado_por=user, activa=True
        ).count()
        
        # Contar asignaciones por estado
        context['tareas_asignadas'] = AsignacionTarea.objects.filter(
            usuario=user, tarea__activa=True
        ).count()
        
        context['tareas_pendientes_respuesta'] = AsignacionTarea.objects.filter(
            usuario=user, estado='asignada', tarea__activa=True
        ).count()
        
        # Añadir asignaciones del usuario para mostrar en el template
        context['mis_asignaciones'] = AsignacionTarea.objects.filter(
            usuario=user, tarea__activa=True
        ).select_related('tarea')
        
        return context


class CrearTareaView(LoginRequiredMixin, CreateView):
    """Vista para crear tarea."""
    model = Tarea
    form_class = TareaForm
    template_name = 'agenda/crear_tarea.html'
    login_url = 'main:login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        
        # Obtener usuarios asignados del formulario
        usuarios_asignados = form.cleaned_data.get('usuarios_asignados', [])
        
        # Mensaje según si se asignó o no
        if usuarios_asignados:
            nombres_asignados = [user.get_full_name() or user.username for user in usuarios_asignados]
            messages.success(
                self.request, 
                f'Tarea "{form.instance.titulo}" creada y asignada a: {", ".join(nombres_asignados)}.'
            )
        else:
            messages.success(self.request, f'Tarea "{form.instance.titulo}" creada exitosamente.')
        
        return response
    
    def get_success_url(self):
        return '/agenda/tareas/'


@login_required
def responder_asignacion_tarea_view(request, asignacion_id):
    """Vista para que el usuario asignado responda a una tarea."""
    from .models import AsignacionTarea
    
    asignacion = get_object_or_404(
        AsignacionTarea, 
        id=asignacion_id, 
        usuario=request.user, 
        estado='asignada'
    )
    
    if request.method == 'POST':
        form = RespuestaAsignacionForm(request.POST)
        if form.is_valid():
            respuesta = form.cleaned_data['respuesta']
            comentarios = form.cleaned_data.get('comentarios', '')
            
            if respuesta == 'aceptar':
                asignacion.aceptar(comentarios)
                mensaje = f'Has aceptado la tarea "{asignacion.tarea.titulo}".'
            else:
                asignacion.rechazar(comentarios)
                mensaje = f'Has rechazado la tarea "{asignacion.tarea.titulo}".'
            
            messages.success(request, mensaje)
            return redirect('agenda:lista_tareas')
    else:
        form = RespuestaAsignacionForm()
    
    return render(request, 'agenda/responder_asignacion.html', {
        'form': form,
        'asignacion': asignacion,
        'tarea': asignacion.tarea
    })


class DetalleTareaView(LoginRequiredMixin, DetailView):
    """Vista de detalle de tarea."""
    model = Tarea
    template_name = 'agenda/detalle_tarea.html'
    login_url = 'main:login'
    
    def get_queryset(self):
        """Solo mostrar tareas que el usuario creó o que le fueron asignadas."""
        from .models import AsignacionTarea
        user = self.request.user
        
        # Obtener IDs de tareas asignadas al usuario
        tareas_asignadas_ids = AsignacionTarea.objects.filter(
            usuario=user
        ).values_list('tarea_id', flat=True)
        
        return Tarea.objects.filter(
            Q(creado_por=user) | Q(id_tarea__in=tareas_asignadas_ids),
            activa=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarea = self.get_object()
        
        # Verificar si el usuario puede comentar
        # Puede comentar si es el creador o si está asignado a la tarea
        puede_comentar = (
            tarea.creado_por == self.request.user or
            tarea.asignaciones.filter(usuario=self.request.user).exists()
        )
        
        context['puede_comentar'] = puede_comentar
        return context


class EditarTareaView(LoginRequiredMixin, UpdateView):
    """Vista para editar tarea."""
    model = Tarea
    form_class = TareaForm
    template_name = 'agenda/editar_tarea.html'
    login_url = 'main:login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Añadir asignaciones actuales de la tarea
        from .models import AsignacionTarea
        context['asignaciones_actuales'] = AsignacionTarea.objects.filter(
            tarea=self.object
        ).select_related('usuario')
        
        return context
    
    def get_queryset(self):
        """Solo el creador puede editar la tarea."""
        return Tarea.objects.filter(creado_por=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Tarea "{form.instance.titulo}" actualizada exitosamente.')
        return response
    
    def get_success_url(self):
        return '/agenda/tareas/'


# Vistas de función
@login_required
def eliminar_contacto_view(request, pk):
    """Eliminar contacto."""
    contacto = get_object_or_404(Contacto, pk=pk)
    contacto.activo = False
    contacto.save()
    messages.success(request, f'Contacto "{contacto.nombre_completo}" eliminado.')
    return redirect('agenda:lista_contactos')


@login_required
def toggle_favorito_view(request, pk):
    """Alternar estado de favorito."""
    contacto = get_object_or_404(Contacto, pk=pk)
    contacto.favorito = not contacto.favorito
    contacto.save()
    
    estado = "agregado a" if contacto.favorito else "removido de"
    messages.success(request, f'Contacto {estado} favoritos.')
    return redirect('agenda:detalle_contacto', pk=pk)


@login_required
def eliminar_evento_view(request, pk):
    """Eliminar evento."""
    evento = get_object_or_404(Evento, pk=pk)
    evento.activo = False
    evento.save()
    messages.success(request, f'Evento "{evento.titulo}" eliminado.')
    return redirect('agenda:lista_eventos')


@login_required
@login_required
def eliminar_tarea_view(request, pk):
    """Eliminar tarea - Solo el creador puede eliminar."""
    tarea = get_object_or_404(Tarea, pk=pk, creado_por=request.user)
    titulo_tarea = tarea.titulo
    tarea.activa = False
    tarea.save()
    messages.success(request, f'Tarea "{titulo_tarea}" eliminada.')
    return redirect('agenda:lista_tareas')


@login_required
def toggle_completar_tarea_view(request, pk):
    """Completar/reactivar tarea - Creador o usuarios asignados."""
    from .models import AsignacionTarea
    
    # Verificar que el usuario pueda modificar esta tarea
    tarea = get_object_or_404(Tarea, pk=pk)
    
    # Solo el creador o usuarios asignados pueden completar la tarea
    es_creador = tarea.creado_por == request.user
    es_asignado = AsignacionTarea.objects.filter(
        tarea=tarea, 
        usuario=request.user
    ).exists()
    
    if not (es_creador or es_asignado):
        messages.error(request, 'No tienes permisos para modificar esta tarea.')
        return redirect('agenda:lista_tareas')
    
    if tarea.estado == 'completada':
        tarea.estado = 'pendiente'
        tarea.fecha_completada = None
        messages.success(request, f'Tarea "{tarea.titulo}" reactivada.')
    else:
        tarea.estado = 'completada'
        tarea.fecha_completada = timezone.now()
        messages.success(request, f'Tarea "{tarea.titulo}" completada.')
    
    tarea.save()
    return redirect('agenda:lista_tareas')


# APIs
@login_required
def eventos_api_view(request):
    """API para obtener eventos en formato JSON."""
    eventos = Evento.objects.filter(activo=True)
    
    # Filtros opcionales
    fecha_inicio = request.GET.get('start')
    fecha_fin = request.GET.get('end')
    
    if fecha_inicio:
        eventos = eventos.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        eventos = eventos.filter(fecha_fin__lte=fecha_fin)
    
    data = []
    for evento in eventos:
        data.append({
            'id': evento.id_evento,
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat(),
            'backgroundColor': evento.tipo_evento.color,
            'borderColor': evento.tipo_evento.color,
            'description': evento.descripcion,
            'location': evento.ubicacion,
        })
    
    return JsonResponse(data, safe=False)


@login_required
def estadisticas_api_view(request):
    """API para estadísticas del dashboard."""
    data = {
        'contactos': {
            'total': Contacto.objects.filter(activo=True).count(),
            'favoritos': Contacto.objects.filter(activo=True, favorito=True).count(),
            'por_tipo': list(Contacto.objects.filter(activo=True).values('tipo_contacto__nombre').annotate(count=Count('id_contacto')))
        },
        'eventos': {
            'total': Evento.objects.filter(activo=True).count(),
            'hoy': Evento.objects.filter(activo=True, fecha_inicio__date=timezone.now().date()).count(),
            'semana': Evento.objects.filter(
                activo=True,
                fecha_inicio__gte=timezone.now(),
                fecha_inicio__lte=timezone.now() + timedelta(days=7)
            ).count()
        },
        'tareas': {
            'pendientes': Tarea.objects.filter(activa=True, estado='pendiente').count(),
            'vencidas': Tarea.objects.filter(
                activa=True,
                estado='pendiente',
                fecha_vencimiento__lt=timezone.now()
            ).count()
        }
    }
    
    return JsonResponse(data)


class TareasKanbanView(LoginRequiredMixin, TemplateView):
    """Vista Kanban para tareas."""
    template_name = 'agenda/tareas_kanban.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from .models import AsignacionTarea
        
        # Obtener IDs de tareas asignadas al usuario
        tareas_asignadas_ids = AsignacionTarea.objects.filter(
            usuario=user
        ).values_list('tarea_id', flat=True)
        
        # Obtener todas las tareas del usuario (creadas por él o asignadas a él)
        todas_las_tareas = Tarea.objects.filter(
            Q(creado_por=user) | Q(id_tarea__in=tareas_asignadas_ids),
            activa=True
        ).order_by('-fecha_creacion')
        
        # Organizar tareas por estado para el Kanban
        context['tareas_pendientes'] = todas_las_tareas.filter(estado='pendiente')
        context['tareas_en_progreso'] = todas_las_tareas.filter(estado='en_progreso')
        context['tareas_completadas'] = todas_las_tareas.filter(estado='completada')
        context['tareas_canceladas'] = todas_las_tareas.filter(estado='cancelada')
        
        # Estadísticas generales
        context['total_tareas'] = todas_las_tareas.count()
        context['tareas_creadas'] = Tarea.objects.filter(
            creado_por=user, activa=True
        ).count()
        context['tareas_asignadas'] = AsignacionTarea.objects.filter(
            usuario=user, tarea__activa=True
        ).count()
        
        # Añadir asignaciones del usuario para mostrar en el template
        context['mis_asignaciones'] = AsignacionTarea.objects.filter(
            usuario=user, tarea__activa=True
        ).select_related('tarea')
        
        return context


@login_required
@login_required
def actualizar_estado_tarea_kanban(request, tarea_id):
    """Vista AJAX para actualizar el estado de una tarea desde el Kanban."""
    if request.method == 'POST':
        try:
            # Verificar que el usuario pueda modificar esta tarea
            from .models import AsignacionTarea
            tarea = get_object_or_404(Tarea, id_tarea=tarea_id)
            
            # Solo el creador o usuarios asignados pueden actualizar el estado
            es_creador = tarea.creado_por == request.user
            es_asignado = AsignacionTarea.objects.filter(
                tarea=tarea, 
                usuario=request.user
            ).exists()
            
            if not (es_creador or es_asignado):
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permisos para modificar esta tarea'
                })
            
            nuevo_estado = request.POST.get('estado')
            
            # Validar que el estado sea válido
            estados_validos = ['pendiente', 'en_progreso', 'completada', 'cancelada']
            if nuevo_estado not in estados_validos:
                return JsonResponse({
                    'success': False,
                    'error': 'Estado no válido'
                })
            
            # Actualizar el estado
            tarea.estado = nuevo_estado
            
            # Si se marca como completada, añadir fecha de completado
            if nuevo_estado == 'completada':
                tarea.fecha_completada = timezone.now()
                tarea.porcentaje_completado = 100
            elif nuevo_estado in ['pendiente', 'en_progreso']:
                tarea.fecha_completada = None
                if nuevo_estado == 'pendiente':
                    tarea.porcentaje_completado = 0
            
            tarea.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Tarea "{tarea.titulo}" actualizada correctamente'
            })
            
        except Tarea.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tarea no encontrada'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })


@login_required
def agregar_comentario_tarea_view(request, tarea_id):
    """Vista para agregar comentarios a una tarea."""
    tarea = get_object_or_404(Tarea, id_tarea=tarea_id)
    
    # Verificar que el usuario tenga permisos (creador o asignado)
    from .models import AsignacionTarea
    es_creador = tarea.creado_por == request.user
    es_asignado = AsignacionTarea.objects.filter(
        tarea=tarea, 
        usuario=request.user
    ).exists()
    
    if not (es_creador or es_asignado):
        messages.error(request, 'No tienes permisos para comentar en esta tarea.')
        return redirect('agenda:detalle_tarea', pk=tarea_id)
    
    if request.method == 'POST':
        form = ComentarioTareaForm(request.POST)
        
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarea = tarea
            comentario.usuario = request.user
            comentario.save()
            
            messages.success(request, 'Comentario agregado correctamente.')
            return redirect('agenda:detalle_tarea', pk=tarea_id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = ComentarioTareaForm()
    
    return render(request, 'agenda/agregar_comentario.html', {
        'form': form,
        'tarea': tarea
    })


@login_required
def chat_list_rooms(request):
    """Listar salas en las que participa el usuario."""
    rooms = ChatRoom.objects.filter(membresias__usuario=request.user, activo=True).distinct()
    data = []
    for r in rooms:
        data.append({
            'id': r.id,
            'nombre': r.nombre or f'Sala {r.id}',
            'es_grupal': r.es_grupal,
            'miembros': [m.usuario.get_full_name() or m.usuario.username for m in r.membresias.select_related('usuario')]
        })
    return JsonResponse({'rooms': data})


@login_required
@require_POST
def chat_create_private(request):
    """Crear o retornar sala privada entre el usuario y `other_user_id`."""
    other_id = request.POST.get('other_user_id')
    if not other_id:
        return HttpResponseBadRequest('Falta other_user_id')
    try:
        other = request.user.__class__.objects.get(pk=other_id)
    except Exception:
        return HttpResponseBadRequest('Usuario destino no encontrado')

    # Buscar sala privada existente entre ambos
    salas = ChatRoom.objects.filter(es_grupal=False, membresias__usuario=request.user).distinct()
    for s in salas:
        if s.membresias.filter(usuario=other).exists():
            return JsonResponse({'room_id': s.id})

    # Crear nueva sala privada
    sala = ChatRoom.objects.create(es_grupal=False, creado_por=request.user)
    ChatMembership.objects.create(sala=sala, usuario=request.user)
    ChatMembership.objects.create(sala=sala, usuario=other)
    return JsonResponse({'room_id': sala.id})


@login_required
@require_POST
def chat_add_members(request, room_id):
    """Agregar miembros a una sala existente (user_ids = '1,2,3')."""
    sala = get_object_or_404(ChatRoom, pk=room_id, activo=True)
    # debe ser miembro para poder agregar
    if not sala.membresias.filter(usuario=request.user).exists():
        return JsonResponse({'error': 'No tienes acceso a esta sala'}, status=403)

    ids = request.POST.get('user_ids', '').strip()
    if not ids:
        return HttpResponseBadRequest('Falta user_ids')
    try:
        id_list = [int(x) for x in ids.split(',') if x.strip()]
    except ValueError:
        return HttpResponseBadRequest('IDs inválidos')

    User = get_user_model()
    added = []
    for uid in id_list:
        try:
            u = User.objects.get(pk=uid, is_active=True)
        except User.DoesNotExist:
            continue
        # evitar duplicados
        if sala.membresias.filter(usuario=u).exists():
            continue
        ChatMembership.objects.create(sala=sala, usuario=u)
        added.append({'id': u.id, 'nombre': u.get_full_name() or u.username})

    return JsonResponse({'added': added})


@login_required
@require_POST
def chat_close_room(request, room_id):
    """Cerrar (desactivar) una sala. Solo el creador puede cerrarla."""
    sala = get_object_or_404(ChatRoom, pk=room_id, activo=True)
    if sala.creado_por != request.user:
        return JsonResponse({'error': 'Solo el creador puede cerrar la sala'}, status=403)
    sala.activo = False
    sala.save()
    return JsonResponse({'closed': True})
@login_required
def chat_search_users(request):
    """Buscar usuarios por nombre/username para crear salas privadas."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'users': []})
    User = get_user_model()
    usuarios = User.objects.filter(
        Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q),
        is_active=True
    ).exclude(pk=request.user.pk)[:10]
    data = []
    for u in usuarios:
        data.append({'id': u.id, 'username': u.username, 'nombre': u.get_full_name() or u.username})
    return JsonResponse({'users': data})


@login_required
def chat_get_messages(request, room_id):
    """Obtener últimos mensajes de una sala (limit 50)."""
    sala = get_object_or_404(ChatRoom, pk=room_id, activo=True)
    if not sala.membresias.filter(usuario=request.user).exists():
        return JsonResponse({'error': 'No tienes acceso a esta sala'}, status=403)
    msgs = sala.mensajes.all().order_by('fecha_creacion')[:200]
    data = []
    for m in msgs:
        data.append({
            'id': m.id,
            'usuario': m.usuario.get_full_name() or m.usuario.username,
            'usuario_id': m.usuario.id,
            'mensaje': m.mensaje,
            'fecha': m.fecha_creacion.isoformat()
        })
    return JsonResponse({'messages': data})


@login_required
def chat_unread_count(request):
    """Devuelve la cantidad total de mensajes sin leer para las salas en las que participa el usuario."""
    # Mensajes en salas donde el usuario es miembro y que no fueron escritos por el usuario
    count = ChatMessage.objects.filter(sala__membresias__usuario=request.user, leido=False).exclude(usuario=request.user).distinct().count()
    return JsonResponse({'unread_count': count})



@login_required
@require_POST
def chat_mark_read(request):
    """Marca como leídos los mensajes especificados por ids (message_ids = '1,2,3')."""
    ids = request.POST.get('message_ids', '').strip()
    if not ids:
        return HttpResponseBadRequest('Falta message_ids')
    try:
        id_list = [int(x) for x in ids.split(',') if x.strip()]
    except ValueError:
        return HttpResponseBadRequest('IDs inválidos')

    msgs = ChatMessage.objects.filter(id__in=id_list)
    # Asegurar que el usuario sea miembro de las salas de esos mensajes
    msgs = msgs.filter(sala__membresias__usuario=request.user).exclude(usuario=request.user)
    updated = msgs.update(leido=True)
    return JsonResponse({'marked': updated})


@login_required
@require_POST
def chat_send_message(request, room_id):
    sala = get_object_or_404(ChatRoom, pk=room_id, activo=True)
    if not sala.membresias.filter(usuario=request.user).exists():
        return JsonResponse({'error': 'No tienes acceso a esta sala'}, status=403)
    text = request.POST.get('mensaje', '').strip()
    if not text:
        return HttpResponseBadRequest('Mensaje vacío')
    msg = ChatMessage.objects.create(sala=sala, usuario=request.user, mensaje=text)
    return JsonResponse({
        'id': msg.id,
        'usuario': msg.usuario.get_full_name() or msg.usuario.username,
        'usuario_id': msg.usuario.id,
        'mensaje': msg.mensaje,
        'fecha': msg.fecha_creacion.isoformat()
    })
