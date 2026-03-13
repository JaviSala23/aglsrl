def perfil_usuario(request):
    """Expone el perfil del usuario autenticado a todos los templates."""
    if not request.user.is_authenticated:
        return {'perfil': None}
    try:
        return {'perfil': request.user.perfil}
    except Exception:
        return {'perfil': None}
