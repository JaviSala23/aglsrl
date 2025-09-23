from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Usuario, Equipo, Proyecto, Tarea, ComentarioTarea, 
    HistorialTarea, Notificacion, Agenda
)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = (
        'username', 'get_full_name', 'email', 'tipo_usuario', 
        'puesto', 'activo', 'date_joined'
    )
    list_filter = ('tipo_usuario', 'activo', 'fecha_ingreso', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'puesto')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': (
                'tipo_usuario', 'telefono', 'celular', 'puesto', 
                'fecha_ingreso', 'activo', 'avatar'
            )
        }),
        ('Preferencias', {
            'fields': ('tema_preferido', 'notificaciones_email', 'notificaciones_sistema')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Nombre Completo'


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'lider', 'activo', 'fecha_creacion', 'cantidad_miembros')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('miembros',)
    
    def cantidad_miembros(self, obj):
        return obj.miembros.count()
    cantidad_miembros.short_description = 'Miembros'


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'propietario', 'estado', 'prioridad', 
        'fecha_inicio', 'fecha_fin_estimada', 'progreso'
    )
    list_filter = ('estado', 'prioridad', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('colaboradores',)
    date_hierarchy = 'fecha_creacion'
    
    def progreso(self, obj):
        porcentaje = obj.progreso_porcentaje()
        color = 'green' if porcentaje >= 75 else 'orange' if porcentaje >= 50 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            porcentaje, color, porcentaje
        )
    progreso.short_description = 'Progreso'


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'asignado_a', 'creado_por', 'estado', 'prioridad', 
        'fecha_vencimiento', 'proyecto', 'esta_vencida_display'
    )
    list_filter = (
        'estado', 'prioridad', 'es_personal', 'es_publica', 
        'fecha_creacion', 'proyecto'
    )
    search_fields = ('titulo', 'descripcion', 'etiquetas')
    date_hierarchy = 'fecha_creacion'
    raw_id_fields = ('creado_por', 'asignado_a', 'proyecto', 'tarea_padre')
    filter_horizontal = ('tareas_dependientes',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'estado', 'prioridad')
        }),
        ('Asignación', {
            'fields': ('creado_por', 'asignado_a', 'proyecto')
        }),
        ('Fechas y Tiempo', {
            'fields': (
                'fecha_vencimiento', 'fecha_inicio_real', 'fecha_completado',
                'tiempo_estimado', 'tiempo_real'
            )
        }),
        ('Organización', {
            'fields': ('etiquetas', 'tarea_padre', 'tareas_dependientes')
        }),
        ('Visibilidad', {
            'fields': ('es_personal', 'es_publica')
        }),
        ('Archivos', {
            'fields': ('archivo_adjunto',)
        }),
    )
    
    def esta_vencida_display(self, obj):
        if obj.esta_vencida():
            return format_html('<span style="color: red;">Vencida</span>')
        return 'No'
    esta_vencida_display.short_description = 'Vencida'


class ComentarioTareaInline(admin.TabularInline):
    model = ComentarioTarea
    extra = 0
    readonly_fields = ('fecha_creacion',)


class HistorialTareaInline(admin.TabularInline):
    model = HistorialTarea
    extra = 0
    readonly_fields = ('fecha',)


# Agregar inlines a TareaAdmin
TareaAdmin.inlines = [ComentarioTareaInline, HistorialTareaInline]


@admin.register(ComentarioTarea)
class ComentarioTareaAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'usuario', 'fecha_creacion', 'es_interno')
    list_filter = ('es_interno', 'fecha_creacion')
    search_fields = ('comentario', 'tarea__titulo')
    date_hierarchy = 'fecha_creacion'


@admin.register(HistorialTarea)
class HistorialTareaAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'usuario', 'accion', 'fecha')
    list_filter = ('accion', 'fecha')
    search_fields = ('descripcion', 'tarea__titulo')
    date_hierarchy = 'fecha'


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'leida', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario__username')
    date_hierarchy = 'fecha_creacion'
    
    actions = ['marcar_como_leida', 'marcar_como_no_leida']
    
    def marcar_como_leida(self, request, queryset):
        queryset.update(leida=True)
    marcar_como_leida.short_description = "Marcar como leída"
    
    def marcar_como_no_leida(self, request, queryset):
        queryset.update(leida=False)
    marcar_como_no_leida.short_description = "Marcar como no leída"


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'organizador', 'tipo', 'fecha_inicio', 
        'fecha_fin', 'ubicacion', 'es_privado'
    )
    list_filter = ('tipo', 'es_privado', 'todo_el_dia', 'fecha_inicio')
    search_fields = ('titulo', 'descripcion', 'ubicacion')
    date_hierarchy = 'fecha_inicio'
    filter_horizontal = ('asistentes',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo')
        }),
        ('Fechas y Hora', {
            'fields': ('fecha_inicio', 'fecha_fin', 'todo_el_dia')
        }),
        ('Ubicación', {
            'fields': ('ubicacion',)
        }),
        ('Participantes', {
            'fields': ('organizador', 'asistentes')
        }),
        ('Configuración', {
            'fields': ('es_privado', 'recordatorio')
        }),
    )
