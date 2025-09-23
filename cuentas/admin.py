"""
Configuración avanzada del admin para el módulo de cuentas.
Incluye inlines, filtros personalizados, acciones en lote y optimizaciones.
"""
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    pais, provincia, localidad, tipo_documento, situacionIva, tipo_cuenta,
    cuenta, contacto_cuenta, direccion
)


# ===============================
# ADMIN CONFIGURACIONES MAESTRAS
# ===============================

@admin.register(pais)
class PaisAdmin(admin.ModelAdmin):
    """Administración de países."""
    list_display = ['id_pais', 'nombre', 'cantidad_provincias']
    search_fields = ['nombre']
    ordering = ['nombre']
    
    def cantidad_provincias(self, obj):
        """Mostrar cantidad de provincias por país."""
        return obj.provincia_set.count()
    cantidad_provincias.short_description = 'Provincias'


@admin.register(provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    """Administración de provincias."""
    list_display = ['id_provincia', 'nombre_provincia', 'codigo_provincia', 'pais_nombre', 'cantidad_localidades']
    list_filter = ['pais_idpais']
    search_fields = ['nombre_provincia', 'codigo_provincia']
    ordering = ['nombre_provincia']
    
    def pais_nombre(self, obj):
        """Mostrar nombre del país."""
        return obj.pais_idpais.nombre if obj.pais_idpais else '-'
    pais_nombre.short_description = 'País'
    
    def cantidad_localidades(self, obj):
        """Mostrar cantidad de localidades por provincia."""
        return obj.localidad_set.count()
    cantidad_localidades.short_description = 'Localidades'


@admin.register(localidad)
class LocalidadAdmin(admin.ModelAdmin):
    """Administración de localidades."""
    list_display = ['id_localidad', 'nombre_localidad', 'cp_localidad', 'provincia_nombre', 'pais_nombre']
    list_filter = ['provincia_id_provincia__pais_idpais', 'provincia_id_provincia']
    search_fields = ['nombre_localidad', 'cp_localidad']
    ordering = ['nombre_localidad']
    
    def provincia_nombre(self, obj):
        """Mostrar nombre de la provincia."""
        return obj.provincia_id_provincia.nombre_provincia if obj.provincia_id_provincia else '-'
    provincia_nombre.short_description = 'Provincia'
    
    def pais_nombre(self, obj):
        """Mostrar nombre del país."""
        if obj.provincia_id_provincia and obj.provincia_id_provincia.pais_idpais:
            return obj.provincia_id_provincia.pais_idpais.nombre
        return '-'
    pais_nombre.short_description = 'País'


@admin.register(tipo_documento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    """Administración de tipos de documento."""
    list_display = ['idtipo_documento', 'descripcion', 'cod_afip', 'cantidad_cuentas']
    search_fields = ['descripcion']
    ordering = ['descripcion']
    
    def cantidad_cuentas(self, obj):
        """Mostrar cantidad de cuentas por tipo de documento."""
        return obj.cuenta_set.count()
    cantidad_cuentas.short_description = 'Cuentas'


@admin.register(situacionIva)
class SituacionIvaAdmin(admin.ModelAdmin):
    """Administración de situaciones de IVA."""
    list_display = ['idsituacionIva', 'descripcion', 'reducida', 'codigo_afip', 'cantidad_cuentas']
    search_fields = ['descripcion', 'reducida']
    list_filter = ['codigo_afip']
    ordering = ['descripcion']
    
    def cantidad_cuentas(self, obj):
        """Mostrar cantidad de cuentas por situación de IVA."""
        return obj.cuenta_set.count()
    cantidad_cuentas.short_description = 'Cuentas'


@admin.register(tipo_cuenta)
class TipoCuentaAdmin(admin.ModelAdmin):
    """Administración de tipos de cuenta."""
    list_display = ['id_tipo_cuenta', 'descripcion', 'cantidad_cuentas']
    search_fields = ['descripcion']
    ordering = ['descripcion']
    
    def cantidad_cuentas(self, obj):
        """Mostrar cantidad de cuentas por tipo."""
        return obj.cuenta_set.count()
    cantidad_cuentas.short_description = 'Cuentas'


# ===============================
# INLINES PARA CUENTAS
# ===============================

class ContactoCuentaInline(admin.TabularInline):
    """Inline para contactos de cuenta."""
    model = contacto_cuenta
    fields = ['nombre', 'cargo', 'email', 'telefono', 'celular', 'activo']
    extra = 0
    classes = ['collapse']


class DireccionInline(admin.TabularInline):
    """Inline para direcciones de cuenta."""
    model = direccion
    fields = ['etiqueta', 'calle', 'numero', 'localidad_idlocalidad', 'es_principal']
    extra = 0
    classes = ['collapse']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Optimizar consultas en el selector de localidad."""
        if db_field.name == "localidad_idlocalidad":
            kwargs["queryset"] = localidad.objects.select_related(
                'provincia_id_provincia__pais_idpais'
            ).order_by('nombre_localidad')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ===============================
# ADMIN PRINCIPAL DE CUENTAS
# ===============================

@admin.register(cuenta)
class CuentaAdmin(admin.ModelAdmin):
    """Administración avanzada de cuentas."""
    
    # Configuración de listado
    list_display = [
        'id_cuenta', 'razon_social_link', 'nombre_fantasia', 
        'tipo_cuenta_badge', 'numero_documento', 'situacion_iva_badge',
        'contactos_count', 'direcciones_count', 'estado_badge', 'fecha_alta'
    ]
    
    list_filter = [
        'activo', 'tipo_cuenta_id_tipo_cuenta', 'situacionIva_idsituacionIva',
        'tipo_documento_idtipo_documento', 'fecha_alta', 'provincia_idprovincia'
    ]
    
    search_fields = [
        'razon_social', 'nombre_fantasia', 'numero_documento', 
        'email_cuenta', 'telefono_cuenta', 'celular_cuenta'
    ]
    
    # Configuración de formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'nombre_fantasia', 'activo')
        }),
        ('Identificación', {
            'fields': ('tipo_documento_idtipo_documento', 'numero_documento')
        }),
        ('Clasificación', {
            'fields': ('tipo_cuenta_id_tipo_cuenta', 'situacionIva_idsituacionIva')
        }),
        ('Ubicación', {
            'fields': ('direccion_cuenta', 'pais_id', 'provincia_idprovincia', 'localidad_idlocalidad'),
            'classes': ['collapse']
        }),
        ('Contacto', {
            'fields': ('telefono_cuenta', 'celular_cuenta', 'email_cuenta'),
            'classes': ['collapse']
        }),
        ('Fechas', {
            'fields': ('fecha_alta', 'fecha_baja'),
            'classes': ['collapse']
        })
    )
    
    readonly_fields = ['fecha_alta']
    date_hierarchy = 'fecha_alta'
    ordering = ['-id_cuenta']
    
    # Inlines
    inlines = [ContactoCuentaInline, DireccionInline]
    
    # Optimización de consultas
    def get_queryset(self, request):
        """Optimizar consultas con select_related y annotations."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'tipo_cuenta_id_tipo_cuenta',
            'situacionIva_idsituacionIva',
            'tipo_documento_idtipo_documento'
        ).annotate(
            contactos_count=Count('contactos', distinct=True),
            direcciones_count=Count('direcciones', distinct=True)
        )
    
    # Acciones personalizadas
    actions = ['activar_cuentas', 'desactivar_cuentas', 'exportar_a_csv']
    
    def activar_cuentas(self, request, queryset):
        """Activar cuentas seleccionadas."""
        updated = queryset.update(activo=True, fecha_baja=None)
        self.message_user(
            request, 
            f'{updated} cuenta(s) activada(s) exitosamente.'
        )
    activar_cuentas.short_description = "Activar cuentas seleccionadas"
    
    def desactivar_cuentas(self, request, queryset):
        """Desactivar cuentas seleccionadas."""
        from django.utils import timezone
        
        updated = queryset.update(activo=False, fecha_baja=timezone.now().date())
        self.message_user(
            request, 
            f'{updated} cuenta(s) desactivada(s) exitosamente.'
        )
    desactivar_cuentas.short_description = "Desactivar cuentas seleccionadas"
    
    def exportar_a_csv(self, request, queryset):
        """Exportar cuentas seleccionadas a CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cuentas.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Razón Social', 'Nombre Fantasía', 'Documento', 
            'Email', 'Teléfono', 'Estado'
        ])
        
        for cuenta_obj in queryset:
            writer.writerow([
                cuenta_obj.id_cuenta,
                cuenta_obj.razon_social,
                cuenta_obj.nombre_fantasia or '',
                cuenta_obj.numero_documento,
                cuenta_obj.email_cuenta or '',
                cuenta_obj.telefono_cuenta or '',
                'Activo' if cuenta_obj.activo else 'Inactivo'
            ])
        
        return response
    exportar_a_csv.short_description = "Exportar a CSV"
    
    # Métodos para campos personalizados del listado
    def razon_social_link(self, obj):
        """Mostrar razón social como enlace al detalle."""
        url = reverse('admin:cuentas_cuenta_change', args=[obj.id_cuenta])
        return format_html('<a href="{}">{}</a>', url, obj.razon_social)
    razon_social_link.short_description = 'Razón Social'
    razon_social_link.admin_order_field = 'razon_social'
    
    def tipo_cuenta_badge(self, obj):
        """Mostrar tipo de cuenta como badge."""
        if obj.tipo_cuenta_id_tipo_cuenta:
            desc = obj.tipo_cuenta_id_tipo_cuenta.descripcion
            return format_html(
                '<span style="background-color: #007cba; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">{}</span>',
                desc
            )
        return '-'
    tipo_cuenta_badge.short_description = 'Tipo'
    tipo_cuenta_badge.admin_order_field = 'tipo_cuenta_id_tipo_cuenta__descripcion'
    
    def situacion_iva_badge(self, obj):
        """Mostrar situación de IVA como badge."""
        if obj.situacionIva_idsituacionIva:
            desc = obj.situacionIva_idsituacionIva.reducida or obj.situacionIva_idsituacionIva.descripcion
            color = '#28a745' if 'RI' in desc else '#6c757d'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">{}</span>',
                color, desc
            )
        return '-'
    situacion_iva_badge.short_description = 'IVA'
    situacion_iva_badge.admin_order_field = 'situacionIva_idsituacionIva__descripcion'
    
    def estado_badge(self, obj):
        """Mostrar estado como badge."""
        if obj.activo:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">●&nbsp;Activo</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">●&nbsp;Inactivo</span>'
            )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'activo'
    
    def contactos_count(self, obj):
        """Mostrar cantidad de contactos."""
        count = getattr(obj, 'contactos_count', obj.contactos.count())
        if count > 0:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 2px 5px; '
                'border-radius: 10px; font-size: 10px;">{}</span>', 
                count
            )
        return '-'
    contactos_count.short_description = 'Contactos'
    contactos_count.admin_order_field = 'contactos_count'
    
    def direcciones_count(self, obj):
        """Mostrar cantidad de direcciones."""
        count = getattr(obj, 'direcciones_count', obj.direcciones.count())
        if count > 0:
            return format_html(
                '<span style="background-color: #fd7e14; color: white; padding: 2px 5px; '
                'border-radius: 10px; font-size: 10px;">{}</span>', 
                count
            )
        return '-'
    direcciones_count.short_description = 'Direcciones'
    direcciones_count.admin_order_field = 'direcciones_count'


# ===============================
# ADMIN PARA CONTACTOS Y DIRECCIONES
# ===============================

@admin.register(contacto_cuenta)
class ContactoCuentaAdmin(admin.ModelAdmin):
    """Administración de contactos de cuenta."""
    
    list_display = ['id_contacto', 'nombre', 'cargo', 'cuenta_link', 'email', 'telefono', 'estado_badge']
    list_filter = ['activo', 'cargo']
    search_fields = ['nombre', 'cargo', 'email', 'telefono', 'cuenta_id__razon_social']
    ordering = ['-id_contacto']
    
    def get_queryset(self, request):
        """Optimizar consultas."""
        return super().get_queryset(request).select_related('cuenta_id')
    
    def cuenta_link(self, obj):
        """Mostrar cuenta como enlace."""
        if obj.cuenta_id:
            url = reverse('admin:cuentas_cuenta_change', args=[obj.cuenta_id.id_cuenta])
            return format_html('<a href="{}">{}</a>', url, obj.cuenta_id.razon_social)
        return '-'
    cuenta_link.short_description = 'Cuenta'
    
    def estado_badge(self, obj):
        """Mostrar estado como badge."""
        if obj.activo:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">●&nbsp;Activo</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">●&nbsp;Inactivo</span>'
            )
    estado_badge.short_description = 'Estado'


@admin.register(direccion)
class DireccionAdmin(admin.ModelAdmin):
    """Administración de direcciones."""
    
    list_display = ['id_direccion', 'cuenta_link', 'etiqueta', 'direccion_completa', 'es_principal_badge']
    list_filter = ['es_principal', 'provincia_idprovincia', 'localidad_idlocalidad']
    search_fields = ['etiqueta', 'calle', 'cuenta_id__razon_social']
    ordering = ['-id_direccion']
    
    def get_queryset(self, request):
        """Optimizar consultas."""
        return super().get_queryset(request).select_related(
            'cuenta_id', 'provincia_idprovincia', 'localidad_idlocalidad'
        )
    
    def cuenta_link(self, obj):
        """Mostrar cuenta como enlace."""
        if obj.cuenta_id:
            url = reverse('admin:cuentas_cuenta_change', args=[obj.cuenta_id.id_cuenta])
            return format_html('<a href="{}">{}</a>', url, obj.cuenta_id.razon_social)
        return '-'
    cuenta_link.short_description = 'Cuenta'
    
    def direccion_completa(self, obj):
        """Mostrar dirección completa."""
        partes = [obj.calle]
        if obj.numero:
            partes.append(obj.numero)
        if obj.localidad_idlocalidad:
            partes.append(obj.localidad_idlocalidad.nombre_localidad)
        return ' '.join(partes)
    direccion_completa.short_description = 'Dirección'
    
    def es_principal_badge(self, obj):
        """Mostrar si es principal como badge."""
        if obj.es_principal:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 6px; '
                'border-radius: 3px; font-size: 11px;">★&nbsp;Principal</span>'
            )
        return '-'
    es_principal_badge.short_description = 'Principal'
