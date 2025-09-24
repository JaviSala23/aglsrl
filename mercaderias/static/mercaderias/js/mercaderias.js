// JavaScript para el módulo de Mercaderías

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-submit de formularios de filtro con delay
    const filterForms = document.querySelectorAll('form[method="get"]');
    filterForms.forEach(form => {
        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', function() {
                // Auto-submit con un pequeño delay para mejor UX
                setTimeout(() => {
                    form.submit();
                }, 150);
            });
        });
    });

    // Búsqueda en tiempo real con debounce
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        let timeoutId;
        input.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                if (input.value.length >= 3 || input.value.length === 0) {
                    input.form.submit();
                }
            }, 500);
        });
    });

    // Animaciones para tarjetas estadísticas
    const statsCards = document.querySelectorAll('.stats-card');
    statsCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Actualizar gráficos del dashboard
    updateDashboardCharts();

    // Contador animado para números grandes
    animateCounters();

    // Confirmación para acciones destructivas
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres realizar esta acción?')) {
                e.preventDefault();
            }
        });
    });
});

// Función para actualizar gráficos del dashboard
function updateDashboardCharts() {
    // Solo ejecutar en la página del dashboard
    if (!document.getElementById('stockPorGranoChart')) return;

    // Los gráficos se cargan desde el template usando las APIs
    // Esta función puede extenderse para actualizaciones dinámicas
}

// Función para animar contadores
function animateCounters() {
    const counters = document.querySelectorAll('.h4, .h5');
    counters.forEach(counter => {
        const text = counter.textContent;
        const number = parseFloat(text.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(number) && number > 0) {
            animateValue(counter, 0, number, 1000);
        }
    });
}

// Función auxiliar para animar valores numéricos
function animateValue(element, start, end, duration) {
    const originalText = element.textContent;
    const increment = (end - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        
        // Mantener el formato original
        const newText = originalText.replace(/[\d,.-]+/, Math.floor(current).toLocaleString());
        element.textContent = newText;
    }, 16);
}

// Función para cargar almacenajes por ubicación (para futuros formularios)
function loadAlmacenajesByUbicacion(ubicacionId, targetSelectId) {
    if (!ubicacionId) {
        document.getElementById(targetSelectId).innerHTML = '<option value="">Seleccione primero una ubicación</option>';
        return;
    }

    fetch(`/mercaderias/api/almacenajes/${ubicacionId}/`)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById(targetSelectId);
            select.innerHTML = '<option value="">Seleccione un almacenaje</option>';
            
            data.almacenajes.forEach(almacenaje => {
                const option = document.createElement('option');
                option.value = almacenaje.id;
                option.textContent = `${almacenaje.codigo} (${almacenaje.tipo})`;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading almacenajes:', error);
            const select = document.getElementById(targetSelectId);
            select.innerHTML = '<option value="">Error cargando almacenajes</option>';
        });
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'info') {
    // Crear el elemento toast si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${type === 'success' ? 'check-circle text-success' : type === 'error' ? 'exclamation-circle text-danger' : 'info-circle text-info'} me-2"></i>
                <strong class="me-auto">Sistema de Mercaderías</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    // Remover el toast del DOM después de que se oculte
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Función para formatear números
function formatNumber(num, decimals = 0) {
    return parseFloat(num).toLocaleString('es-AR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Función para convertir KG a TN
function kgToTn(kg, decimals = 1) {
    return formatNumber(kg / 1000, decimals);
}

// Exportar funciones para uso global
window.MercaderiasJS = {
    loadAlmacenajesByUbicacion,
    showToast,
    formatNumber,
    kgToTn
};