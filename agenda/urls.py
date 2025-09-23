"""
URLs para el módulo de agenda y contactos.
"""
from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    # Dashboard
    path('', views.DashboardAgendaView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardAgendaView.as_view(), name='dashboard_explicit'),
    
    # Contactos
    path('contactos/', views.ListaContactosView.as_view(), name='lista_contactos'),
    path('contactos/nuevo/', views.CrearContactoView.as_view(), name='crear_contacto'),
    path('contactos/<int:pk>/', views.DetalleContactoView.as_view(), name='detalle_contacto'),
    path('contactos/<int:pk>/editar/', views.EditarContactoView.as_view(), name='editar_contacto'),
    path('contactos/<int:pk>/eliminar/', views.eliminar_contacto_view, name='eliminar_contacto'),
    path('contactos/<int:pk>/favorito/', views.toggle_favorito_view, name='toggle_favorito'),
    
    # Eventos
    path('eventos/', views.ListaEventosView.as_view(), name='lista_eventos'),
    path('eventos/nuevo/', views.CrearEventoView.as_view(), name='crear_evento'),
    path('eventos/<int:pk>/', views.DetalleEventoView.as_view(), name='detalle_evento'),
    path('eventos/<int:pk>/editar/', views.EditarEventoView.as_view(), name='editar_evento'),
    path('eventos/<int:pk>/eliminar/', views.eliminar_evento_view, name='eliminar_evento'),
    
    # Calendario
    path('calendario/', views.AgendaCalendarioView.as_view(), name='calendario'),
    
    # Tareas
    path('tareas/', views.ListaTareasView.as_view(), name='lista_tareas'),
    path('tareas/nueva/', views.CrearTareaView.as_view(), name='crear_tarea'),
    path('tareas/kanban/', views.TareasKanbanView.as_view(), name='tareas_kanban'),
    path('tareas/<int:pk>/', views.DetalleTareaView.as_view(), name='detalle_tarea'),
    path('tareas/<int:pk>/editar/', views.EditarTareaView.as_view(), name='editar_tarea'),
    path('tareas/<int:pk>/eliminar/', views.eliminar_tarea_view, name='eliminar_tarea'),
    path('tareas/<int:pk>/completar/', views.toggle_completar_tarea_view, name='toggle_completar_tarea'),
    path('tareas/<int:tarea_id>/comentario/', views.agregar_comentario_tarea_view, name='agregar_comentario_tarea'),
    path('actualizar-estado-tarea-kanban/<int:tarea_id>/', views.actualizar_estado_tarea_kanban, name='actualizar_estado_tarea_kanban'),
    path('asignaciones/<int:asignacion_id>/responder/', views.responder_asignacion_tarea_view, name='responder_asignacion'),
    # Chat
    path('chat/rooms/', views.chat_list_rooms, name='chat_list_rooms'),
    path('chat/create_private/', views.chat_create_private, name='chat_create_private'),
    path('chat/search_users/', views.chat_search_users, name='chat_search_users'),
    path('chat/<int:room_id>/messages/', views.chat_get_messages, name='chat_get_messages'),
    path('chat/<int:room_id>/send/', views.chat_send_message, name='chat_send_message'),
    path('chat/<int:room_id>/add_members/', views.chat_add_members, name='chat_add_members'),
    path('chat/<int:room_id>/close/', views.chat_close_room, name='chat_close_room'),
    path('chat/unread_count/', views.chat_unread_count, name='chat_unread_count'),
    path('chat/mark_read/', views.chat_mark_read, name='chat_mark_read'),
    
    # APIs
    path('api/eventos/', views.eventos_api_view, name='api_eventos'),
    path('api/estadisticas/', views.estadisticas_api_view, name='api_estadisticas'),
    path('api/cuenta/<int:cuenta_id>/', views.obtener_cuenta_info, name='obtener_cuenta_info'),
]