"""
URL configuration for agl_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

# Router principal del proyecto
main_router = DefaultRouter()

urlpatterns = [
    # Administración
    path('admin/', admin.site.urls),
    
    # App principal (landing, login, panel)
    path('', include('main.urls')),
    
    # App de cuentas
    path('cuentas/', include('cuentas.urls')),
    
    # App de agenda
    path('agenda/', include('agenda.urls')),
    
    # App de transportes
    path('transportes/', include('transportes.urls')),
    
    # App de mercaderías
    path('mercaderias/', include('mercaderias.urls')),
    
    # App de almacenamiento
    path('almacenamiento/', include('almacenamiento.urls')),
    
    # App de procesamiento/clasificación
    path('procesamiento/', include('procesamiento.urls')),
    
    # App de usuarios y tareas (comentado temporalmente)
    # path('usuarios/', include('usuarios.urls')),
    
    # API principal del proyecto (para futuras apps)
    path('api/', include(main_router.urls)),
    
    # API auth de DRF (login/logout via web)
    path('api-auth/', include('rest_framework.urls')),
]
