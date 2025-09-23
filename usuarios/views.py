from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
import json

from .models import (
    Usuario, Equipo, Proyecto, Tarea, ComentarioTarea, 
    HistorialTarea, Notificacion, Agenda
)
from .serializers import (
    UsuarioSerializer, EquipoSerializer, ProyectoSerializer,
    TareaSerializer, NotificacionSerializer, AgendaSerializer
)

# =====================================================
# VISTAS DE TEMPLATES
# =====================================================

@login_required
def dashboard_usuarios(request):
    """Dashboard principal de gestión de usuarios y tareas"""
    usuario = request.user
    
    # Estadísticas del usuario
    mis_tareas_pendientes = Tarea.objects.filter(
        asignado_a=usuario, 
        estado__in=['PENDIENTE', 'EN_PROGRESO']
    ).count()
    
    mis_tareas_vencidas = Tarea.objects.filter(
        asignado_a=usuario,
        fecha_vencimiento__lt=timezone.now(),
        estado__in=['PENDIENTE', 'EN_PROGRESO']
    ).count()
    
    tareas_creadas_por_mi = Tarea.objects.filter(creado_por=usuario).count()
    
    # Tareas recientes
    tareas_recientes = Tarea.objects.filter(
        Q(asignado_a=usuario) | Q(creado_por=usuario)
    ).distinct().order_by('-fecha_actualizacion')[:5]
    
    # Proyectos activos
    mis_proyectos = Proyecto.objects.filter(
        Q(propietario=usuario) | Q(colaboradores=usuario)
    ).filter(estado__in=['PLANIFICACION', 'EN_CURSO']).distinct()[:3]
    
    # Notificaciones no leídas
    notificaciones_no_leidas = usuario.notificaciones.filter(leida=False).count()
    
    # Eventos de agenda para hoy
    hoy = timezone.now().date()
    eventos_hoy = Agenda.objects.filter(
        Q(organizador=usuario) | Q(asistentes=usuario),
        fecha_inicio__date=hoy
    ).distinct()
    
    context = {
        'mis_tareas_pendientes': mis_tareas_pendientes,
        'mis_tareas_vencidas': mis_tareas_vencidas,
        'tareas_creadas_por_mi': tareas_creadas_por_mi,
        'tareas_recientes': tareas_recientes,
        'mis_proyectos': mis_proyectos,
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'eventos_hoy': eventos_hoy,
    }
    
    return render(request, 'usuarios/dashboard.html', context)


