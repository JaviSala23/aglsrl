"""
Configuración del Django Admin para el sistema de tickets de transporte.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import TipoMovimiento, EstadoTicket, Ticket, DetalleMercaderia, ComentarioTicket, ArchivoTicket, AnalisisMercaderia


@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'requiere_origen', 'requiere_destinatario', 'activo']
    list_filter = ['activo', 'requiere_origen', 'requiere_destinatario']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']


@admin.register(EstadoTicket)
class EstadoTicketAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'color_badge', 'es_inicial', 'es_final', 'permite_edicion', 'activo']
    list_filter = ['es_inicial', 'es_final', 'permite_edicion', 'activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    
    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            obj.color,
            obj.nombre
        )
    color_badge.short_description = 'Color'


class DetalleMercaderiaInline(admin.TabularInline):
    model = DetalleMercaderia
    extra = 1
    fields = [
        'mercaderia', 'cantidad_kg', 'calidad_clasificacion', 
        'ubicacion_almacenaje', 'analisis_realizado', 'observaciones'
    ]
    readonly_fields = ['analisis_realizado']


class ComentarioTicketInline(admin.TabularInline):
    model = ComentarioTicket
    extra = 0
    readonly_fields = ['autor', 'fecha_comentario']
    fields = ['autor', 'fecha_comentario', 'comentario']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('autor')


class ArchivoTicketInline(admin.TabularInline):
    model = ArchivoTicket
    extra = 0
    readonly_fields = ['subido_por', 'fecha_subida']
    fields = ['archivo', 'descripcion', 'subido_por', 'fecha_subida']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'numero_ticket', 'patente_camion', 'tipo_movimiento_badge', 
        'estado_badge', 'chofer', 'peso_status', 'fecha_creacion', 'creado_por'
    ]
    list_filter = [
        'tipo_movimiento', 'estado', 'fecha_creacion'
    ]
    search_fields = [
        'numero_ticket', 'patente_camion', 'chofer__nombre', 
        'origen__razon_social', 'destinatario__razon_social'
    ]
    readonly_fields = [
        'numero_ticket', 'peso_neto', 'fecha_creacion', 
        'fecha_actualizacion', 'creado_por'
    ]
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_ticket', 'tipo_movimiento', 'estado',
                'patente_camion', 'chofer', 'cuenta_transporte'
            )
        }),
        ('Origen y Destino', {
            'fields': ('origen', 'destinatario')
        }),
        ('Pesos', {
            'fields': (
                ('peso_bruto', 'peso_tara', 'peso_neto'),
            )
        }),
        ('Fechas', {
            'fields': (
                ('fecha_llegada', 'fecha_salida'),
                ('fecha_creacion', 'fecha_actualizacion')
            )
        }),
        ('Control', {
            'fields': ('creado_por', 'observaciones')
        }),
    )
    
    inlines = [DetalleMercaderiaInline, ComentarioTicketInline, ArchivoTicketInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tipo_movimiento', 'estado', 'chofer', 'creado_por',
            'origen', 'destinatario'
        )
    
    def tipo_movimiento_badge(self, obj):
        color = '#28a745' if obj.tipo_movimiento.codigo == 'REC' else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px;">{}</span>',
            color,
            obj.tipo_movimiento.codigo
        )
    tipo_movimiento_badge.short_description = 'Tipo'
    
    def estado_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px;">{}</span>',
            obj.estado.color,
            obj.estado.nombre
        )
    estado_badge.short_description = 'Estado'
    
    def peso_status(self, obj):
        if obj.tiene_pesos_completos:
            return format_html(
                '<span style="color: green;">✓ Completo<br/><small>{} kg</small></span>',
                obj.peso_neto
            )
        else:
            return format_html('<span style="color: orange;">⚠ Pendiente</span>')
    peso_status.short_description = 'Pesos'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es creación
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(DetalleMercaderia)
class DetalleMercaderiaAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_link', 'mercaderia', 'cantidad_kg', 
        'calidad_clasificacion', 'analisis_status'
    ]
    list_filter = ['analisis_realizado', 'mercaderia', 'calidad_clasificacion']
    search_fields = [
        'ticket__numero_ticket', 'ticket__patente_camion', 'mercaderia__nombre'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'ticket', 'mercaderia', 'calidad_clasificacion'
        )
    
    def ticket_link(self, obj):
        url = reverse('admin:tickets_ticket_change', args=[obj.ticket.pk])
        return format_html('<a href="{}">{}</a>', url, obj.ticket.numero_ticket)
    ticket_link.short_description = 'Ticket'
    
    def analisis_status(self, obj):
        if obj.analisis_realizado:
            return format_html('<span style="color: green;">✓ Realizado</span>')
        else:
            return format_html('<span style="color: orange;">⚠ Pendiente</span>')
    analisis_status.short_description = 'Análisis'


@admin.register(AnalisisMercaderia)
class AnalisisMercaderiaAdmin(admin.ModelAdmin):
    list_display = [
        'detalle_mercaderia', 'fecha_analisis', 'analista', 
        'humedad', 'proteina', 'grasa', 'aprobado'
    ]
    list_filter = ['aprobado', 'fecha_analisis', 'analista']
    search_fields = [
        'detalle_mercaderia__ticket__numero_ticket',
        'detalle_mercaderia__mercaderia__nombre'
    ]
    readonly_fields = ['fecha_analisis']
    date_hierarchy = 'fecha_analisis'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'detalle_mercaderia__ticket', 'detalle_mercaderia__mercaderia', 'analista'
        )


@admin.register(ComentarioTicket)
class ComentarioTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'autor', 'fecha_comentario', 'comentario_short']
    list_filter = ['fecha_comentario', 'autor']
    search_fields = ['ticket__numero_ticket', 'comentario', 'autor__username']
    readonly_fields = ['fecha_comentario']
    
    def comentario_short(self, obj):
        return obj.comentario[:50] + '...' if len(obj.comentario) > 50 else obj.comentario
    comentario_short.short_description = 'Comentario'


@admin.register(ArchivoTicket)
class ArchivoTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'descripcion', 'archivo', 'subido_por', 'fecha_subida']
    list_filter = ['fecha_subida', 'subido_por']
    search_fields = ['ticket__numero_ticket', 'descripcion']
    readonly_fields = ['fecha_subida']


# Personalización del sitio admin
admin.site.site_header = "AGL SRL - Administración de Tickets"
admin.site.site_title = "AGL SRL Admin"
admin.site.index_title = "Sistema de Gestión de Tickets de Transporte"