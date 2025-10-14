"""
URLs para el sistema de tickets de transporte.
"""
from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_tickets, name='dashboard'),
    
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