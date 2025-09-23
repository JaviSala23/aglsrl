"""
Configuración del admin para el módulo de agenda.
"""
from django.contrib import admin
from .models import TipoContacto, Contacto, TipoEvento, Evento, Tarea


@admin.register(TipoContacto)
class TipoContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'color', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'empresa', 'telefono_principal', 'email_principal', 'tipo_contacto', 'favorito', 'activo']
    list_filter = ['tipo_contacto', 'favorito', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'apellido', 'empresa', 'email_principal', 'telefono_principal']
    list_editable = ['favorito', 'activo']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'empresa', 'cargo')
        }),
        ('Contacto', {
            'fields': ('telefono_principal', 'telefono_secundario', 'email_principal', 'email_secundario')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'provincia', 'codigo_postal', 'pais')
        }),
        ('Categorización', {
            'fields': ('tipo_contacto', 'cuenta_relacionada')
        }),
        ('Información Adicional', {
            'fields': ('notas', 'fecha_nacimiento', 'sitio_web')
        }),
        ('Control', {
            'fields': ('favorito', 'activo', 'creado_por', 'fecha_creacion', 'fecha_modificacion')
        }),
    )


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'color', 'icono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_inicio', 'fecha_fin', 'tipo_evento', 'prioridad', 'estado', 'creado_por']
    list_filter = ['tipo_evento', 'prioridad', 'estado', 'fecha_inicio', 'todo_el_dia']
    search_fields = ['titulo', 'descripcion', 'ubicacion']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    filter_horizontal = ['contactos']
    date_hierarchy = 'fecha_inicio'


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_vencimiento', 'prioridad', 'estado', 'creado_por', 'esta_vencida']
    list_filter = ['prioridad', 'estado', 'fecha_vencimiento', 'activa']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'esta_vencida']
    date_hierarchy = 'fecha_vencimiento'
