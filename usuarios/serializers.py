from rest_framework import serializers
from .models import (
    Usuario, Equipo, Proyecto, Tarea, ComentarioTarea,
    HistorialTarea, Notificacion, Agenda
)


class UsuarioSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name_or_username', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'tipo_usuario', 'telefono', 'celular', 'puesto', 'fecha_ingreso',
            'activo', 'avatar', 'tema_preferido', 'notificaciones_email',
            'notificaciones_sistema', 'date_joined'
        ]
        read_only_fields = ['date_joined']
        extra_kwargs = {'password': {'write_only': True}}


class EquipoSerializer(serializers.ModelSerializer):
    lider_nombre = serializers.CharField(source='lider.get_full_name_or_username', read_only=True)
    cantidad_miembros = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipo
        fields = [
            'id', 'nombre', 'descripcion', 'lider', 'lider_nombre',
            'miembros', 'activo', 'fecha_creacion', 'cantidad_miembros'
        ]
    
    def get_cantidad_miembros(self, obj):
        return obj.miembros.count()


class ProyectoSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.get_full_name_or_username', read_only=True)
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)
    progreso = serializers.SerializerMethodField()
    total_tareas = serializers.SerializerMethodField()
    tareas_completadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Proyecto
        fields = [
            'id', 'nombre', 'descripcion', 'estado', 'fecha_inicio',
            'fecha_fin_estimada', 'fecha_fin_real', 'propietario', 'propietario_nombre',
            'colaboradores', 'equipo', 'equipo_nombre', 'prioridad', 'color',
            'fecha_creacion', 'fecha_actualizacion', 'progreso', 'total_tareas',
            'tareas_completadas'
        ]
    
    def get_progreso(self, obj):
        return obj.progreso_porcentaje()
    
    def get_total_tareas(self, obj):
        return obj.tareas.count()
    
    def get_tareas_completadas(self, obj):
        return obj.tareas.filter(estado='COMPLETADA').count()


class TareaSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name_or_username', read_only=True)
    asignado_a_nombre = serializers.CharField(source='asignado_a.get_full_name_or_username', read_only=True)
    proyecto_nombre = serializers.CharField(source='proyecto.nombre', read_only=True)
    esta_vencida = serializers.SerializerMethodField()
    dias_hasta_vencimiento = serializers.SerializerMethodField()
    puede_editar = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarea
        fields = [
            'id', 'titulo', 'descripcion', 'estado', 'prioridad',
            'creado_por', 'creado_por_nombre', 'asignado_a', 'asignado_a_nombre',
            'proyecto', 'proyecto_nombre', 'etiquetas', 'fecha_vencimiento',
            'fecha_inicio_real', 'fecha_completado', 'tiempo_estimado', 'tiempo_real',
            'tarea_padre', 'tareas_dependientes', 'es_personal', 'es_publica',
            'fecha_creacion', 'fecha_actualizacion', 'archivo_adjunto',
            'esta_vencida', 'dias_hasta_vencimiento', 'puede_editar'
        ]
    
    def get_esta_vencida(self, obj):
        return obj.esta_vencida()
    
    def get_dias_hasta_vencimiento(self, obj):
        return obj.dias_hasta_vencimiento()
    
    def get_puede_editar(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.puede_editar(request.user)
        return False


class ComentarioTareaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name_or_username', read_only=True)
    
    class Meta:
        model = ComentarioTarea
        fields = [
            'id', 'tarea', 'usuario', 'usuario_nombre', 'comentario',
            'es_interno', 'fecha_creacion'
        ]


class HistorialTareaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name_or_username', read_only=True)
    
    class Meta:
        model = HistorialTarea
        fields = [
            'id', 'tarea', 'usuario', 'usuario_nombre', 'accion',
            'descripcion', 'fecha'
        ]


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tarea_titulo = serializers.CharField(source='tarea.titulo', read_only=True)
    proyecto_nombre = serializers.CharField(source='proyecto.nombre', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'usuario', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'leida', 'fecha_creacion', 'tarea', 'tarea_titulo',
            'proyecto', 'proyecto_nombre'
        ]


class AgendaSerializer(serializers.ModelSerializer):
    organizador_nombre = serializers.CharField(source='organizador.get_full_name_or_username', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    puede_ver = serializers.SerializerMethodField()
    
    class Meta:
        model = Agenda
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'tipo_display',
            'fecha_inicio', 'fecha_fin', 'todo_el_dia', 'ubicacion',
            'organizador', 'organizador_nombre', 'asistentes', 'es_privado',
            'recordatorio', 'fecha_creacion', 'fecha_actualizacion', 'puede_ver'
        ]
    
    def get_puede_ver(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.puede_ver(request.user)
        return False


# Serializers más simples para selects y listas desplegables
class UsuarioSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name_or_username', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'full_name', 'tipo_usuario']


class ProyectoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id', 'nombre', 'estado', 'color']


class TareaSimpleSerializer(serializers.ModelSerializer):
    asignado_a_nombre = serializers.CharField(source='asignado_a.get_full_name_or_username', read_only=True)
    
    class Meta:
        model = Tarea
        fields = ['id', 'titulo', 'estado', 'prioridad', 'asignado_a_nombre', 'fecha_vencimiento']