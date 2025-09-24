from django.urls import path
from . import views

app_name = 'clasificacion'

urlpatterns = [
    # Panel principal
    path('', views.panel_clasificacion, name='panel'),
    
    # Selección de stock
    path('seleccionar-stock/', views.seleccionar_stock, name='seleccionar_stock'),
    
    # CRUD de clasificaciones
    path('lista/', views.lista_clasificaciones, name='lista_clasificaciones'),
    path('detalle/<int:id>/', views.detalle_clasificacion, name='detalle_clasificacion'),
    path('crear/<int:stock_id>/', views.crear_clasificacion, name='crear_clasificacion'),
    path('editar/<int:id>/', views.editar_clasificacion, name='editar_clasificacion'),
    
    # AJAX endpoints
    path('ajax/stock/<int:stock_id>/', views.ajax_stock_info, name='ajax_stock_info'),
    path('ajax/almacenajes/', views.ajax_almacenajes_por_ubicacion, name='ajax_almacenajes'),
]