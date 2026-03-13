from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PerfilUsuario


@login_required
def mi_perfil(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    return render(request, 'usuarios/mi_perfil.html', {'perfil': perfil})
