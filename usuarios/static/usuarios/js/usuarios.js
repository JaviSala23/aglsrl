/**
 * JavaScript para el módulo de Usuarios y Tareas
 * Funcionalidades: Dashboard interactivo, gestión de tareas, notificaciones
 */

// Configuración global
const USUARIOS_CONFIG = {
    urls: {
        cambiarEstadoTarea: '/usuarios/ajax/cambiar-estado-tarea/',
        obtenerNotificaciones: '/usuarios/ajax/obtener-notificaciones/',
        buscarUsuarios: '/usuarios/ajax/buscar-usuarios/',
        estadisticasDashboard: '/usuarios/ajax/estadisticas-dashboard/',
    },
    refreshInterval: 30000, // 30 segundos
    animationDuration: 300
};

// Estado global de la aplicación
let appState = {
    notificaciones: [],
    tareas: [],
    refreshTimers: {},
    activeModals: []
};

/**
 * ============================================
 * INICIALIZACIÓN
 * ============================================
 */

document.addEventListener('DOMContentLoaded', function() {
    initUsuarios();
});

function initUsuarios() {
    console.log('🚀 Inicializando módulo de Usuarios y Tareas');
    
    // Configurar CSRF token para AJAX
    setupCSRF();
    
    // Inicializar componentes
    initDashboard();
    initNotificaciones();
    initTareas();
    initProyectos();
    initFormularios();
    initTooltips();
    initAnimaciones();
    
    // Configurar auto-refresh
    setupAutoRefresh();
    
    console.log('✅ Módulo de Usuarios inicializado correctamente');
}

/**
 * ============================================
 * CONFIGURACIÓN AJAX Y CSRF
 * ============================================
 */

function setupCSRF() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name="csrf-token"]')?.content;
    
    if (csrfToken) {
        // Configurar jQuery AJAX (si está disponible)
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrfToken);
                    }
                }
            });
        }
        
        // Configurar fetch para todas las peticiones
        window.csrfToken = csrfToken;
    }
}

function fetchWithCSRF(url, options = {}) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': window.csrfToken,
            'Content-Type': 'application/json',
        }
    };
    
    return fetch(url, { ...defaultOptions, ...options });
}

/**
 * ============================================
 * DASHBOARD
 * ============================================
 */

function initDashboard() {
    console.log('📊 Inicializando Dashboard');
    
    // Actualizar estadísticas cada minuto
    updateDashboardStats();
    setInterval(updateDashboardStats, 60000);
    
    // Configurar gráficos si Chart.js está disponible
    if (typeof Chart !== 'undefined') {
        initCharts();
    }
    
    // Configurar accesos rápidos
    setupQuickActions();
}

function updateDashboardStats() {
    fetchWithCSRF(USUARIOS_CONFIG.urls.estadisticasDashboard)
        .then(response => response.json())
        .then(data => {
            updateStatCard('mis-tareas-pendientes', data.mis_tareas_pendientes);
            updateStatCard('mis-tareas-vencidas', data.mis_tareas_vencidas);
            updateStatCard('tareas-creadas-por-mi', data.tareas_creadas_por_mi);
            updateStatCard('notificaciones-no-leidas', data.notificaciones_no_leidas);
        })
        .catch(error => console.error('Error actualizando estadísticas:', error));
}

function updateStatCard(id, value) {
    const element = document.querySelector(`[data-stat="${id}"] .h5`);
    if (element && element.textContent !== value.toString()) {
        // Animación de actualización
        element.style.transform = 'scale(1.1)';
        element.textContent = value;
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
}

function setupQuickActions() {
    // Configurar atajos de teclado
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N = Nueva tarea
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const crearTareaBtn = document.querySelector('[href*="crear_tarea"]');
            if (crearTareaBtn) crearTareaBtn.click();
        }
        
        // Ctrl/Cmd + P = Nuevo proyecto
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            const crearProyectoBtn = document.querySelector('[href*="crear_proyecto"]');
            if (crearProyectoBtn) crearProyectoBtn.click();
        }
    });
}

/**
 * ============================================
 * GESTIÓN DE TAREAS
 * ============================================
 */

function initTareas() {
    console.log('📋 Inicializando gestión de tareas');
    
    // Configurar cambios de estado
    setupTaskStateButtons();
    
    // Configurar filtros
    setupTaskFilters();
    
    // Configurar drag & drop si es necesario
    setupTaskDragDrop();
}

