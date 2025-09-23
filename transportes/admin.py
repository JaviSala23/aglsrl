"""
Configuración del panel de administración para el módulo de transportes.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TipoCamion, Camion, Chofer, Viaje, TicketBalanza


@admin.register(TipoCamion)
class TipoCamionAdmin(admin.ModelAdmin):
    """Administración de tipos de camión."""
    list_display = ['nombre', 'capacidad_maxima', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'capacidad_maxima')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    """Administración de camiones."""
    list_display = [
        'patente', 
        'cuenta_asociada', 
        'acoplados_display',
        'capacidad_carga',
        'tara',
        'activo'
    ]
    list_filter = ['cuenta_asociada', 'activo']
    search_fields = ['patente', 'acoplado_1', 'acoplado_2']
    ordering = ['patente']
    
    def acoplados_display(self, obj):
        """Muestra los acoplados del camión."""
        acoplados = []
        if obj.acoplado_1:
            acoplados.append(obj.acoplado_1)
        if obj.acoplado_2:
            acoplados.append(obj.acoplado_2)
        return ', '.join(acoplados) if acoplados else 'Sin acoplados'
    acoplados_display.short_description = 'Acoplados'


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    """Administración de choferes."""
    list_display = [
        'legajo',
        'nombre_completo_display',
        'dni',
        'tipo_licencia',
        'estado_display',
        'licencia_status',
        'camion_asignado',
        'activo'
    ]
    list_filter = [
        'estado',
        'tipo_licencia',
        'activo',
        'fecha_vencimiento_licencia',
        'fecha_ingreso'
    ]
    search_fields = ['nombre', 'apellido', 'dni', 'legajo', 'numero_licencia']
    ordering = ['apellido', 'nombre']
    date_hierarchy = 'fecha_ingreso'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'dni', 'fecha_nacimiento', 'telefono', 'email', 'direccion')
        }),
        ('Información Laboral', {
            'fields': ('legajo', 'fecha_ingreso', 'tipo_licencia', 'numero_licencia', 'fecha_vencimiento_licencia')
        }),
        ('Estado y Asignación', {
            'fields': ('estado', 'camion_asignado')
        }),
        ('Contacto de Emergencia', {
            'fields': ('contacto_emergencia_nombre', 'contacto_emergencia_telefono')
        }),
        ('Control', {
            'fields': ('activo', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_alta', 'fecha_modificacion']
    
    def nombre_completo_display(self, obj):
        """Muestra el nombre completo del chofer."""
        return obj.nombre_completo
    nombre_completo_display.short_description = 'Nombre Completo'
    
    def estado_display(self, obj):
        """Muestra el estado con colores."""
        colors = {
            'disponible': 'green',
            'en_viaje': 'blue',
            'descanso': 'orange',
            'vacaciones': 'purple',
            'licencia': 'gray',
            'suspendido': 'red'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'
    
    def licencia_status(self, obj):
        """Muestra el estado de la licencia."""
        if obj.licencia_vencida:
            return format_html('<span style="color: red; font-weight: bold;">❌ Vencida</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ Vigente</span>')
    licencia_status.short_description = 'Licencia'


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    """Administración de viajes."""
    list_display = [
        'numero_viaje',
        'fecha_programada',
        'camion',
        'chofer',
        'ruta_display',
        'cliente',
        'estado_display',
        'peso_carga'
    ]
    list_filter = [
        'estado',
        'tipo_carga',
        'fecha_programada',
        'camion__cuenta_asociada',
        'cliente'
    ]
    search_fields = [
        'numero_viaje',
        'origen',
        'destino',
        'camion__patente',
        'chofer__nombre',
        'chofer__apellido',
        'cliente__nombre_comercial'
    ]
    ordering = ['-fecha_programada']
    date_hierarchy = 'fecha_programada'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_viaje', 'fecha_programada', 'fecha_inicio_real', 'fecha_fin_real')
        }),
        ('Recursos Asignados', {
            'fields': ('camion', 'chofer')
        }),
        ('Ruta', {
            'fields': ('origen', 'destino', 'distancia_km')
        }),
        ('Información de Carga', {
            'fields': ('tipo_carga', 'descripcion_carga', 'peso_estimado', 'peso_real')
        }),
        ('Cliente y Facturación', {
            'fields': ('cliente', 'precio_acordado')
        }),
        ('Estado y Control', {
            'fields': ('estado', 'observaciones')
        }),
        ('Control del Sistema', {
            'fields': ('creado_por',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def ruta_display(self, obj):
        """Muestra la ruta de forma compacta."""
        return f"{obj.origen} → {obj.destino}"
    ruta_display.short_description = 'Ruta'
    
    def estado_display(self, obj):
        """Muestra el estado con colores."""
        colors = {
            'planificado': 'blue',
            'en_curso': 'green',
            'completado': 'gray',
            'cancelado': 'red',
            'demorado': 'orange'
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'
    
    def peso_carga(self, obj):
        """Muestra información del peso."""
        if obj.peso_real:
            return f"{obj.peso_real}t (Real)"
        elif obj.peso_estimado:
            return f"{obj.peso_estimado}t (Est.)"
        return "Sin datos"
    peso_carga.short_description = 'Peso'


@admin.register(TicketBalanza)
class TicketBalanzaAdmin(admin.ModelAdmin):
    """Administración de tickets de balanza."""
    list_display = [
        'numero_ticket',
        'fecha_pesaje',
        'tipo_pesaje',
        'camion',
        'chofer',
        'peso_bruto_display',
        'peso_neto_display',
        'cliente_carga',
        'producto'
    ]
    list_filter = [
        'tipo_pesaje',
        'fecha_pesaje',
        'producto',
        'cliente_carga',
        'camion__cuenta_asociada'
    ]
    search_fields = [
        'numero_ticket',
        'camion__patente',
        'chofer__nombre',
        'chofer__apellido',
        'producto',
        'cliente_carga__nombre_comercial',
        'balanza_operador'
    ]
    ordering = ['-fecha_pesaje']
    date_hierarchy = 'fecha_pesaje'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_ticket', 'fecha_pesaje', 'tipo_pesaje')
        }),
        ('Vehículo y Conductor', {
            'fields': ('camion', 'chofer', 'viaje')
        }),
        ('Datos del Pesaje', {
            'fields': ('peso_bruto', 'peso_tara', 'peso_neto')
        }),
        ('Información de la Carga', {
            'fields': ('producto', 'cliente_carga', 'destino_carga')
        }),
        ('Control', {
            'fields': ('balanza_operador', 'observaciones', 'creado_por')
        }),
    )
    
    readonly_fields = ['peso_neto', 'fecha_creacion']
    
    def peso_bruto_display(self, obj):
        """Muestra el peso bruto formateado."""
        return f"{obj.peso_bruto_toneladas:.2f} t"
    peso_bruto_display.short_description = 'Peso Bruto'
    
    def peso_neto_display(self, obj):
        """Muestra el peso neto formateado."""
        return f"{obj.peso_neto_toneladas:.2f} t"
    peso_neto_display.short_description = 'Peso Neto'
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario que crea el ticket."""
        if not change:  # Solo para nuevos objetos
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
