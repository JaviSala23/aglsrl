from django.urls import path
from . import views

app_name = 'granos'

urlpatterns = [
    path('', views.lista_granos, name='lista'),
    path('crear/', views.crear_grano, name='crear'),
    path('<int:id>/', views.detalle_grano, name='detalle'),
    path('<int:id>/editar/', views.editar_grano, name='editar'),
    path('<int:id>/eliminar/', views.eliminar_grano, name='eliminar'),
    path('<int:id>/toggle/', views.toggle_grano_activo, name='toggle_activo'),
]