function cambiarEstadoTarea(tareaId, nuevoEstado) {
    const data = {
        tarea_id: tareaId,
        nuevo_estado: nuevoEstado
    };
    
    // Mostrar indicador de carga
    const spinner = createSpinner();
    document.body.appendChild(spinner);
    
    fetchWithCSRF(USUARIOS_CONFIG.urls.cambiarEstadoTarea, {
        method: 'POST',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar UI
            updateTaskUI(tareaId, data.tarea);
            showToast('Estado de tarea actualizado', 'success');
            
            // Actualizar estadísticas
            updateDashboardStats();
        } else {
            showToast(data.error || 'Error al actualizar tarea', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
    })
    .finally(() => {
        document.body.removeChild(spinner);
    });
}

function updateTaskUI(tareaId, tareaData) {
    const tareaElement = document.querySelector(`[data-tarea-id="${tareaId}"]`);
    if (!tareaElement) return;
    
    // Actualizar badge de estado
    const estadoBadge = tareaElement.querySelector('.badge-tarea-estado');
    if (estadoBadge) {
        estadoBadge.className = `badge badge-tarea-${tareaData.estado.toLowerCase()}`;
        estadoBadge.textContent = tareaData.estado_display;
    }
    
    // Agregar animación
    tareaElement.style.transform = 'scale(1.02)';
    tareaElement.style.transition = 'transform 0.2s ease';
    setTimeout(() => {
        tareaElement.style.transform = 'scale(1)';
    }, 200);
}

function setupTaskStateButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-action="cambiar-estado"]')) {
            e.preventDefault();
            const tareaId = e.target.dataset.tareaId;
            const nuevoEstado = e.target.dataset.estado;
            cambiarEstadoTarea(tareaId, nuevoEstado);
        }
    });
}

function setupTaskFilters() {
    const filtros = document.querySelectorAll('[data-filter]');
    filtros.forEach(filtro => {
        filtro.addEventListener('change', function() {
            filterTasks();
        });
    });
}

function filterTasks() {
    const estado = document.querySelector('[data-filter="estado"]')?.value;
    const prioridad = document.querySelector('[data-filter="prioridad"]')?.value;
    const asignado = document.querySelector('[data-filter="asignado"]')?.value;
    
    const tareas = document.querySelectorAll('.tarea-item');
    
    tareas.forEach(tarea => {
        let mostrar = true;
        
        if (estado && tarea.dataset.estado !== estado) mostrar = false;
        if (prioridad && tarea.dataset.prioridad !== prioridad) mostrar = false;
        if (asignado && tarea.dataset.asignado !== asignado) mostrar = false;
        
        tarea.style.display = mostrar ? 'block' : 'none';
    });
}

function setupTaskDragDrop() {
    // Implementar drag & drop para reordenar tareas si es necesario
    // Por ahora dejamos la funcionalidad básica
}

/**
 * ============================================
 * NOTIFICACIONES
 * ============================================
 */

function initNotificaciones() {
    console.log('🔔 Inicializando sistema de notificaciones');
    
    // Cargar notificaciones iniciales
    cargarNotificaciones();
    
    // Configurar auto-refresh
    setInterval(cargarNotificaciones, USUARIOS_CONFIG.refreshInterval);
    
    // Configurar marca como leída
    setupNotificationReaders();
}

function cargarNotificaciones() {
    fetchWithCSRF(USUARIOS_CONFIG.urls.obtenerNotificaciones)
        .then(response => response.json())
        .then(data => {
            appState.notificaciones = data.notificaciones;
            updateNotificationUI(data);
        })
        .catch(error => console.error('Error cargando notificaciones:', error));
}

function updateNotificationUI(data) {
    // Actualizar contador
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = data.no_leidas;
        badge.style.display = data.no_leidas > 0 ? 'block' : 'none';
    }
    
    // Actualizar lista de notificaciones
    const lista = document.querySelector('.notificaciones-lista');
    if (lista) {
        lista.innerHTML = '';
        data.notificaciones.forEach(notif => {
            lista.appendChild(createNotificationElement(notif));
        });
    }
}

