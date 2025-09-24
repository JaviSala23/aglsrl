from django.contrib import admin
from .models import (
    TipoGrano, CalidadGrado, Mercaderia,
    Ubicacion, Almacenaje, TipoPresentacion, UnidadMedida,
    PesoUnitarioReferencia, FactorConversion, ReglaAlmacenajePresentacion,
    Stock
)

# ==========================================
# GRANOS Y MERCADERÍAS
# ==========================================

@admin.register(TipoGrano)
class TipoGranoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'codigo')
    ordering = ('nombre',)


@admin.register(CalidadGrado)
class CalidadGradoAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'codigo', 'activo')
    list_filter = ('activo',)
    search_fields = ('descripcion', 'codigo')
    ordering = ('descripcion',)


class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    readonly_fields = ('fecha_actualizacion',)


@admin.register(Mercaderia)
class MercaderiaAdmin(admin.ModelAdmin):
    list_display = ('grano', 'calidad_grado', 'cantidad_kg', 'activo', 'fecha_ingreso')
    list_filter = ('activo', 'grano', 'calidad_grado', 'fecha_ingreso')
    search_fields = ('grano__nombre', 'calidad_grado__descripcion', 'observaciones')
    ordering = ('-fecha_ingreso',)
    readonly_fields = ('fecha_ingreso', 'fecha_modificacion')
    inlines = [StockInline]


# ==========================================
# UBICACIONES Y ALMACENAJES
# ==========================================

class AlmacenajeInline(admin.TabularInline):
    model = Almacenaje
    extra = 0
    fields = ('tipo', 'codigo', 'capacidad_kg', 'estado', 'activo')


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'encargado_nombre', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre', 'encargado_nombre', 'direccion')
    ordering = ('nombre',)
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'tipo', 'encargado_nombre', 'activo')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'latitud', 'longitud')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )
    inlines = [AlmacenajeInline]


@admin.register(Almacenaje)
class AlmacenajeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'ubicacion', 'tipo', 'capacidad_kg', 'estado', 'activo')
    list_filter = ('tipo', 'estado', 'activo', 'ubicacion')
    search_fields = ('codigo', 'ubicacion__nombre', 'observaciones')
    ordering = ('ubicacion__nombre', 'codigo')
    fieldsets = (
        ('Información General', {
            'fields': ('ubicacion', 'tipo', 'codigo', 'capacidad_kg', 'estado', 'activo')
        }),
        ('Ubicación Específica', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Silo Bolsa (opcional)', {
            'fields': ('longitud_metros', 'sentido'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        })
    )


# ==========================================
# CONFIGURACIONES
# ==========================================

@admin.register(PesoUnitarioReferencia)
class PesoUnitarioReferenciaAdmin(admin.ModelAdmin):
    list_display = ('presentacion', 'peso_kg')
    ordering = ('presentacion',)


@admin.register(FactorConversion)
class FactorConversionAdmin(admin.ModelAdmin):
    list_display = ('unidad_origen', 'unidad_destino', 'factor')
    ordering = ('unidad_origen', 'unidad_destino')


@admin.register(ReglaAlmacenajePresentacion)
class ReglaAlmacenajePresentacionAdmin(admin.ModelAdmin):
    list_display = ('tipo_almacenaje', 'tipo_presentacion', 'es_compatible')
    list_filter = ('tipo_almacenaje', 'es_compatible')
    ordering = ('tipo_almacenaje', 'tipo_presentacion')


# ==========================================
# STOCK
# ==========================================

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ubicacion', 'almacenaje', 'mercaderia_grano', 'cantidad_kg', 'fecha_actualizacion')
    list_filter = ('ubicacion', 'almacenaje__tipo', 'mercaderia__grano', 'fecha_actualizacion')
    search_fields = ('ubicacion__nombre', 'almacenaje__codigo', 'mercaderia__grano__nombre')
    ordering = ('-fecha_actualizacion',)
    readonly_fields = ('fecha_actualizacion',)
    
    def mercaderia_grano(self, obj):
        return obj.mercaderia.grano.nombre
    mercaderia_grano.short_description = 'Grano'
