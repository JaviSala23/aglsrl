"""
Vistas principales del sistema - Landing, Login y Panel Principal.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.contrib import messages
from django.db.models import Q
from .forms import RegistroUsuarioForm, EditarUsuarioForm


def landing_page_view(request):
    """Vista de la landing page principal."""
    return render(request, 'main/landing.html')


def login_view(request):
    """Vista de login del sistema."""
    if request.user.is_authenticated:
        return redirect('main:panel')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                return redirect('main:panel')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor completa todos los campos.')
    
    return render(request, 'main/login.html')


class MainPanelView(LoginRequiredMixin, TemplateView):
    """Vista del panel principal de navegación."""
    
    template_name = 'main/panel.html'
    login_url = 'main:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Importar aquí para evitar circular imports
        from cuentas.models import cuenta
        from django.contrib.auth.models import User
        
        # Estadísticas básicas para mostrar en el panel
        context['total_cuentas'] = cuenta.objects.count()
        context['cuentas_activas'] = cuenta.objects.filter(activo=True).count()
        
        # Estadísticas de usuarios
        context['total_usuarios'] = User.objects.count()
        context['usuarios_activos'] = User.objects.filter(is_active=True).count()
        
        # Estadísticas de transportes
        try:
            from transportes.models import Camion, Chofer
            context['total_camiones'] = Camion.objects.filter(activo=True).count()
            context['total_choferes'] = Chofer.objects.filter(activo=True).count()
        except ImportError:
            # El módulo de transportes no está disponible
            context['total_camiones'] = 0
            context['total_choferes'] = 0
        
        # Información del usuario
        context['usuario'] = self.request.user
        
        return context


@login_required
def logout_view(request):
    """Vista de logout."""
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('main:login')


def registro_view(request):
    """Vista para registrar nuevos usuarios."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'Usuario {user.username} creado exitosamente. Ya puede iniciar sesión.'
            )
            return redirect('main:login')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'main/registro.html', {'form': form})


@login_required
def lista_usuarios(request):
    """Vista para listar usuarios con búsqueda."""
    query = request.GET.get('q', '')
    usuarios = User.objects.all()
    
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    usuarios = usuarios.order_by('date_joined')
    
    context = {
        'usuarios': usuarios,
        'query': query,
        'total_usuarios': User.objects.count(),
        'usuarios_activos': User.objects.filter(is_active=True).count(),
    }
    return render(request, 'main/usuarios/lista.html', context)


@login_required
def detalle_usuario(request, user_id):
    """Vista para ver detalles de un usuario."""
    usuario = get_object_or_404(User, id=user_id)
    
    # Estadísticas del usuario
    tareas_asignadas = usuario.tareas_asignadas.count()
    tareas_creadas = usuario.tarea_set.count()
    
    context = {
        'usuario': usuario,
        'tareas_asignadas': tareas_asignadas,
        'tareas_creadas': tareas_creadas,
    }
    return render(request, 'main/usuarios/detalle.html', context)


@login_required
def editar_usuario(request, user_id):
    """Vista para editar un usuario."""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
            return redirect('main:detalle_usuario', user_id=usuario.id)
    else:
        form = EditarUsuarioForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
    }
    return render(request, 'main/usuarios/editar.html', context)


@login_required
def eliminar_usuario(request, user_id):
    """Vista para eliminar un usuario."""
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        if usuario != request.user:  # No permitir auto-eliminación
            username = usuario.username
            usuario.delete()
            messages.success(request, f'Usuario {username} eliminado exitosamente.')
        else:
            messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('main:lista_usuarios')
    
    context = {
        'usuario': usuario,
    }
    return render(request, 'main/usuarios/eliminar.html', context)
