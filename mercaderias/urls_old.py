from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para API REST
router = DefaultRouter()
# Aquí agregaremos los viewsets cuando los creemos

app_name = 'mercaderias'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Mercaderías
    path('mercaderias/', views.mercaderias_list, name='mercaderias_list'),
    path('mercaderias/<int:pk>/', views.mercaderia_detail, name='mercaderia_detail'),
    
    # Ubicaciones
    path('ubicaciones/', views.ubicaciones_list, name='ubicaciones_list'),
    path('ubicaciones/<int:pk>/', views.ubicacion_detail, name='ubicacion_detail'),
    
    # Stocks
    path('stocks/', views.stocks_list, name='stocks_list'),
    
    # APIs AJAX
    path('api/stock-por-grano/', views.api_stock_por_grano, name='api_stock_por_grano'),
    path('api/stock-por-ubicacion/', views.api_stock_por_ubicacion, name='api_stock_por_ubicacion'),
    path('api/almacenajes/<int:ubicacion_id>/', views.api_almacenajes_por_ubicacion, name='api_almacenajes_por_ubicacion'),
    
    # API REST
    path('api/', include(router.urls)),
]