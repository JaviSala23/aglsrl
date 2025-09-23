/**
 * AGL SRL - Custom JavaScript Functions
 * Sistema de Gestión de Cuentas
 */

// ============================================
// Global Configuration
// ============================================

const AGL = {
    config: {
        apiUrl: '/cuentas/api/v1/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value,
        timeoutDuration: 30000,
        animationDuration: 300
    },
    
    // Common functions
    utils: {},
    
    // API functions
    api: {},
    
    // UI functions
    ui: {},
    
    // Form functions
    forms: {},
    
    // Table functions
    tables: {}
};

// ============================================
// Utility Functions
// ============================================

AGL.utils = {
    /**
     * Show loading spinner on element
     */
    showLoading: function(element, text = 'Cargando...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const originalContent = element.innerHTML;
            element.dataset.originalContent = originalContent;
            element.innerHTML = `
                <div class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    ${text}
                </div>
            `;
            element.disabled = true;
        }
    },
    
    /**
     * Hide loading spinner and restore content
     */
    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element && element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            element.disabled = false;
            delete element.dataset.originalContent;
        }
    },
    
    /**
     * Format CUIT/DNI number
     */
    formatCuitDni: function(value) {
        // Remove all non-numeric characters
        value = value.replace(/\D/g, '');
        
        if (value.length === 11) {
            // Format as CUIT: XX-XXXXXXXX-X
            return value.replace(/(\d{2})(\d{8})(\d{1})/, '$1-$2-$3');
        } else if (value.length === 8) {
            // Format as DNI: XX.XXX.XXX
            return value.replace(/(\d{2})(\d{3})(\d{3})/, '$1.$2.$3');
        }
        
        return value;
    },
    
    /**
     * Validate CUIT/DNI
     */
    validateCuitDni: function(value) {
        value = value.replace(/\D/g, '');
        
        if (value.length === 8) {
            // DNI validation (basic)
            return /^\d{8}$/.test(value);
        } else if (value.length === 11) {
            // CUIT validation (basic)
            return /^\d{11}$/.test(value);
        }
        
        return false;
    },
    
    /**
     * Debounce function
     */
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },
    
    /**
     * Get cookie value
     */
    getCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};

// ============================================
// API Functions
// ============================================

