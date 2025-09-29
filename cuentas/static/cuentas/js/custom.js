// ============================================
// AGL SRL - Sistema de Gestión
// Custom JavaScript Functions
// ============================================

const AGL = {
    config: {
        apiUrl: '/cuentas/api/v1/',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value,
        timeoutDuration: 30000,
        animationDuration: 300
    },

    // ============================================
    // Utility Functions
    // ============================================
    utils: {},

    // ============================================
    // API Functions
    // ============================================
    api: {},

    // ============================================
    // UI Functions
    // ============================================
    ui: {},

    // ============================================
    // Form Functions
    // ============================================
    forms: {},

    // ============================================
    // Table Functions
    // ============================================
    tables: {}
};

// ============================================
// Utility Functions Implementation
// ============================================

AGL.utils = {
    /**
     * Show loading state
     */
    showLoading: function(element, text = 'Cargando...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const originalContent = element.innerHTML;
            element.setAttribute('data-original-content', originalContent);
            element.innerHTML = `
                <div class="d-flex align-items-center">
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
     * Hide loading state
     */
    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const originalContent = element.getAttribute('data-original-content');
            if (originalContent) {
                element.innerHTML = originalContent;
                element.removeAttribute('data-original-content');
            }
            element.disabled = false;
        }
    },

    /**
     * Format CUIT/DNI
     */
    formatCuitDni: function(value) {
        // Remove all non-digits
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
        
        if (value.length === 8 || value.length === 11) {
            return true;
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
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }
};

// ============================================
// API Functions Implementation
// ============================================

AGL.api = {
    /**
     * Make API request
     */
    request: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': AGL.config.csrfToken
            }
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
};

// ============================================
// UI Functions Implementation
// ============================================

AGL.ui = {
    /**
     * Show success message
     */
    showSuccess: function(title, text) {
        // Implementation would depend on your notification system
        // For now, using console.log
        console.log(`✅ ${title}: ${text}`);
    },

    /**
     * Show error message
     */
    showError: function(title, text) {
        // Implementation would depend on your notification system
        // For now, using console.error
        console.error(`❌ ${title}: ${text}`);
    },

    /**
     * Show confirmation dialog
     */
    confirm: async function(title, text, confirmText = 'Confirmar', cancelText = 'Cancelar') {
        return new Promise((resolve) => {
            const result = window.confirm(`${title}\n\n${text}`);
            resolve({ isConfirmed: result });
        });
    }
};

// ============================================
// Form Functions Implementation
// ============================================

AGL.forms = {
    /**
     * Initialize form validation
     */
    initValidation: function(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        });
    }
};

// ============================================
// Table Functions Implementation
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
                const column = header.dataset.column;
                const currentSort = header.dataset.sort || 'asc';
                const newSort = currentSort === 'asc' ? 'desc' : 'asc';

                // Reset all headers
                headers.forEach(h => h.removeAttribute('data-sort'));
                
                // Set current header
                header.dataset.sort = newSort;

                this.sortTable(tableId, column, newSort === 'asc');
            });
        });
    },

    /**
     * Sort table
     */
    sortTable: function(tableId, column, isAscending) {
        const table = document.getElementById(tableId);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

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
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});

// Export for use in other scripts
window.AGL = AGL;