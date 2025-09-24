from django.contrib import admin
from .models import (
    Ubicacion, Almacenaje, TipoPresentacion, UnidadMedida,
    PesoUnitarioReferencia, FactorConversion, ReglaAlmacenajePresentacion,
    Stock
)

# ==========================================
# UBICACIONES Y ALMACENAJES
# ==========================================

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'encargado', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'encargado__username', 'encargado__first_name', 'encargado__last_name']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'tipo', 'encargado', 'direccion', 'activo')
        }),
        ('Geolocalización', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )


class AlmacenajeInline(admin.TabularInline):
    model = Almacenaje
    extra = 0
    fields = ['codigo', 'tipo', 'capacidad_kg', 'estado', 'activo']
    
    
@admin.register(Almacenaje)
class AlmacenajeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tipo', 'capacidad_kg', 'estado', 'activo']
    list_filter = ['tipo', 'estado', 'activo', 'ubicacion']
    search_fields = ['codigo', 'ubicacion__nombre']
    ordering = ['ubicacion__nombre', 'codigo']
    
    fieldsets = (
        ('Información General', {
            'fields': ('ubicacion', 'codigo', 'tipo', 'capacidad_kg', 'estado', 'activo')
        }),
        ('Geolocalización', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Información Específica', {
            'fields': ('longitud_metros', 'sentido'),
            'classes': ('collapse',),
            'description': 'Campos específicos para silo bolsa'
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )


# Agregar inline a Ubicacion
UbicacionAdmin.inlines = [AlmacenajeInline]


# ==========================================
# PRESENTACIONES Y UNIDADES
# ==========================================

@admin.register(PesoUnitarioReferencia)
class PesoUnitarioReferenciaAdmin(admin.ModelAdmin):
    list_display = ['presentacion', 'peso_kg']
    list_editable = ['peso_kg']
    ordering = ['presentacion']


@admin.register(FactorConversion)
class FactorConversionAdmin(admin.ModelAdmin):
    list_display = ['unidad_origen', 'unidad_destino', 'factor']
    list_editable = ['factor']
    list_filter = ['unidad_origen', 'unidad_destino']
    ordering = ['unidad_origen', 'unidad_destino']


@admin.register(ReglaAlmacenajePresentacion)
class ReglaAlmacenajePresentacionAdmin(admin.ModelAdmin):
    list_display = ['tipo_almacenaje', 'tipo_presentacion', 'es_compatible']
    list_editable = ['es_compatible']
    list_filter = ['tipo_almacenaje', 'tipo_presentacion', 'es_compatible']
    ordering = ['tipo_almacenaje', 'tipo_presentacion']


# ==========================================
# STOCK
# ==========================================

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['ubicacion', 'almacenaje', 'mercaderia', 'cantidad_kg', 'fecha_actualizacion']
    list_filter = ['ubicacion', 'almacenaje__tipo', 'mercaderia__grano', 'fecha_actualizacion']
    search_fields = ['ubicacion__nombre', 'almacenaje__codigo', 'mercaderia__grano__nombre']
    ordering = ['ubicacion__nombre', 'almacenaje__codigo']
    readonly_fields = ['fecha_actualizacion']
    
    fieldsets = (
        ('Ubicación', {
            'fields': ('ubicacion', 'almacenaje')
        }),
        ('Mercadería', {
            'fields': ('mercaderia',)
        }),
        ('Stock', {
            'fields': ('cantidad_kg', 'fecha_actualizacion')
        })
    )
