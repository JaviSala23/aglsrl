from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Grano
from ..forms import GranoForm

def lista_granos(request):
    """Vista para listar todos los granos"""
    granos_list = Grano.objects.prefetch_related('mercaderias').all().order_by('nombre')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        granos_list = granos_list.filter(
            Q(nombre__icontains=search) |
            Q(codigo__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    # Filtro por tipo (no aplica ya que no hay tipos separados)
    
    # Filtro por estado
    activo_filter = request.GET.get('activo', '')
    if activo_filter:
        granos_list = granos_list.filter(activo=(activo_filter == 'true'))
    
    # Paginación
    paginator = Paginator(granos_list, 10)
    page_number = request.GET.get('page')
    granos = paginator.get_page(page_number)
    
    context = {
        'granos': granos,
        'search': search,
        'activo_filter': activo_filter,
        'total_granos': granos_list.count(),
    }
    
    return render(request, 'mercaderias/granos/lista_granos.html', context)

def crear_grano(request):
    """Vista para crear un nuevo grano"""
    if request.method == 'POST':
        form = GranoForm(request.POST)
        if form.is_valid():
            grano = form.save()
            messages.success(request, f'Grano "{grano.nombre}" creado exitosamente.')
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Grano "{grano.nombre}" creado exitosamente.',
                    'grano_id': grano.id,
                    'grano_nombre': grano.nombre
                })
            
            return redirect('mercaderias:granos:lista')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = GranoForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Grano',
        'submit_text': 'Crear Grano'
    }
    
    return render(request, 'mercaderias/granos/crear_grano.html', context)

def editar_grano(request, id):
    """Vista para editar un grano existente"""
    grano = get_object_or_404(Grano, id=id)
    
    if request.method == 'POST':
        form = GranoForm(request.POST, instance=grano)
        if form.is_valid():
            grano = form.save()
            messages.success(request, f'Grano "{grano.nombre}" actualizado exitosamente.')
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Grano "{grano.nombre}" actualizado exitosamente.'
                })
            
            return redirect('mercaderias:granos:lista')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = GranoForm(instance=grano)
    
    context = {
        'form': form,
        'grano': grano,
        'title': f'Editar Grano: {grano.nombre}',
        'submit_text': 'Actualizar Grano'
    }
    
    return render(request, 'mercaderias/granos/crear_grano.html', context)

def detalle_grano(request, id):
    """Vista para ver los detalles de un grano"""
    grano = get_object_or_404(Grano, id=id)
    
    # Obtener estadísticas del grano
    total_mercaderias = grano.mercaderias.count()
    mercaderias_activas = grano.mercaderias.filter(estado='ACTIVO').count()
    
    context = {
        'grano': grano,
        'total_mercaderias': total_mercaderias,
        'mercaderias_activas': mercaderias_activas,
    }
    
    return render(request, 'mercaderias/granos/detalle_grano.html', context)

def eliminar_grano(request, id):
    """Vista para eliminar un grano"""
    grano = get_object_or_404(Grano, id=id)
    
    if request.method == 'POST':
        # Verificar si el grano tiene mercaderías asociadas
        if grano.mercaderias.exists():
            messages.error(request, f'No se puede eliminar el grano "{grano.nombre}" porque tiene mercaderías asociadas.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'No se puede eliminar el grano "{grano.nombre}" porque tiene mercaderías asociadas.'
                })
        else:
            nombre_grano = grano.nombre
            grano.delete()
            messages.success(request, f'Grano "{nombre_grano}" eliminado exitosamente.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Grano "{nombre_grano}" eliminado exitosamente.'
                })
        
        return redirect('mercaderias:granos:lista')
    
    context = {
        'grano': grano,
        'total_mercaderias': grano.mercaderias.count(),
    }
    
    return render(request, 'mercaderias/granos/eliminar_grano.html', context)

def toggle_grano_activo(request, id):
    """Vista AJAX para activar/desactivar un grano"""
    if request.method == 'POST':
        grano = get_object_or_404(Grano, id=id)
        grano.activo = not grano.activo
        grano.save()
        
        estado_texto = "activado" if grano.activo else "desactivado"
        messages.success(request, f'Grano "{grano.nombre}" {estado_texto} exitosamente.')
        
        return JsonResponse({
            'success': True,
            'activo': grano.activo,
            'message': f'Grano "{grano.nombre}" {estado_texto} exitosamente.'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})