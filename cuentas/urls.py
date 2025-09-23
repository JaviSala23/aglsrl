"""
URLs para el módulo de cuentas con API versionada.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router principal para la API
router = DefaultRouter()

# Registro de ViewSets maestros (solo lectura)
router.register(r'paises', views.PaisViewSet, basename='pais')
router.register(r'provincias', views.ProvinciaViewSet, basename='provincia')
router.register(r'localidades', views.LocalidadViewSet, basename='localidad')
router.register(r'tipos-documento', views.TipoDocumentoViewSet, basename='tipo-documento')
router.register(r'situaciones-iva', views.SituacionIvaViewSet, basename='situacion-iva')
router.register(r'tipos-cuenta', views.TipoCuentaViewSet, basename='tipo-cuenta')

# Registro de ViewSets principales
router.register(r'cuentas', views.CuentaViewSet, basename='cuenta')
router.register(r'contactos', views.ContactoCuentaViewSet, basename='contacto')
router.register(r'direcciones', views.DireccionViewSet, basename='direccion')

app_name = 'cuentas'

urlpatterns = [
    # ============================================
    # RUTAS WEB (INTERFAZ DE USUARIO)
    # ============================================
    
    # Dashboard y navegación principal
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # CRUD de cuentas - Web
    path('cuentas/', views.ListaCuentasView.as_view(), name='lista_cuentas'),
    path('cuentas/nueva/', views.CrearCuentaView.as_view(), name='crear_cuenta'),
    path('cuentas/<int:pk>/', views.DetalleCuentaView.as_view(), name='ver_cuenta'),
    path('cuentas/<int:pk>/editar/', views.EditarCuentaView.as_view(), name='editar_cuenta'),
    path('cuentas/<int:pk>/eliminar/', views.eliminar_cuenta_view, name='eliminar_cuenta'),
    path('cuentas/<int:pk>/toggle-activo/', views.toggle_cuenta_activo_view, name='toggle_cuenta_activo'),
    
    # Exportación de cuentas
    path('cuentas/exportar/pdf/', views.exportar_cuentas_pdf, name='exportar_cuentas_pdf'),
    path('cuentas/exportar/excel/', views.exportar_cuentas_excel, name='exportar_cuentas_excel'),
    
    # API endpoints adicionales
    path('api/estadisticas/', views.estadisticas_api_view, name='estadisticas_api'),
    
    # AJAX endpoints para filtros en cascada
    path('ajax/provincias/', views.ajax_provincias, name='ajax_provincias'),
    path('ajax/localidades/', views.ajax_localidades, name='ajax_localidades'),
    
    # ============================================
    # RUTAS API REST
    # ============================================
    path('api/v1/', include(router.urls)),
]