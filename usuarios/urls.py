from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'usuarios'

# Router para DRF
router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'equipos', views.EquipoViewSet)
router.register(r'proyectos', views.ProyectoViewSet)
router.register(r'tareas', views.TareaViewSet)
router.register(r'notificaciones', views.NotificacionViewSet)
router.register(r'agenda', views.AgendaViewSet)

urlpatterns = [
    # Dashboard principal de usuarios/tareas
    path('', views.dashboard_usuarios, name='dashboard'),
    
    # Gestión de tareas
    path('tareas/', views.lista_tareas, name='lista_tareas'),
    path('tareas/crear/', views.crear_tarea, name='crear_tarea'),
    path('tareas/<int:pk>/', views.detalle_tarea, name='detalle_tarea'),
    path('tareas/<int:pk>/editar/', views.editar_tarea, name='editar_tarea'),
    path('tareas/<int:pk>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),
    path('tareas/<int:pk>/completar/', views.completar_tarea, name='completar_tarea'),
    
    # Mis tareas (vista personal)
    path('mis-tareas/', views.mis_tareas, name='mis_tareas'),
    
    # Proyectos
    path('proyectos/', views.lista_proyectos, name='lista_proyectos'),
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/<int:pk>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyectos/<int:pk>/editar/', views.editar_proyecto, name='editar_proyecto'),
    
    # Agenda
    path('agenda/', views.agenda_calendario, name='agenda'),
    path('agenda/crear/', views.crear_evento, name='crear_evento'),
    path('agenda/<int:pk>/', views.detalle_evento, name='detalle_evento'),
    
    # Equipos
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('equipos/<int:pk>/', views.detalle_equipo, name='detalle_equipo'),
    
    # Notificaciones
    path('notificaciones/', views.lista_notificaciones, name='notificaciones'),
    path('notificaciones/<int:pk>/marcar-leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    
    # Perfil de usuario
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # API REST
    path('api/', include(router.urls)),
    
    # AJAX endpoints
    path('ajax/cambiar-estado-tarea/', views.cambiar_estado_tarea_ajax, name='cambiar_estado_tarea_ajax'),
    path('ajax/obtener-tareas-calendario/', views.obtener_tareas_calendario, name='obtener_tareas_calendario'),
    path('ajax/estadisticas-dashboard/', views.estadisticas_dashboard_ajax, name='estadisticas_dashboard_ajax'),
]