// ==========================================
// JAVASCRIPT PARA MÓDULO DE CLASIFICACIÓN
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades del módulo
    initClasificacionModule();
});

function initClasificacionModule() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar validaciones de formularios
    initFormValidations();
    
    // Inicializar calculadora de porcentajes
    initPercentageCalculator();
}

function initFormValidations() {
    // Validar que las cantidades sumen correctamente
    const cantidadInputs = document.querySelectorAll('.cantidad-detalle');
    if (cantidadInputs.length > 0) {
        cantidadInputs.forEach(input => {
            input.addEventListener('input', calculateTotals);
        });
    }
}

function calculateTotals() {
    const cantidadOriginal = parseFloat(document.getElementById('cantidad-original')?.value || 0);
    const cantidadInputs = document.querySelectorAll('.cantidad-detalle');
    let totalRegistrado = 0;
    
    cantidadInputs.forEach(input => {
        const valor = parseFloat(input.value || 0);
        totalRegistrado += valor;
        
        // Calcular porcentaje para este input
        const porcentajeInput = input.parentElement.parentElement.querySelector('.porcentaje-detalle');
        if (porcentajeInput && cantidadOriginal > 0) {
            const porcentaje = (valor / cantidadOriginal * 100).toFixed(2);
            porcentajeInput.value = porcentaje;
        }
    });
    
    // Mostrar total registrado
    const totalElement = document.getElementById('total-registrado');
    if (totalElement) {
        totalElement.textContent = totalRegistrado.toFixed(2);
    }
    
    // Mostrar diferencia
    const diferencia = cantidadOriginal - totalRegistrado;
    const diferenciaElement = document.getElementById('diferencia');
    if (diferenciaElement) {
        diferenciaElement.textContent = diferencia.toFixed(2);
        diferenciaElement.className = diferencia === 0 ? 'text-success' : 'text-warning';
    }
    
    // Mostrar alerta si hay diferencia significativa
    const alertaElement = document.getElementById('alerta-diferencia');
    if (alertaElement) {
        if (Math.abs(diferencia) > 0.01) {
            alertaElement.style.display = 'block';
        } else {
            alertaElement.style.display = 'none';
        }
    }
}

function initPercentageCalculator() {
    // Permitir calcular porcentajes automáticamente
    const porcentajeInputs = document.querySelectorAll('.porcentaje-detalle');
    porcentajeInputs.forEach(input => {
        input.addEventListener('input', function() {
            const cantidadOriginal = parseFloat(document.getElementById('cantidad-original')?.value || 0);
            const porcentaje = parseFloat(this.value || 0);
            
            if (cantidadOriginal > 0 && porcentaje > 0) {
                const cantidad = (cantidadOriginal * porcentaje / 100).toFixed(2);
                const cantidadInput = this.parentElement.parentElement.querySelector('.cantidad-detalle');
                if (cantidadInput) {
                    cantidadInput.value = cantidad;
                    calculateTotals();
                }
            }
        });
    });
}

// Función para agregar nueva fila de detalle
function addDetalleRow() {
    const container = document.getElementById('detalles-container');
    if (!container) return;
    
    const totalForms = document.querySelector('#id_detalles-TOTAL_FORMS');
    const formNum = parseInt(totalForms.value);
    
    const newRow = document.querySelector('.detalle-row:last-child').cloneNode(true);
    
    // Actualizar IDs y nombres de los campos
    newRow.querySelectorAll('input, select, textarea').forEach(field => {
        const name = field.name.replace(/-\d+-/, `-${formNum}-`);
        const id = field.id.replace(/-\d+-/, `-${formNum}-`);
        field.name = name;
        field.id = id;
        field.value = '';
    });
    
    container.appendChild(newRow);
    totalForms.value = formNum + 1;
    
    // Reinicializar eventos
    initFormValidations();
}

// Función para eliminar fila de detalle
function removeDetalleRow(button) {
    const row = button.closest('.detalle-row');
    if (document.querySelectorAll('.detalle-row').length > 1) {
        row.remove();
        calculateTotals();
    }
}

// Función para validar formulario antes de enviar
function validateClasificacionForm() {
    const cantidadOriginal = parseFloat(document.getElementById('cantidad-original')?.value || 0);
    const cantidadInputs = document.querySelectorAll('.cantidad-detalle');
    let totalRegistrado = 0;
    
    cantidadInputs.forEach(input => {
        totalRegistrado += parseFloat(input.value || 0);
    });
    
    const diferencia = Math.abs(cantidadOriginal - totalRegistrado);
    
    if (diferencia > 0.01) {
        return confirm(`Hay una diferencia de ${diferencia.toFixed(2)} kg entre la cantidad original y el total registrado. ¿Desea continuar? Se generará un ticket de ajuste.`);
    }
    
    return true;
}

// Exportar funciones globales
window.addDetalleRow = addDetalleRow;
window.removeDetalleRow = removeDetalleRow;
window.validateClasificacionForm = validateClasificacionForm;