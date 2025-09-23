"""
URLs para la app principal del sistema.
"""
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Landing page
    path('', views.landing_page_view, name='landing'),
    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    
    # Panel principal de navegación
    path('panel/', views.MainPanelView.as_view(), name='panel'),
    
    # URLs para gestión de usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:user_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
]