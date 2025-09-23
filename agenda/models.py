"""
Modelos para el módulo de agenda y contactos.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from cuentas.models import cuenta


class TipoContacto(models.Model):
    """Tipos de contacto: Personal, Profesional, Cliente, Proveedor, etc."""
    id_tipo_contacto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(max_length=200, blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Color en formato hexadecimal')
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Contacto'
        verbose_name_plural = 'Tipos de Contacto'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Contacto(models.Model):
    """Modelo principal para contactos de la agenda."""
    id_contacto = models.AutoField(primary_key=True)
    
    # Información básica
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    empresa = models.CharField(max_length=150, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    
    # Información de contacto
    telefono_principal = models.CharField(max_length=20, blank=True)
    telefono_secundario = models.CharField(max_length=20, blank=True)
    email_principal = models.EmailField(blank=True)
    email_secundario = models.EmailField(blank=True)
    
    # Dirección
    direccion = models.TextField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    pais = models.CharField(max_length=100, default='Argentina')
    
    # Categorización
    tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.PROTECT)
    cuenta_relacionada = models.ForeignKey(
        cuenta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text='Cuenta del sistema relacionada con este contacto'
    )
    
    # Información adicional
    notas = models.TextField(blank=True, help_text='Notas adicionales sobre el contacto')
    sitio_web = models.URLField(blank=True)
    
    # Control
    favorito = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['nombre', 'apellido']),
            models.Index(fields=['email_principal']),
            models.Index(fields=['telefono_principal']),
            models.Index(fields=['tipo_contacto']),
        ]
    
    def __str__(self):
        if self.apellido:
            return f"{self.apellido}, {self.nombre}"
        return self.nombre
    
    @property
    def nombre_completo(self):
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre
    
    @property
    def iniciales(self):
        iniciales = self.nombre[0].upper() if self.nombre else ''
        if self.apellido:
            iniciales += self.apellido[0].upper()
        return iniciales


class TipoEvento(models.Model):
    """Tipos de eventos para la agenda."""
    id_tipo_evento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(max_length=200, blank=True)
    color = models.CharField(max_length=7, default='#28a745', help_text='Color en formato hexadecimal')
    icono = models.CharField(max_length=50, default='bi-calendar-event', help_text='Clase de icono Bootstrap')
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Evento'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Evento(models.Model):
    """Modelo para eventos de la agenda."""
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('pospuesto', 'Pospuesto'),
    ]
    
    id_evento = models.AutoField(primary_key=True)
    
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Fecha y hora
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    todo_el_dia = models.BooleanField(default=False)
    
    # Ubicación
    ubicacion = models.CharField(max_length=200, blank=True)
    ubicacion_virtual = models.URLField(blank=True, help_text='Link para reuniones virtuales')
    
    # Categorización
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.PROTECT)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    
    # Relaciones
    contactos = models.ManyToManyField(Contacto, blank=True, help_text='Contactos relacionados con este evento')
    cuenta_relacionada = models.ForeignKey(
        cuenta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text='Cuenta del sistema relacionada'
    )
    
    # Recordatorios
    recordatorio_activo = models.BooleanField(default=True)
    minutos_recordatorio = models.PositiveIntegerField(default=15, help_text='Minutos antes del evento')
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha_inicio']
        indexes = [
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['fecha_fin']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_evento']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duracion_horas(self):
        """Duración del evento en horas."""
        if self.fecha_fin and self.fecha_inicio:
            delta = self.fecha_fin - self.fecha_inicio
            return round(delta.total_seconds() / 3600, 2)
        return 0
    
    @property
    def es_hoy(self):
        """Verifica si el evento es hoy."""
        return self.fecha_inicio.date() == timezone.now().date()
    
    @property
    def esta_vencido(self):
        """Verifica si el evento ya pasó."""
        return self.fecha_fin < timezone.now() and self.estado == 'pendiente'


class Tarea(models.Model):
    """Modelo para tareas y recordatorios."""
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    ESTADO_ASIGNACION_CHOICES = [
        ('sin_asignar', 'Sin Asignar'),
        ('asignada', 'Asignada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    id_tarea = models.AutoField(primary_key=True)
    
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Fechas
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    # Categorización
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    
    # Relaciones
    contacto_relacionado = models.ForeignKey(
        Contacto, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    evento_relacionado = models.ForeignKey(
        Evento, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    cuenta_relacionada = models.ForeignKey(
        cuenta, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Asignación de tareas
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tareas_asignadas',
        help_text='Usuario al que se asigna la tarea'
    )
    estado_asignacion = models.CharField(
        max_length=15, 
        choices=ESTADO_ASIGNACION_CHOICES, 
        default='sin_asignar',
        help_text='Estado de la asignación de la tarea'
    )
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_respuesta_asignacion = models.DateTimeField(null=True, blank=True)
    comentarios_asignacion = models.TextField(
        blank=True, 
        help_text='Comentarios sobre la asignación o respuesta'
    )
    
    # Control
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='tareas_creadas'
    )
    
    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['fecha_vencimiento', 'prioridad']
        indexes = [
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
        ]
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_vencida(self):
        """Verifica si la tarea está vencida."""
        if self.fecha_vencimiento and self.estado != 'completada':
            return timezone.now() > self.fecha_vencimiento
        return False
    
    @property
    def dias_restantes(self):
        """Días restantes hasta el vencimiento."""
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento.date() - timezone.now().date()
            return delta.days
        return None
    
    @property
    def es_asignada(self):
        """Verifica si la tarea está asignada a otro usuario."""
        return self.asignado_a is not None and self.asignado_a != self.creado_por
    
    @property 
    def puede_responder_asignacion(self):
        """Verifica si el usuario asignado puede responder la asignación."""
        return self.estado_asignacion == 'asignada'
    
    def asignar_a_usuario(self, usuario, comentarios=''):
        """Asigna la tarea a un usuario."""
        from django.utils import timezone
        self.asignado_a = usuario
        self.estado_asignacion = 'asignada'
        self.fecha_asignacion = timezone.now()
        self.comentarios_asignacion = comentarios
        self.save()
    
    def aceptar_asignacion(self, comentarios=''):
        """El usuario asignado acepta la tarea."""
        from django.utils import timezone
        if self.estado_asignacion == 'asignada':
            self.estado_asignacion = 'aceptada'
            self.fecha_respuesta_asignacion = timezone.now()
            if comentarios:
                self.comentarios_asignacion += f"\n[ACEPTADA] {comentarios}"
            self.save()
    
    def rechazar_asignacion(self, comentarios=''):
        """El usuario asignado rechaza la tarea."""
        from django.utils import timezone
        if self.estado_asignacion == 'asignada':
            self.estado_asignacion = 'rechazada'
            self.fecha_respuesta_asignacion = timezone.now()
            if comentarios:
                self.comentarios_asignacion += f"\n[RECHAZADA] {comentarios}"
            self.save()

    @property
    def usuarios_asignados(self):
        """Obtiene todos los usuarios asignados a esta tarea."""
        return [asignacion.usuario for asignacion in self.asignaciones.all()]
    
    @property
    def asignaciones_aceptadas(self):
        """Obtiene las asignaciones aceptadas."""
        return self.asignaciones.filter(estado='aceptada')
    
    @property
    def asignaciones_pendientes(self):
        """Obtiene las asignaciones pendientes."""
        return self.asignaciones.filter(estado='asignada')
    
    def asignar_a_usuarios(self, usuarios, comentarios=''):
        """Asigna la tarea a múltiples usuarios."""
        from django.utils import timezone
        
        # Crear asignaciones para cada usuario
        for usuario in usuarios:
            AsignacionTarea.objects.get_or_create(
                tarea=self,
                usuario=usuario,
                defaults={
                    'estado': 'asignada',
                    'fecha_asignacion': timezone.now(),
                    'comentarios': comentarios
                }
            )


class AsignacionTarea(models.Model):
    """Modelo intermedio para asignaciones de tareas a múltiples usuarios."""
    
    ESTADO_ASIGNACION_CHOICES = [
        ('asignada', 'Asignada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_tarea'
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_ASIGNACION_CHOICES,
        default='asignada'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    comentarios = models.TextField(blank=True)
    comentarios_respuesta = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['tarea', 'usuario']
        verbose_name = 'Asignación de Tarea'
        verbose_name_plural = 'Asignaciones de Tareas'
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"{self.tarea.titulo} -> {self.usuario.get_full_name() or self.usuario.username}"
    
    def aceptar(self, comentarios=''):
        """El usuario acepta la asignación."""
        from django.utils import timezone
        self.estado = 'aceptada'
        self.fecha_respuesta = timezone.now()
        if comentarios:
            self.comentarios_respuesta = comentarios
        self.save()
    
    def rechazar(self, comentarios=''):
        """El usuario rechaza la asignación."""
        from django.utils import timezone
        self.estado = 'rechazada'
        self.fecha_respuesta = timezone.now()
        if comentarios:
            self.comentarios_respuesta = comentarios
        self.save()


class AsignacionEvento(models.Model):
    """Modelo para asignar eventos a múltiples usuarios."""
    
    ESTADO_CHOICES = [
        ('asignado', 'Asignado'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='asignaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='asignado')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    comentarios = models.TextField(blank=True, help_text='Comentarios del usuario sobre la asignación')
    
    class Meta:
        unique_together = ('evento', 'usuario')
        verbose_name = 'Asignación de Evento'
        verbose_name_plural = 'Asignaciones de Eventos'
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"{self.evento.titulo} - {self.usuario.username} ({self.estado})"
    
    def aceptar(self, comentarios=''):
        """El usuario acepta la asignación."""
        from django.utils import timezone
        self.estado = 'aceptado'
        self.fecha_respuesta = timezone.now()
        if comentarios:
            self.comentarios = comentarios
        self.save()
    
    def rechazar(self, comentarios=''):
        """El usuario rechaza la asignación."""
        from django.utils import timezone
        self.estado = 'rechazado'
        self.fecha_respuesta = timezone.now()
        if comentarios:
            self.comentarios = comentarios
        self.save()


class ComentarioTarea(models.Model):
    """Modelo para comentarios y notas sobre tareas."""
    
    TIPO_CHOICES = [
        ('progreso', 'Progreso'),
        ('problema', 'Problema'),
        ('solucion', 'Solución'),
        ('nota', 'Nota General'),
        ('completado', 'Completado'),
    ]
    
    tarea = models.ForeignKey(
        Tarea, 
        on_delete=models.CASCADE, 
        related_name='comentarios'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    tipo = models.CharField(
        max_length=15, 
        choices=TIPO_CHOICES, 
        default='nota'
    )
    comentario = models.TextField(
        help_text='Comentario sobre la tarea'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Comentario de Tarea'
        verbose_name_plural = 'Comentarios de Tareas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.get_tipo_display()} ({self.usuario.username})"


# Chat models: salas, membresías y mensajes
class ChatRoom(models.Model):
    """Sala de chat - puede ser privada (entre 2 usuarios) o grupal."""
    nombre = models.CharField(max_length=150, blank=True)
    es_grupal = models.BooleanField(default=False)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='chat_rooms_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'

    def __str__(self):
        if self.nombre:
            return self.nombre
        return f"Sala {self.id} ({'Grupal' if self.es_grupal else 'Privada'})"

    def miembros(self):
        return [m.usuario for m in self.membresias.select_related('usuario').all()]


class ChatMembership(models.Model):
    """Membresía de usuario en una sala de chat."""
    sala = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='membresias')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('sala', 'usuario')
        verbose_name = 'Membresía de Chat'
        verbose_name_plural = 'Membresías de Chat'

    def __str__(self):
        return f"{self.sala} <- {self.usuario.username}"


class ChatMessage(models.Model):
    """Mensaje dentro de una sala de chat."""
    sala = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'

    def __str__(self):
        return f"{self.usuario.username}: {self.mensaje[:30]}"
