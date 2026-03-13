"""
Decoradores de control de acceso por rol para AGL SRL.

Uso:
    @requiere_administrador
    def mi_vista(request): ...

    @requiere_encargado_o_admin
    def mi_vista(request): ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def _obtener_tipo_usuario(user):
    """Devuelve el tipo_usuario del perfil, o None si no tiene perfil."""
    try:
        return user.perfil.tipo_usuario
    except Exception:
        return None


def requiere_administrador(view_func):
    """Solo ADMINISTRADOR y GERENCIA pueden acceder."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('main:login')
        tipo = _obtener_tipo_usuario(request.user)
        if tipo not in ('ADMINISTRADOR', 'GERENCIA') and not request.user.is_superuser:
            messages.error(request, 'No tenés permiso para acceder a esta sección.')
            return redirect('tickets:balanza_lista')
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_encargado_o_admin(view_func):
    """ENCARGADO, ADMINISTRADOR y GERENCIA pueden acceder."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('main:login')
        tipo = _obtener_tipo_usuario(request.user)
        if tipo not in ('ENCARGADO', 'ADMINISTRADOR', 'GERENCIA') and not request.user.is_superuser:
            messages.error(request, 'No tenés permiso para acceder a esta sección.')
            return redirect('main:panel')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_planta_usuario(user):
    """
    Devuelve la Ubicacion asignada a un encargado, o None si es admin.
    Los admins y superusuarios NO tienen restricción de planta.
    """
    if user.is_superuser:
        return None
    try:
        perfil = user.perfil
        if perfil.tipo_usuario in ('ADMINISTRADOR', 'GERENCIA'):
            return None
        return perfil.planta  # puede ser None si el encargado no tiene planta asignada aún
    except Exception:
        return None


def es_administrador(user):
    """Retorna True si el usuario tiene rol de administrador o gerencia."""
    if user.is_superuser:
        return True
    try:
        return user.perfil.tipo_usuario in ('ADMINISTRADOR', 'GERENCIA')
    except Exception:
        return False
