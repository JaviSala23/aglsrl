"""
Vistas para el módulo de agenda y contactos.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Contacto, TipoContacto, Evento, TipoEvento, Tarea
from .forms import ContactoForm, EventoForm, TareaForm, RespuestaAsignacionForm
from cuentas.models import cuenta


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
            Q(creado_por=user) | Q(id__in=tareas_asignadas_ids),
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
        
        # Mensaje según si se asignó o no
        if form.instance.asignado_a:
            messages.success(
                self.request, 
                f'Tarea "{form.instance.titulo}" creada y asignada a {form.instance.asignado_a.get_full_name() or form.instance.asignado_a.username}.'
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
                asignacion.estado = 'aceptada'
                mensaje = f'Has aceptado la tarea "{asignacion.tarea.titulo}".'
            else:
                asignacion.estado = 'rechazada'
                mensaje = f'Has rechazado la tarea "{asignacion.tarea.titulo}".'
            
            if comentarios:
                asignacion.comentarios = comentarios
            
            asignacion.save()
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
def eliminar_tarea_view(request, pk):
    """Eliminar tarea."""
    tarea = get_object_or_404(Tarea, pk=pk)
    tarea.activa = False
    tarea.save()
    messages.success(request, f'Tarea "{tarea.titulo}" eliminada.')
    return redirect('agenda:lista_tareas')


@login_required
def toggle_completar_tarea_view(request, pk):
    """Completar/reactivar tarea."""
    tarea = get_object_or_404(Tarea, pk=pk)
    
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
