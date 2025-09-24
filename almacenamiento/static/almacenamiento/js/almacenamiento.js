/* ===== ALMACENAMIENTO MODULE JAVASCRIPT ===== */

document.addEventListener('DOMContentLoaded', function() {
    // Configuración de colores para charts de almacenamiento
    const almacenamientoColors = {
        primary: '#fd7e14',
        secondary: '#e76500',
        light: '#fff3e0',
        dark: '#cc5200',
        gradient: ['#fd7e14', '#e76500']
    };

    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Animaciones suaves para cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Función para formatear números
    function formatNumber(num) {
        return new Intl.NumberFormat('es-AR').format(num);
    }

    // Función para formatear peso
    function formatWeight(kg) {
        if (kg >= 1000) {
            return (kg / 1000).toFixed(1) + ' ton';
        }
        return kg.toFixed(0) + ' kg';
    }

    // Configuración por defecto para Chart.js
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        
        // Colores por defecto para almacenamiento
        Chart.register({
            id: 'almacenamientoDefaults',
            beforeInit: function(chart) {
                if (!chart.options.plugins.colors) {
                    chart.options.plugins.colors = {
                        enabled: true,
                        forceOverride: false
                    };
                }
            }
        });
    }

    // Función para actualizar estadísticas en tiempo real
    function updateStats() {
        // Aquí se pueden agregar llamadas AJAX para actualizar estadísticas
        console.log('Actualizando estadísticas de almacenamiento...');
    }

    // Auto-refresh cada 5 minutos (opcional)
    // setInterval(updateStats, 300000);

    // Manejar filtros de búsqueda
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Implementar lógica de búsqueda en tiempo real si es necesario
            console.log('Buscando:', this.value);
        });
    });

    // Validaciones de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Validaciones personalizadas aquí
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor, complete todos los campos requeridos.');
            }
        });
    });

    console.log('Módulo de Almacenamiento inicializado correctamente');
});