@login_required
def lista_tareas(request):
    """Lista todas las tareas que el usuario puede ver"""
    usuario = request.user
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    prioridad_filtro = request.GET.get('prioridad', '')
    proyecto_filtro = request.GET.get('proyecto', '')
    asignado_filtro = request.GET.get('asignado', '')
    
    # Query base - tareas que el usuario puede ver
    tareas = Tarea.objects.filter(
        Q(asignado_a=usuario) |
        Q(creado_por=usuario) |
        Q(es_publica=True) |
        (Q(es_personal=False) & Q(proyecto__colaboradores=usuario))
    ).distinct()
    
    # Aplicar filtros
    if estado_filtro:
        tareas = tareas.filter(estado=estado_filtro)
    if prioridad_filtro:
        tareas = tareas.filter(prioridad=prioridad_filtro)
    if proyecto_filtro:
        tareas = tareas.filter(proyecto_id=proyecto_filtro)
    if asignado_filtro:
        tareas = tareas.filter(asignado_a_id=asignado_filtro)
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_creacion')
    tareas = tareas.order_by(orden)
    
    # Paginación
    paginator = Paginator(tareas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    proyectos = Proyecto.objects.filter(
        Q(propietario=usuario) | Q(colaboradores=usuario)
    ).distinct()
    
    usuarios_disponibles = Usuario.objects.filter(activo=True)
    
    context = {
        'page_obj': page_obj,
        'proyectos': proyectos,
        'usuarios_disponibles': usuarios_disponibles,
        'filtros': {
            'estado': estado_filtro,
            'prioridad': prioridad_filtro,
            'proyecto': proyecto_filtro,
            'asignado': asignado_filtro,
            'orden': orden,
        }
    }
    
    return render(request, 'usuarios/lista_tareas.html', context)


@login_required
def mis_tareas(request):
    """Vista personal de las tareas del usuario"""
    usuario = request.user
    
    # Mis tareas por estado
    pendientes = usuario.tareas_asignadas.filter(estado='PENDIENTE')
    en_progreso = usuario.tareas_asignadas.filter(estado='EN_PROGRESO')
    completadas = usuario.tareas_asignadas.filter(estado='COMPLETADA')[:10]  # Últimas 10
    
    # Tareas vencidas
    vencidas = usuario.tareas_asignadas.filter(
        fecha_vencimiento__lt=timezone.now(),
        estado__in=['PENDIENTE', 'EN_PROGRESO']
    )
    
    # Tareas que he creado para otros
    creadas_para_otros = usuario.tareas_creadas.exclude(asignado_a=usuario)[:10]
    
    context = {
        'pendientes': pendientes,
        'en_progreso': en_progreso,
        'completadas': completadas,
        'vencidas': vencidas,
        'creadas_para_otros': creadas_para_otros,
    }
    
    return render(request, 'usuarios/mis_tareas.html', context)


@login_required
def crear_tarea(request):
    """Crear nueva tarea"""
    if request.method == 'POST':
        # Aquí iría el formulario de creación
        # Por ahora, retorna la vista
        messages.success(request, 'Tarea creada exitosamente.')
        return redirect('usuarios:lista_tareas')
    
    # Datos para el formulario
    usuarios_disponibles = Usuario.objects.filter(activo=True)
    proyectos_disponibles = Proyecto.objects.filter(
        Q(propietario=request.user) | Q(colaboradores=request.user)
    ).distinct()
    
    context = {
        'usuarios_disponibles': usuarios_disponibles,
        'proyectos_disponibles': proyectos_disponibles,
    }
    
    return render(request, 'usuarios/crear_tarea.html', context)


@login_required
def detalle_tarea(request, pk):
    """Detalle de una tarea específica"""
    tarea = get_object_or_404(Tarea, pk=pk)
    
    # Verificar permisos
    if not tarea.puede_ver(request.user):
        messages.error(request, 'No tienes permisos para ver esta tarea.')
        return redirect('usuarios:lista_tareas')
    
    # Comentarios de la tarea
    comentarios = tarea.comentarios.all()
    
    # Historial de cambios
    historial = tarea.historial.all()[:10]  # Últimos 10 cambios
    
    context = {
        'tarea': tarea,
        'comentarios': comentarios,
        'historial': historial,
        'puede_editar': tarea.puede_editar(request.user),
    }
    
    return render(request, 'usuarios/detalle_tarea.html', context)


# Placeholder para otras vistas
def editar_tarea(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Editar Tarea'})

def eliminar_tarea(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Eliminar Tarea'})

def completar_tarea(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Completar Tarea'})

def lista_proyectos(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Lista de Proyectos'})

def crear_proyecto(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Crear Proyecto'})

def detalle_proyecto(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Detalle de Proyecto'})

def editar_proyecto(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Editar Proyecto'})

def agenda_calendario(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Agenda/Calendario'})

def crear_evento(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Crear Evento'})

def detalle_evento(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Detalle de Evento'})

def lista_equipos(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Lista de Equipos'})

def detalle_equipo(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Detalle de Equipo'})

def lista_notificaciones(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Notificaciones'})

def marcar_notificacion_leida(request, pk):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Marcar Notificación'})

def perfil_usuario(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Perfil de Usuario'})

def editar_perfil(request):
    return render(request, 'usuarios/placeholder.html', {'titulo': 'Editar Perfil'})


# =====================================================
# VISTAS AJAX
# =====================================================

@login_required
def cambiar_estado_tarea_ajax(request):
    """Cambiar estado de tarea vía AJAX"""
    if request.method == 'POST':
        tarea_id = request.POST.get('tarea_id')
        nuevo_estado = request.POST.get('estado')
        
        try:
            tarea = Tarea.objects.get(pk=tarea_id)
            if tarea.puede_editar(request.user):
                tarea.estado = nuevo_estado
                if nuevo_estado == 'COMPLETADA':
                    tarea.fecha_completado = timezone.now()
                tarea.save()
                
                # Crear entrada en historial
                HistorialTarea.objects.create(
                    tarea=tarea,
                    usuario=request.user,
                    accion='Cambio de estado',
                    descripcion=f'Estado cambiado a {tarea.get_estado_display()}'
                )
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Sin permisos'})
        except Tarea.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Tarea no encontrada'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def obtener_tareas_calendario(request):
    """Obtener tareas para mostrar en calendario"""
    inicio = request.GET.get('start')
    fin = request.GET.get('end')
    
    if inicio and fin:
        inicio_date = datetime.fromisoformat(inicio.replace('Z', '+00:00'))
        fin_date = datetime.fromisoformat(fin.replace('Z', '+00:00'))
        
        tareas = Tarea.objects.filter(
            Q(asignado_a=request.user) | Q(creado_por=request.user),
            fecha_vencimiento__range=[inicio_date, fin_date]
        ).distinct()
        
        eventos = []
        for tarea in tareas:
            color = {
                'PENDIENTE': '#dc3545',
                'EN_PROGRESO': '#ffc107',
                'COMPLETADA': '#28a745',
                'BLOQUEADA': '#6c757d',
                'CANCELADA': '#6c757d',
            }.get(tarea.estado, '#007bff')
            
            eventos.append({
                'id': tarea.id,
                'title': tarea.titulo,
                'start': tarea.fecha_vencimiento.isoformat() if tarea.fecha_vencimiento else None,
                'color': color,
                'url': f'/usuarios/tareas/{tarea.id}/'
            })
        
        return JsonResponse(eventos, safe=False)
    
    return JsonResponse([], safe=False)


@login_required
def estadisticas_dashboard_ajax(request):
    """Obtener estadísticas para el dashboard vía AJAX"""
    usuario = request.user
    
    # Estadísticas básicas
    stats = {
        'tareas_pendientes': usuario.tareas_asignadas.filter(estado='PENDIENTE').count(),
        'tareas_en_progreso': usuario.tareas_asignadas.filter(estado='EN_PROGRESO').count(),
        'tareas_completadas_mes': usuario.tareas_asignadas.filter(
            estado='COMPLETADA',
            fecha_completado__month=timezone.now().month
        ).count(),
        'notificaciones_no_leidas': usuario.notificaciones.filter(leida=False).count(),
    }
    
    return JsonResponse(stats)


# =====================================================
# API REST VIEWSETS
# =====================================================

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.filter(activo=True)
    serializer_class = UsuarioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'tipo_usuario']
    permission_classes = [permissions.IsAuthenticated]


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.filter(activo=True)
    serializer_class = EquipoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    permission_classes = [permissions.IsAuthenticated]


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_creacion', 'estado']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo proyectos donde el usuario es propietario o colaborador"""
        return Proyecto.objects.filter(
            Q(propietario=self.request.user) | Q(colaboradores=self.request.user)
        ).distinct()


class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descripcion', 'etiquetas']
    ordering_fields = ['fecha_creacion', 'fecha_vencimiento', 'prioridad']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo tareas que el usuario puede ver"""
        return Tarea.objects.filter(
            Q(asignado_a=self.request.user) |
            Q(creado_por=self.request.user) |
            Q(es_publica=True) |
            (Q(es_personal=False) & Q(proyecto__colaboradores=self.request.user))
        ).distinct()


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_creacion']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo notificaciones del usuario actual"""
        return self.request.user.notificaciones.all()
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marcar notificación como leída"""
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response({'status': 'ok'})


class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_inicio']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo eventos donde el usuario es organizador o asistente"""
        return Agenda.objects.filter(
            Q(organizador=self.request.user) | Q(asistentes=self.request.user)
        ).distinct()
