"""
URLs para el sistema de tickets de transporte.
"""
from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_tickets, name='dashboard'),
    
    # ── BALANZA RÁPIDA PARA ENCARGADOS ───────────────────────────────────────
    path('balanza/', views.ticket_balanza_lista, name='balanza_lista'),
    path('balanza/entrada/', views.ticket_balanza_nuevo, {'tipo': 'entrada'}, name='balanza_entrada'),
    path('balanza/salida/', views.ticket_balanza_nuevo, {'tipo': 'salida'}, name='balanza_salida'),
    path('balanza/<int:pk>/segunda-pesada/', views.ticket_balanza_segunda_pesada, name='balanza_segunda_pesada'),
    path('balanza/cargar-cpe/', views.cargar_cpe, name='cargar_cpe'),

    # Gestión de tickets
    path('lista/', views.lista_tickets, name='lista_tickets'),
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('crear/entrada/', views.crear_ticket_entrada, name='crear_ticket_entrada'),
    path('crear/salida/', views.crear_ticket_salida, name='crear_ticket_salida'),
    path('nuevo/', views.crear_ticket, name='crear_ticket_nuevo'),  # URL limpia sin caché
    path('<int:pk>/', views.detalle_ticket, name='detalle_ticket'),
    
    # Acciones específicas del flujo
    path('<int:pk>/pesos/', views.actualizar_pesos, name='actualizar_pesos'),
    path('<int:pk>/salida/', views.marcar_salida, name='marcar_salida'),
    path('analisis/<int:detalle_id>/', views.realizar_analisis, name='realizar_analisis'),
    
    # Estadísticas
    path('estadisticas/', views.estadisticas_avanzadas, name='estadisticas'),
]
