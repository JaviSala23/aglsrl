"""
URLs para el módulo de transportes.
"""
from django.urls import path
from . import views

app_name = 'transportes'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_transportes, name='dashboard'),
    
    # Camiones
    path('camiones/', views.lista_camiones, name='lista_camiones'),
    path('camiones/nuevo/', views.crear_camion, name='crear_camion'),
    path('camiones/<int:pk>/', views.detalle_camion, name='detalle_camion'),
    path('camiones/<int:pk>/editar/', views.editar_camion, name='editar_camion'),
    
    # Choferes
    path('choferes/', views.lista_choferes, name='lista_choferes'),
    path('choferes/nuevo/', views.crear_chofer, name='crear_chofer'),
    path('choferes/<int:pk>/', views.detalle_chofer, name='detalle_chofer'),
    path('choferes/<int:pk>/editar/', views.editar_chofer, name='editar_chofer'),
    
    # Viajes
    path('viajes/', views.lista_viajes, name='lista_viajes'),
    path('viajes/nuevo/', views.crear_viaje, name='crear_viaje'),
    path('viajes/<int:pk>/', views.detalle_viaje, name='detalle_viaje'),
    path('viajes/<int:pk>/estado/', views.cambiar_estado_viaje, name='cambiar_estado_viaje'),
    
    # Tickets de Balanza
    path('tickets/', views.lista_tickets, name='lista_tickets'),
    path('tickets/nuevo/', views.crear_ticket, name='crear_ticket'),
    path('tickets/<int:pk>/', views.detalle_ticket, name='detalle_ticket'),
    
    # AJAX
    path('ajax/camiones-disponibles/', views.ajax_camiones_disponibles, name='ajax_camiones_disponibles'),
    path('ajax/choferes-disponibles/', views.ajax_choferes_disponibles, name='ajax_choferes_disponibles'),
]