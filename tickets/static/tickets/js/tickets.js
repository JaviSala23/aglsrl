// JavaScript específico para el módulo de tickets

document.addEventListener('DOMContentLoaded', function() {
    console.log('Módulo de tickets cargado correctamente');
    
    // Inicializar funcionalidades específicas de tickets
    initializeTicketModule();
});

function initializeTicketModule() {
    // Configurar efectos hover para tarjetas de movimiento
    setupMovementCardEffects();
    
    // Configurar validaciones de formulario
    setupFormValidations();
}

function setupMovementCardEffects() {
    const movementCards = document.querySelectorAll('.movement-card');
    
    movementCards.forEach(card => {
        // Efecto hover
        card.addEventListener('mouseenter', function() {
            if (!this.classList.contains('selected')) {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('selected')) {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
            }
        });
    });
}

function setupFormValidations() {
    const ticketForm = document.getElementById('ticketForm');
    
    if (ticketForm) {
        ticketForm.addEventListener('submit', function(e) {
            // Validaciones básicas antes de enviar
            if (!validateTicketForm()) {
                e.preventDefault();
            }
        });
    }
}

function validateTicketForm() {
    // Validar que se haya seleccionado un tipo de movimiento
    const tipoMovimiento = document.getElementById('tipo_movimiento');
    
    if (!tipoMovimiento || !tipoMovimiento.value) {
        alert('❌ Por favor selecciona un tipo de movimiento');
        return false;
    }
    
    return true;
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Función para animaciones suaves
function smoothScrollTo(element, offset = 0) {
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (element) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}