from django.contrib import admin
from .models import (
    Grano, Mercaderia, Calidad,
    ClasificacionCalidad, DetalleCalidad, TicketAjuste
)


# ==========================================
# GRANOS Y MERCADERÍAS
# ==========================================

@admin.register(Grano)
class GranoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo']
    ordering = ['nombre']


@admin.register(Mercaderia)
class MercaderiaAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__', 'tipo', 'estado', 'propietario_nombre', 'fecha_ingreso']
    list_filter = ['grano', 'tipo', 'estado', 'fecha_ingreso']
    search_fields = ['grano__nombre', 'propietario_nombre']
    ordering = ['-fecha_ingreso', 'grano__nombre']
    date_hierarchy = 'fecha_ingreso'
    
    fieldsets = (
        ('Información General', {
            'fields': ('grano', 'tipo', 'estado')
        }),
        ('Propietario', {
            'fields': ('propietario_nombre', 'propietario_contacto')
        }),
        ('Características del Grano', {
            'fields': ('humedad_porcentaje', 'proteina_porcentaje', 'cuerpos_extranos_porcentaje', 
                      'granos_danados_porcentaje', 'peso_hectolitro'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_ingreso', 'fecha_analisis', 'fecha_vencimiento')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )


@admin.register(Calidad)
class CalidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'orden_presentacion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo']
    ordering = ['orden_presentacion', 'nombre']
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'codigo', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden_presentacion', 'activo', 'color_hex')
        })
    )


# ==========================================
# CLASIFICACIÓN DE CALIDADES
# ==========================================

class DetalleCalidadInline(admin.TabularInline):
    """Inline para detalles de calidad en clasificación"""
    model = DetalleCalidad
    extra = 1
    fields = ['calidad', 'cantidad_kg', 'porcentaje', 'ubicacion_especifica', 'observaciones']
    readonly_fields = ['porcentaje']


@admin.register(ClasificacionCalidad)
class ClasificacionCalidadAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'fecha_registro', 'stock_origen_info', 'tipo_clasificacion', 
        'estado', 'cantidad_stock_original', 'cantidad_total_registrada', 
        'diferencia_cantidad', 'registrado_por'
    ]
    list_filter = ['estado', 'tipo_clasificacion', 'fecha_registro']
    search_fields = ['codigo', 'stock_origen__mercaderia__grano__nombre', 'registrado_por']
    ordering = ['-fecha_registro', '-fecha_creacion']
    date_hierarchy = 'fecha_registro'
    
    inlines = [DetalleCalidadInline]
    
    readonly_fields = [
        'codigo', 'cantidad_stock_original', 'cantidad_total_registrada',
        'diferencia_cantidad', 'tiene_diferencia', 'porcentaje_total',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'fecha_registro', 'stock_origen', 'tipo_clasificacion')
        }),
        ('Estado y Control', {
            'fields': ('estado', 'registrado_por', 'responsable')
        }),
        ('Cantidades', {
            'fields': (
                'cantidad_stock_original', 'cantidad_total_registrada', 
                'diferencia_cantidad', 'tiene_diferencia', 'porcentaje_total'
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Control de Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    def stock_origen_info(self, obj):
        return f"{obj.stock_origen.mercaderia.grano.nombre} - {obj.stock_origen.cantidad_actual}kg"
    stock_origen_info.short_description = "Stock Origen"
    
    def diferencia_cantidad(self, obj):
        diferencia = obj.diferencia_cantidad
        if abs(diferencia) <= 0.01:
            return "✓ Sin diferencia"
        elif diferencia > 0:
            return f"⚠️ Falta: {diferencia}kg"
        else:
            return f"⚠️ Sobra: {abs(diferencia)}kg"
    diferencia_cantidad.short_description = "Diferencia"
    
    actions = ['marcar_como_verificado', 'generar_tickets_ajuste']
    
    def marcar_como_verificado(self, request, queryset):
        """Marcar clasificaciones seleccionadas como verificadas"""
        registrados = queryset.filter(estado='REGISTRADO')
        count = registrados.update(estado='VERIFICADO')
        self.message_user(request, f"{count} clasificaciones marcadas como verificadas.")
    marcar_como_verificado.short_description = "Marcar como verificado"
    
    def generar_tickets_ajuste(self, request, queryset):
        """Generar tickets de ajuste para clasificaciones con diferencias"""
        from mercaderias.clasificacion.views import crear_ticket_ajuste
        count = 0
        for clasificacion in queryset:
            if clasificacion.tiene_diferencia:
                crear_ticket_ajuste(clasificacion)
                count += 1
        self.message_user(request, f"{count} tickets de ajuste generados.")
    generar_tickets_ajuste.short_description = "Generar tickets de ajuste"


@admin.register(DetalleCalidad)
class DetalleCalidadAdmin(admin.ModelAdmin):
    list_display = [
        'clasificacion', 'calidad', 'cantidad_kg', 'porcentaje', 
        'ubicacion_especifica', 'almacenaje_especifico'
    ]
    list_filter = ['calidad', 'ubicacion_especifica']
    search_fields = ['clasificacion__codigo', 'calidad__nombre']
    ordering = ['-clasificacion__fecha_registro', '-porcentaje']


@admin.register(TicketAjuste)
class TicketAjusteAdmin(admin.ModelAdmin):
    list_display = [
        'numero_ticket', 'fecha_ajuste', 'tipo_ajuste', 'stock_afectado_info',
        'cantidad_ajuste_kg', 'aplicado', 'autorizado_por'
    ]
    list_filter = ['tipo_ajuste', 'aplicado', 'fecha_ajuste']
    search_fields = ['numero_ticket', 'stock_afectado__mercaderia__grano__nombre']
    ordering = ['-fecha_ajuste', '-fecha_creacion']
    date_hierarchy = 'fecha_ajuste'
    
    readonly_fields = [
        'numero_ticket', 'fecha_creacion', 'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('numero_ticket', 'tipo_ajuste', 'fecha_ajuste')
        }),
        ('Stock y Ajuste', {
            'fields': ('stock_afectado', 'cantidad_ajuste_kg', 'motivo')
        }),
        ('Control y Autorización', {
            'fields': ('autorizado_por', 'registrado_por', 'aplicado', 'fecha_aplicacion')
        }),
        ('Origen', {
            'fields': ('clasificacion_origen',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Control de Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    def stock_afectado_info(self, obj):
        return f"{obj.stock_afectado.mercaderia.grano.nombre} - {obj.stock_afectado.cantidad_actual}kg"
    stock_afectado_info.short_description = "Stock Afectado"
    
    actions = ['aplicar_ajustes']
    
    def aplicar_ajustes(self, request, queryset):
        """Marcar tickets como aplicados"""
        from django.utils import timezone
        pendientes = queryset.filter(aplicado=False)
        count = pendientes.update(aplicado=True, fecha_aplicacion=timezone.now())
        self.message_user(request, f"{count} tickets marcados como aplicados.")
    aplicar_ajustes.short_description = "Marcar como aplicados"