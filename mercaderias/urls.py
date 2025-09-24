from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para API REST
router = DefaultRouter()
router.register(r'granos', views.GranoViewSet)
router.register(r'mercaderias', views.MercaderiaViewSet)

app_name = 'mercaderias'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Módulo de clasificación de calidades
    path('clasificacion/', include('mercaderias.clasificacion.urls')),
    
    # Módulo de granos
    path('granos/', include('mercaderias.granos.urls')),
    path('granos/<int:pk>/', views.grano_detail, name='grano_detail'),
    path('granos/crear/', views.grano_create, name='grano_create'),
    path('granos/<int:pk>/editar/', views.grano_edit, name='grano_edit'),
    path('granos/<int:pk>/eliminar/', views.grano_delete, name='grano_delete'),
    
    # Mercaderías - CRUD Completo
    path('mercaderias/', views.mercaderias_list, name='mercaderias_list'),
    path('mercaderias/<int:pk>/', views.mercaderia_detail, name='mercaderia_detail'),
    path('mercaderias/crear/', views.mercaderia_create, name='mercaderia_create'),
    path('mercaderias/<int:pk>/editar/', views.mercaderia_edit, name='mercaderia_edit'),
    path('mercaderias/<int:pk>/eliminar/', views.mercaderia_delete, name='mercaderia_delete'),
    
    # Stocks - Sistema Avanzado
    path('stocks/', views.stocks_list, name='stocks_list'),
    path('stocks/filtrar/', views.stocks_filter, name='stocks_filter'),
    path('stocks/<int:pk>/', views.stock_detail, name='stock_detail'),
    
    # APIs AJAX
    path('api/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('api/stock-por-grano/', views.api_stock_por_grano, name='api_stock_por_grano'),
    path('api/stock-por-ubicacion/', views.api_stock_por_ubicacion, name='api_stock_por_ubicacion'),
    
    # API REST
    path('api/', include(router.urls)),
]