AGL.api = {
    /**
     * Make API request
     */
    request: async function(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': AGL.utils.getCookie('csrftoken') || AGL.config.csrfToken
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(`${AGL.config.apiUrl}${endpoint}`, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    },
    
    /**
     * Get cuentas list
     */
    getCuentas: async function(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `cuentas/?${queryString}` : 'cuentas/';
        return await this.request(endpoint);
    },
    
    /**
     * Get cuenta by ID
     */
    getCuenta: async function(id) {
        return await this.request(`cuentas/${id}/`);
    },
    
    /**
     * Create cuenta
     */
    createCuenta: async function(data) {
        return await this.request('cuentas/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * Update cuenta
     */
    updateCuenta: async function(id, data) {
        return await this.request(`cuentas/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * Delete cuenta
     */
    deleteCuenta: async function(id) {
        return await this.request(`cuentas/${id}/`, {
            method: 'DELETE'
        });
    },
    
    /**
     * Get statistics
     */
    getEstadisticas: async function() {
        return await this.request('cuentas/estadisticas/');
    }
};

// ============================================
// UI Functions
// ============================================

AGL.ui = {
    /**
     * Show success toast
     */
    showSuccess: function(title, text = '') {
        return Swal.fire({
            icon: 'success',
            title: title,
            text: text,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
    },
    
    /**
     * Show error toast
     */
    showError: function(title, text = '') {
        return Swal.fire({
            icon: 'error',
            title: title,
            text: text,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 5000,
            timerProgressBar: true
        });
    },
    
    /**
     * Show warning toast
     */
    showWarning: function(title, text = '') {
        return Swal.fire({
            icon: 'warning',
            title: title,
            text: text,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 4000,
            timerProgressBar: true
        });
    },
    
    /**
     * Show info toast
     */
    showInfo: function(title, text = '') {
        return Swal.fire({
            icon: 'info',
            title: title,
            text: text,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
    },
    
    /**
     * Show confirmation dialog
     */
    confirm: function(title, text, confirmText = 'Confirmar', cancelText = 'Cancelar') {
        return Swal.fire({
            title: title,
            text: text,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: confirmText,
            cancelButtonText: cancelText,
            reverseButtons: true
        });
    },
    
    /**
     * Show loading dialog
     */
    showLoading: function(title = 'Procesando...', text = 'Por favor espere') {
        return Swal.fire({
            title: title,
            text: text,
            allowOutsideClick: false,
            allowEscapeKey: false,
            allowEnterKey: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
    },
    
    /**
     * Update table row
     */
    updateTableRow: function(tableId, rowId, data) {
        const table = document.getElementById(tableId);
        const row = table.querySelector(`tr[data-id="${rowId}"]`);
        
        if (row) {
            // Update row content based on data
            // This would be customized based on table structure
            console.log('Updating row:', rowId, data);
        }
    }
};

// ============================================
// Form Functions
// ============================================

AGL.forms = {
    /**
     * Initialize form validations
     */
    initValidation: function(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        // Custom validation rules
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateField);
            input.addEventListener('input', this.clearValidation);
        });
        
        // CUIT/DNI formatting
        const cuitDniInputs = form.querySelectorAll('input[name*="cuit"], input[name*="dni"]');
        cuitDniInputs.forEach(input => {
            input.addEventListener('input', this.formatCuitDniInput);
        });
        
        // Form submission
        form.addEventListener('submit', this.handleSubmit);
    },
    
    /**
     * Validate individual field
     */
    validateField: function(event) {
        const field = event.target;
        const value = field.value.trim();
        
        // Clear previous validation
        field.classList.remove('is-valid', 'is-invalid');
        
        // Required validation
        if (field.hasAttribute('required') && !value) {
            field.classList.add('is-invalid');
            return false;
        }
        
        // CUIT/DNI validation
        if (field.name.includes('cuit') || field.name.includes('dni')) {
            if (value && !AGL.utils.validateCuitDni(value)) {
                field.classList.add('is-invalid');
                return false;
            }
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                field.classList.add('is-invalid');
                return false;
            }
        }
        
        // If we get here, field is valid
        if (value) {
            field.classList.add('is-valid');
        }
        
        return true;
    },
    
    /**
     * Clear field validation
     */
    clearValidation: function(event) {
        const field = event.target;
        field.classList.remove('is-invalid');
        
        if (field.value.trim()) {
            AGL.forms.validateField(event);
        } else {
            field.classList.remove('is-valid');
        }
    },
    
    /**
     * Format CUIT/DNI input
     */
    formatCuitDniInput: function(event) {
        const field = event.target;
        const cursorPosition = field.selectionStart;
        const oldValue = field.value;
        const newValue = AGL.utils.formatCuitDni(field.value);
        
        field.value = newValue;
        
        // Restore cursor position
        const newCursorPosition = cursorPosition + (newValue.length - oldValue.length);
        field.setSelectionRange(newCursorPosition, newCursorPosition);
    },
    
    /**
     * Handle form submission
     */
    handleSubmit: async function(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Validate all fields
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            const fieldEvent = { target: input };
            if (!AGL.forms.validateField(fieldEvent)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            AGL.ui.showError('Error de validación', 'Por favor corrige los errores en el formulario');
            return;
        }
        
        // Show loading state
        AGL.utils.showLoading(submitBtn);
        
        try {
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Submit via API or standard form submission
            if (form.dataset.apiSubmit === 'true') {
                // API submission
                const endpoint = form.dataset.endpoint || 'cuentas/';
                const method = form.dataset.method || 'POST';
                
                const response = await AGL.api.request(endpoint, {
                    method: method,
                    body: JSON.stringify(data)
                });
                
                AGL.ui.showSuccess('¡Éxito!', 'Los datos se guardaron correctamente');
                
                // Redirect if specified
                if (form.dataset.redirectUrl) {
                    setTimeout(() => {
                        window.location.href = form.dataset.redirectUrl;
                    }, 1500);
                }
            } else {
                // Standard form submission
                form.submit();
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            AGL.ui.showError('Error', 'Ocurrió un error al guardar los datos');
        } finally {
            AGL.utils.hideLoading(submitBtn);
        }
    },
    
    /**
     * Reset form
     */
    reset: function(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
            form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
                field.classList.remove('is-valid', 'is-invalid');
            });
        }
    }
};

// ============================================
// Table Functions
// ============================================

AGL.tables = {
    /**
     * Initialize data table
     */
    init: function(tableId, options = {}) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        // Add search functionality
        this.addSearch(tableId);
        
        // Add sorting
        this.addSorting(tableId);
        
        // Add row actions
        this.addRowActions(tableId);
    },
    
    /**
     * Add search functionality
     */
    addSearch: function(tableId) {
        const searchInput = document.querySelector(`#${tableId}-search`);
        if (!searchInput) return;
        
        const searchFunction = AGL.utils.debounce((event) => {
            const searchTerm = event.target.value.toLowerCase();
            const table = document.getElementById(tableId);
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300);
        
        searchInput.addEventListener('input', searchFunction);
    },
    
    /**
     * Add sorting functionality
     */
    addSorting: function(tableId) {
        const table = document.getElementById(tableId);
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(tableId, header.dataset.sortable);
            });
        });
    },
    
    /**
     * Sort table by column
     */
    sortTable: function(tableId, column) {
        const table = document.getElementById(tableId);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isAscending = table.dataset.sortDirection !== 'asc';
        table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`[data-column="${column}"]`)?.textContent || '';
            const bValue = b.querySelector(`[data-column="${column}"]`)?.textContent || '';
            
            if (isAscending) {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    },
    
    /**
     * Add row actions
     */
    addRowActions: function(tableId) {
        const table = document.getElementById(tableId);
        const actionButtons = table.querySelectorAll('[data-action]');
        
        actionButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const action = button.dataset.action;
                const id = button.dataset.id;
                
                this.handleRowAction(action, id, button);
            });
        });
    },
    
    /**
     * Handle row actions
     */
    handleRowAction: async function(action, id, button) {
        switch (action) {
            case 'delete':
                const result = await AGL.ui.confirm(
                    '¿Eliminar cuenta?',
                    'Esta acción no se puede deshacer',
                    'Sí, eliminar',
                    'Cancelar'
                );
                
                if (result.isConfirmed) {
                    try {
                        await AGL.api.deleteCuenta(id);
                        const row = button.closest('tr');
                        row.remove();
                        AGL.ui.showSuccess('¡Eliminado!', 'La cuenta se eliminó correctamente');
                    } catch (error) {
                        AGL.ui.showError('Error', 'No se pudo eliminar la cuenta');
                    }
                }
                break;
                
            case 'toggle-status':
                try {
                    const cuenta = await AGL.api.getCuenta(id);
                    const newStatus = !cuenta.activo;
                    
                    await AGL.api.updateCuenta(id, { activo: newStatus });
                    
                    // Update button and row
                    const statusBadge = button.closest('tr').querySelector('.status-badge');
                    if (statusBadge) {
                        statusBadge.textContent = newStatus ? 'Activo' : 'Inactivo';
                        statusBadge.className = `badge ${newStatus ? 'bg-success' : 'bg-danger'} status-badge`;
                    }
                    
                    AGL.ui.showSuccess('¡Actualizado!', 'El estado se cambió correctamente');
                } catch (error) {
                    AGL.ui.showError('Error', 'No se pudo cambiar el estado');
                }
                break;
        }
    }
};

// ============================================
// Document Ready
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize forms
    document.querySelectorAll('form[data-agl-form]').forEach(form => {
        AGL.forms.initValidation(form.id);
    });
    
    // Initialize tables
    document.querySelectorAll('table[data-agl-table]').forEach(table => {
        AGL.tables.init(table.id);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    console.log('🚀 AGL SRL System initialized successfully!');
});

// ============================================
// Global Error Handling
// ============================================

window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // Optionally show user-friendly error message
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    // Optionally show user-friendly error message
});

// Export for use in other scripts
window.AGL = AGL;