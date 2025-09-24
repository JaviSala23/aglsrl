from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para API REST
router = DefaultRouter()
# Aquí agregaremos los viewsets cuando los creemos

app_name = 'almacenamiento'

urlpatterns = [
    # Dashboard de almacenamiento
    path('', views.dashboard, name='dashboard'),
    
    # Ubicaciones
    path('ubicaciones/', views.ubicaciones_list, name='ubicaciones_list'),
    path('ubicaciones/crear/', views.crear_ubicacion, name='crear_ubicacion'),
    path('ubicaciones/<int:pk>/', views.ubicacion_detail, name='ubicacion_detail'),
    path('ubicaciones/<int:pk>/editar/', views.editar_ubicacion, name='editar_ubicacion'),
    path('ubicaciones/<int:pk>/eliminar/', views.eliminar_ubicacion, name='eliminar_ubicacion'),
    path('ubicaciones/<int:pk>/toggle-activo/', views.toggle_ubicacion_activo, name='toggle_ubicacion_activo'),
    
    # Almacenajes
    path('almacenajes/', views.almacenajes_list, name='almacenajes_list'),
    path('almacenajes/crear/', views.crear_almacenaje, name='crear_almacenaje'),
    path('almacenajes/<int:pk>/', views.almacenaje_detail, name='almacenaje_detail'),
    path('almacenajes/<int:pk>/editar/', views.editar_almacenaje, name='editar_almacenaje'),
    path('almacenajes/<int:pk>/eliminar/', views.eliminar_almacenaje, name='eliminar_almacenaje'),
    path('almacenajes/<int:pk>/toggle-activo/', views.toggle_almacenaje_activo, name='toggle_almacenaje_activo'),
    
    # Stocks
    path('stocks/', views.stocks_list, name='stocks_list'),
    
    # APIs AJAX
    path('api/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    
    # API REST
    path('api/', include(router.urls)),
]