function createNotificationElement(notificacion) {
    const element = document.createElement('div');
    element.className = `notificacion-item p-3 border-bottom ${!notificacion.leida ? 'no-leida' : ''}`;
    element.dataset.notifId = notificacion.id;
    
    element.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
                <h6 class="mb-1">${notificacion.titulo}</h6>
                <p class="mb-1 text-muted">${notificacion.mensaje}</p>
                <small class="text-muted">${formatearFecha(notificacion.fecha_creacion)}</small>
            </div>
            ${!notificacion.leida ? 
                `<button class="btn btn-sm btn-outline-primary" onclick="marcarNotificacionLeida(${notificacion.id})">
                    Marcar leída
                </button>` : ''
            }
        </div>
    `;
    
    return element;
}

function marcarNotificacionLeida(notifId) {
    fetchWithCSRF(`/usuarios/notificaciones/${notifId}/leer/`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar UI
            const element = document.querySelector(`[data-notif-id="${notifId}"]`);
            if (element) {
                element.classList.remove('no-leida');
                const button = element.querySelector('button');
                if (button) button.remove();
            }
            
            // Actualizar contador
            cargarNotificaciones();
        }
    })
    .catch(error => console.error('Error:', error));
}

function setupNotificationReaders() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-action="marcar-leida"]')) {
            const notifId = e.target.dataset.notifId;
            marcarNotificacionLeida(notifId);
        }
    });
}

/**
 * ============================================
 * PROYECTOS
 * ============================================
 */

function initProyectos() {
    console.log('📊 Inicializando gestión de proyectos');
    
    // Configurar progress bars animadas
    animateProgressBars();
    
    // Configurar color pickers si existen
    setupColorPickers();
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });
}

function setupColorPickers() {
    const colorPickers = document.querySelectorAll('input[type="color"]');
    colorPickers.forEach(picker => {
        picker.addEventListener('change', function() {
            updateProjectColor(this.value);
        });
    });
}

/**
 * ============================================
 * FORMULARIOS
 * ============================================
 */

function initFormularios() {
    console.log('📝 Inicializando formularios');
    
    // Configurar validación en tiempo real
    setupFormValidation();
    
    // Configurar autocompletado
    setupAutocompletar();
    
    // Configurar drag & drop para archivos
    setupFileUpload();
}

function setupFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const campos = form.querySelectorAll('[required]');
    
    campos.forEach(campo => {
        if (!campo.value.trim()) {
            showFieldError(campo, 'Este campo es requerido');
            isValid = false;
        } else {
            clearFieldError(campo);
        }
    });
    
    return isValid;
}

function showFieldError(campo, mensaje) {
    clearFieldError(campo);
    
    const error = document.createElement('div');
    error.className = 'invalid-feedback d-block';
    error.textContent = mensaje;
    
    campo.classList.add('is-invalid');
    campo.parentNode.appendChild(error);
}

function clearFieldError(campo) {
    campo.classList.remove('is-invalid');
    const error = campo.parentNode.querySelector('.invalid-feedback');
    if (error) error.remove();
}

function setupAutocompletar() {
    const buscadores = document.querySelectorAll('[data-autocomplete="usuarios"]');
    buscadores.forEach(input => {
        let timeout;
        
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                buscarUsuarios(this.value, this);
            }, 300);
        });
    });
}

function buscarUsuarios(query, input) {
    if (query.length < 2) return;
    
    fetchWithCSRF(`${USUARIOS_CONFIG.urls.buscarUsuarios}?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showUserSuggestions(data.usuarios, input);
        })
        .catch(error => console.error('Error buscando usuarios:', error));
}

function showUserSuggestions(usuarios, input) {
    // Remover sugerencias anteriores
    const existingSuggestions = document.querySelector('.user-suggestions');
    if (existingSuggestions) existingSuggestions.remove();
    
    if (usuarios.length === 0) return;
    
    const suggestions = document.createElement('div');
    suggestions.className = 'user-suggestions list-group position-absolute w-100';
    suggestions.style.zIndex = '1000';
    
    usuarios.forEach(usuario => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'list-group-item list-group-item-action';
        item.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="avatar avatar-sm me-2">
                    ${usuario.iniciales}
                </div>
                <div>
                    <div class="fw-bold">${usuario.nombre_completo}</div>
                    <small class="text-muted">${usuario.email}</small>
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            input.value = usuario.nombre_completo;
            input.dataset.userId = usuario.id;
            suggestions.remove();
        });
        
        suggestions.appendChild(item);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestions);
}

function setupFileUpload() {
    const dropZones = document.querySelectorAll('[data-upload]');
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('drop', handleFileDrop);
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files, e.currentTarget);
    }
}

/**
 * ============================================
 * UTILIDADES
 * ============================================
 */

function initTooltips() {
    // Inicializar tooltips de Bootstrap si está disponible
    if (typeof bootstrap !== 'undefined') {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }
}

function initAnimaciones() {
    // Configurar Animate.css si está disponible
    const elements = document.querySelectorAll('.animate__animated');
    
    // Observer para animar elementos al entrar en viewport
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.visibility = 'visible';
                }
            });
        });
        
        elements.forEach(el => {
            observer.observe(el);
            el.style.visibility = 'hidden';
        });
    }
}

function setupAutoRefresh() {
    // Configurar refresh automático solo si la página está visible
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Pausar timers cuando la página no está visible
            Object.values(appState.refreshTimers).forEach(timer => clearInterval(timer));
        } else {
            // Reanudar cuando vuelva a estar visible
            cargarNotificaciones();
            updateDashboardStats();
        }
    });
}

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Contenedor de toasts
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Mostrar toast
    if (typeof bootstrap !== 'undefined') {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    } else {
        toast.classList.add('show');
        setTimeout(() => {
            toast.remove();
        }, duration);
    }
}

function createSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-usuarios position-fixed top-50 start-50 translate-middle';
    spinner.style.zIndex = '9999';
    return spinner;
}

function formatearFecha(fecha) {
    const date = new Date(fecha);
    const now = new Date();
    const diff = now - date;
    
    // Menos de un minuto
    if (diff < 60000) return 'Hace un momento';
    
    // Menos de una hora
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    }
    
    // Menos de un día
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    }
    
    // Más de un día
    return date.toLocaleDateString('es-ES', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Exportar funciones principales para uso global
window.UsuariosJS = {
    cambiarEstadoTarea,
    marcarNotificacionLeida,
    showToast,
    cargarNotificaciones,
    updateDashboardStats
};