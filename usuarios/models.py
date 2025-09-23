"""from django.db import models

Modelos para gestión de usuarios, equipos, proyectos y tareas.from django.contrib.auth.models import AbstractUser

Sistema de roles jerárquico para AGL SRL usando extensión del User de Django.from django.utils import timezone

"""

from django.db import models# Modelo de Usuario personalizado

from django.contrib.auth.models import Userclass Usuario(AbstractUser):

from django.utils import timezone    """

from django.urls import reverseModelos para gestión de usuarios, equipos, proyectos y tareas.

from datetime import datetime, timedeltaSistema de roles jerárquico para AGL SRL.

"""

from django.db import models

class PerfilUsuario(models.Model):from django.contrib.auth.models import User

    """Perfil extendido del usuario con información adicional"""from django.utils import timezone

    from django.urls import reverse

    TIPO_USUARIO_CHOICES = [from datetime import datetime, timedelta

        ('AUXILIAR', 'Auxiliar'),

        ('ENCARGADO', 'Encargado'), 

        ('ADMINISTRADOR', 'Administrador'),class PerfilUsuario(models.Model):

        ('GERENCIA', 'Gerencia'),    """Perfil extendido del usuario con información adicional"""

    ]    

        TIPO_USUARIO_CHOICES = [

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')        ('AUXILIAR', 'Auxiliar'),

    tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES, default='AUXILIAR')        ('ENCARGADO', 'Encargado'), 

            ('ADMINISTRADOR', 'Administrador'),

    # Información personal adicional        ('GERENCIA', 'Gerencia'),

    telefono = models.CharField(max_length=20, blank=True)    ]

    direccion = models.TextField(blank=True)    

    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')

        tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES, default='AUXILIAR')

    # Configuraciones de la cuenta    

    recibir_notificaciones = models.BooleanField(default=True)    # Información personal adicional

    notificaciones_email = models.BooleanField(default=True)    telefono = models.CharField(max_length=20, blank=True)

    tema_interfaz = models.CharField(max_length=10, choices=[('claro', 'Claro'), ('oscuro', 'Oscuro')], default='claro')    direccion = models.TextField(blank=True)

        foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)

    # Control    

    activo = models.BooleanField(default=True)    # Configuraciones de la cuenta

    fecha_ultima_actividad = models.DateTimeField(auto_now=True)    recibir_notificaciones = models.BooleanField(default=True)

        notificaciones_email = models.BooleanField(default=True)

    class Meta:    tema_interfaz = models.CharField(max_length=10, choices=[('claro', 'Claro'), ('oscuro', 'Oscuro')], default='claro')

        verbose_name = 'Perfil de Usuario'    

        verbose_name_plural = 'Perfiles de Usuario'    # Control

        ordering = ['user__last_name', 'user__first_name']    activo = models.BooleanField(default=True)

        fecha_ultima_actividad = models.DateTimeField(auto_now=True)

    def __str__(self):    

        return f"{self.user.get_full_name() or self.user.username} ({self.get_tipo_usuario_display()})"    class Meta:

            verbose_name = 'Perfil de Usuario'

    @property        verbose_name_plural = 'Perfiles de Usuario'

    def nombre_completo(self):        ordering = ['user__last_name', 'user__first_name']

        return self.user.get_full_name() or self.user.username    

        def __str__(self):

    @property        return f"{self.user.get_full_name() or self.user.username} ({self.get_tipo_usuario_display()})"

    def iniciales(self):    

        if self.user.first_name and self.user.last_name:    @property

            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()    def nombre_completo(self):

        return self.user.username[:2].upper()        return self.user.get_full_name() or self.user.username

        

    def puede_ver_datos_sensibles(self):    @property

        """Determina si el usuario puede ver datos financieros sensibles"""    def iniciales(self):

        return self.tipo_usuario in ['ADMINISTRADOR', 'GERENCIA']        if self.user.first_name and self.user.last_name:

                return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()

    def puede_administrar_usuarios(self):        return self.user.username[:2].upper()

        """Determina si puede gestionar otros usuarios"""    

        return self.tipo_usuario in ['ADMINISTRADOR', 'GERENCIA']    def puede_ver_datos_sensibles(self):

            """Determina si el usuario puede ver datos financieros sensibles"""

    def puede_crear_proyectos(self):        return self.tipo_usuario in ['ADMINISTRADOR', 'GERENCIA']

        """Determina si puede crear nuevos proyectos"""    

        return self.tipo_usuario in ['ENCARGADO', 'ADMINISTRADOR', 'GERENCIA']    def puede_administrar_usuarios(self):

        """Determina si puede gestionar otros usuarios"""

        return self.tipo_usuario in ['ADMINISTRADOR', 'GERENCIA']

class Equipo(models.Model):    

    """Equipos de trabajo para organizar usuarios y proyectos"""    def puede_crear_proyectos(self):

            """Determina si puede crear nuevos proyectos"""

    nombre = models.CharField(max_length=100, unique=True)        return self.tipo_usuario in ['ENCARGADO', 'ADMINISTRADOR', 'GERENCIA']

    descripcion = models.TextField(blank=True)    TIPO_USUARIO_CHOICES = [

    color = models.CharField(max_length=7, default='#6f42c1', help_text='Color en hexadecimal')        ('AUXILIAR', 'Auxiliar'),

            ('ENCARGADO', 'Encargado'),

    # Jerarquía        ('ADMINISTRADOR', 'Administrador'),

    lider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='equipos_liderados')        ('GERENCIA', 'Gerencia'),

    miembros = models.ManyToManyField(User, related_name='equipos', blank=True)    ]

        

    # Control    # Campos adicionales del usuario

    activo = models.BooleanField(default=True)    tipo_usuario = models.CharField(

    fecha_creacion = models.DateTimeField(auto_now_add=True)        max_length=15, 

    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='equipos_creados')        choices=TIPO_USUARIO_CHOICES, 

            default='AUXILIAR',

    class Meta:        help_text="Tipo de usuario que determina los permisos base"

        verbose_name = 'Equipo'    )

        verbose_name_plural = 'Equipos'    telefono = models.CharField(max_length=20, blank=True, null=True)

        ordering = ['nombre']    celular = models.CharField(max_length=20, blank=True, null=True)

        puesto = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):    fecha_ingreso = models.DateField(default=timezone.now)

        return self.nombre    activo = models.BooleanField(default=True)

        

    @property    # Avatar/foto de perfil

    def total_miembros(self):    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

        return self.miembros.count()    

    # Configuraciones personales

    tema_preferido = models.CharField(

class Proyecto(models.Model):        max_length=10, 

    """Proyectos para organizar tareas"""        choices=[('light', 'Claro'), ('dark', 'Oscuro')], 

            default='light'

    ESTADO_CHOICES = [    )

        ('PLANIFICACION', 'En Planificación'),    notificaciones_email = models.BooleanField(default=True)

        ('EN_CURSO', 'En Curso'),    notificaciones_sistema = models.BooleanField(default=True)

        ('PAUSADO', 'Pausado'),    

        ('COMPLETADO', 'Completado'),    class Meta:

        ('CANCELADO', 'Cancelado'),        verbose_name = "Usuario"

    ]        verbose_name_plural = "Usuarios"

            

    PRIORIDAD_CHOICES = [    def __str__(self):

        ('BAJA', 'Baja'),        return f"{self.get_full_name() or self.username} ({self.get_tipo_usuario_display()})"

        ('MEDIA', 'Media'),    

        ('ALTA', 'Alta'),    def get_full_name_or_username(self):

        ('CRITICA', 'Crítica'),        return self.get_full_name() or self.username

    ]    

        def puede_crear_tareas(self):

    nombre = models.CharField(max_length=200)        """Determina si el usuario puede crear tareas para otros"""

    descripcion = models.TextField(blank=True)        return self.tipo_usuario in ['ENCARGADO', 'ADMINISTRADOR', 'GERENCIA']

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PLANIFICACION')    

    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')    def puede_administrar_sistema(self):

    color = models.CharField(max_length=7, default='#6f42c1')        """Determina si el usuario puede administrar el sistema"""

            return self.tipo_usuario in ['ADMINISTRADOR', 'GERENCIA']

    # Fechas

    fecha_inicio = models.DateField(null=True, blank=True)

    fecha_fin_estimada = models.DateField(null=True, blank=True)class Equipo(models.Model):

    fecha_fin_real = models.DateField(null=True, blank=True)    """

        Equipos de trabajo para organizar usuarios

    # Asignaciones    """

    propietario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='proyectos_propios')    nombre = models.CharField(max_length=100, unique=True)

    colaboradores = models.ManyToManyField(User, related_name='proyectos_colaborando', blank=True)    descripcion = models.TextField(blank=True, null=True)

    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True)    lider = models.ForeignKey(

            Usuario, 

    # Control        on_delete=models.SET_NULL, 

    activo = models.BooleanField(default=True)        null=True, 

    fecha_creacion = models.DateTimeField(auto_now_add=True)        blank=True,

    fecha_modificacion = models.DateTimeField(auto_now=True)        related_name='equipos_liderados'

    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='proyectos_creados')    )

        miembros = models.ManyToManyField(

    class Meta:        Usuario, 

        verbose_name = 'Proyecto'        related_name='equipos',

        verbose_name_plural = 'Proyectos'        blank=True

        ordering = ['-fecha_creacion']    )

        indexes = [    activo = models.BooleanField(default=True)

            models.Index(fields=['estado']),    fecha_creacion = models.DateTimeField(auto_now_add=True)

            models.Index(fields=['propietario']),    

            models.Index(fields=['fecha_inicio']),    class Meta:

        ]        verbose_name = "Equipo"

            verbose_name_plural = "Equipos"

    def __str__(self):        

        return self.nombre    def __str__(self):

            return self.nombre

    @property

    def progreso_porcentaje(self):

        """Calcula el progreso basado en tareas completadas"""class Proyecto(models.Model):

        total_tareas = self.tareas.count()    """

        if total_tareas == 0:    Proyectos para organizar tareas

            return 0    """

        tareas_completadas = self.tareas.filter(estado='COMPLETADA').count()    ESTADO_CHOICES = [

        return round((tareas_completadas / total_tareas) * 100)        ('PLANIFICACION', 'En Planificación'),

        ('EN_CURSO', 'En Curso'),

        ('PAUSADO', 'Pausado'),

class Tarea(models.Model):        ('COMPLETADO', 'Completado'),

    """Tareas individuales del sistema"""        ('CANCELADO', 'Cancelado'),

        ]

    ESTADO_CHOICES = [    

        ('PENDIENTE', 'Pendiente'),    nombre = models.CharField(max_length=200)

        ('EN_PROGRESO', 'En Progreso'),    descripcion = models.TextField(blank=True, null=True)

        ('COMPLETADA', 'Completada'),    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PLANIFICACION')

        ('CANCELADA', 'Cancelada'),    

    ]    # Fechas

        fecha_inicio = models.DateField(null=True, blank=True)

    PRIORIDAD_CHOICES = [    fecha_fin_estimada = models.DateField(null=True, blank=True)

        ('BAJA', 'Baja'),    fecha_fin_real = models.DateField(null=True, blank=True)

        ('MEDIA', 'Media'),    

        ('ALTA', 'Alta'),    # Responsables

        ('CRITICA', 'Crítica'),    propietario = models.ForeignKey(

    ]        Usuario, 

            on_delete=models.CASCADE,

    titulo = models.CharField(max_length=200)        related_name='proyectos_propios'

    descripcion = models.TextField(blank=True)    )

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')    colaboradores = models.ManyToManyField(

    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')        Usuario, 

            related_name='proyectos_colaborador',

    # Fechas        blank=True

    fecha_vencimiento = models.DateTimeField(null=True, blank=True)    )

    fecha_completado = models.DateTimeField(null=True, blank=True)    equipo = models.ForeignKey(

            Equipo, 

    # Asignaciones        on_delete=models.SET_NULL, 

    asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_asignadas')        null=True, 

    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='tareas_creadas')        blank=True

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas', null=True, blank=True)    )

        

    # Configuración de visibilidad    # Metadatos

    es_personal = models.BooleanField(default=False, help_text='Solo visible para el asignado')    prioridad = models.CharField(

    es_publica = models.BooleanField(default=True, help_text='Visible para todos los usuarios')        max_length=10,

            choices=[

    # Metadatos            ('BAJA', 'Baja'),

    etiquetas = models.CharField(max_length=500, blank=True, help_text='Separadas por comas')            ('MEDIA', 'Media'),

    tiempo_estimado = models.PositiveIntegerField(null=True, blank=True, help_text='En minutos')            ('ALTA', 'Alta'),

                ('URGENTE', 'Urgente'),

    # Control        ],

    activa = models.BooleanField(default=True)        default='MEDIA'

    fecha_creacion = models.DateTimeField(auto_now_add=True)    )

    fecha_actualizacion = models.DateTimeField(auto_now=True)    color = models.CharField(max_length=7, default='#3498db', help_text="Color hexadecimal para identificar el proyecto")

        

    class Meta:    fecha_creacion = models.DateTimeField(auto_now_add=True)

        verbose_name = 'Tarea'    fecha_actualizacion = models.DateTimeField(auto_now=True)

        verbose_name_plural = 'Tareas'    

        ordering = ['-fecha_creacion']    class Meta:

        indexes = [        verbose_name = "Proyecto"

            models.Index(fields=['asignado_a', 'estado']),        verbose_name_plural = "Proyectos"

            models.Index(fields=['creado_por']),        ordering = ['-fecha_creacion']

            models.Index(fields=['fecha_vencimiento']),        

            models.Index(fields=['prioridad']),    def __str__(self):

        ]        return f"{self.nombre} ({self.get_estado_display()})"

        

    def __str__(self):    def progreso_porcentaje(self):

        return self.titulo        """Calcula el porcentaje de completado basado en las tareas"""

            total_tareas = self.tareas.count()

    @property        if total_tareas == 0:

    def esta_vencida(self):            return 0

        """Determina si la tarea está vencida"""        tareas_completadas = self.tareas.filter(estado='COMPLETADA').count()

        if not self.fecha_vencimiento:        return int((tareas_completadas / total_tareas) * 100)

            return False

        return timezone.now() > self.fecha_vencimiento and self.estado != 'COMPLETADA'

    class Tarea(models.Model):

    def puede_editar(self, usuario):    """

        """Determina si un usuario puede editar esta tarea"""    Tareas personales y asignadas por otros usuarios

        if not hasattr(usuario, 'perfil'):    """

            return False    ESTADO_CHOICES = [

                ('PENDIENTE', 'Pendiente'),

        # El creador y el asignado siempre pueden editar        ('EN_PROGRESO', 'En Progreso'),

        if self.creado_por == usuario or self.asignado_a == usuario:        ('BLOQUEADA', 'Bloqueada'),

            return True        ('COMPLETADA', 'Completada'),

                ('CANCELADA', 'Cancelada'),

        # Administradores y gerencia pueden editar cualquier tarea    ]

        return usuario.perfil.tipo_usuario in ['ADMINISTRADOR', 'GERENCIA']    

    PRIORIDAD_CHOICES = [

        ('BAJA', 'Baja'),

class ComentarioTarea(models.Model):        ('MEDIA', 'Media'),

    """Comentarios en las tareas"""        ('ALTA', 'Alta'),

            ('URGENTE', 'Urgente'),

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='comentarios')    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)    

    comentario = models.TextField()    # Información básica

        titulo = models.CharField(max_length=200)

    # Control    descripcion = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')

    fecha_modificacion = models.DateTimeField(auto_now=True)    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')

    activo = models.BooleanField(default=True)    

        # Asignación y responsabilidades

    class Meta:    creado_por = models.ForeignKey(

        verbose_name = 'Comentario de Tarea'        Usuario, 

        verbose_name_plural = 'Comentarios de Tareas'        on_delete=models.CASCADE,

        ordering = ['fecha_creacion']        related_name='tareas_creadas',

            help_text="Usuario que creó la tarea"

    def __str__(self):    )

        return f"Comentario de {self.usuario.username} en {self.tarea.titulo}"    asignado_a = models.ForeignKey(

        Usuario, 

        on_delete=models.CASCADE,

class HistorialTarea(models.Model):        related_name='tareas_asignadas',

    """Historial de cambios en las tareas"""        help_text="Usuario responsable de ejecutar la tarea"

        )

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='historial')    

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)    # Organización

    accion = models.CharField(max_length=100)    proyecto = models.ForeignKey(

    descripcion = models.TextField()        Proyecto, 

    fecha = models.DateTimeField(auto_now_add=True)        on_delete=models.CASCADE, 

            related_name='tareas',

    class Meta:        null=True, 

        verbose_name = 'Historial de Tarea'        blank=True

        verbose_name_plural = 'Historiales de Tareas'    )

        ordering = ['-fecha']    etiquetas = models.CharField(

            max_length=200, 

    def __str__(self):        blank=True, 

        return f"{self.accion} por {self.usuario.username}"        null=True,

        help_text="Etiquetas separadas por comas para categorizar la tarea"

    )

class Notificacion(models.Model):    

    """Sistema de notificaciones para usuarios"""    # Fechas y tiempo

        fecha_vencimiento = models.DateTimeField(null=True, blank=True)

    TIPO_CHOICES = [    fecha_inicio_real = models.DateTimeField(null=True, blank=True)

        ('TAREA_ASIGNADA', 'Tarea Asignada'),    fecha_completado = models.DateTimeField(null=True, blank=True)

        ('TAREA_VENCIDA', 'Tarea Vencida'),    tiempo_estimado = models.PositiveIntegerField(

        ('PROYECTO_ACTUALIZADO', 'Proyecto Actualizado'),        null=True, 

        ('COMENTARIO_TAREA', 'Comentario en Tarea'),        blank=True,

        ('SISTEMA', 'Notificación del Sistema'),        help_text="Tiempo estimado en horas"

    ]    )

        tiempo_real = models.PositiveIntegerField(

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')        null=True, 

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)        blank=True,

    titulo = models.CharField(max_length=200)        help_text="Tiempo real invertido en horas"

    mensaje = models.TextField()    )

        

    # Referencias opcionales    # Dependencias

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, null=True, blank=True)    tarea_padre = models.ForeignKey(

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, blank=True)        'self', 

    url = models.URLField(blank=True, help_text='URL de acción opcional')        on_delete=models.CASCADE, 

            null=True, 

    # Control        blank=True,

    leida = models.BooleanField(default=False)        related_name='subtareas'

    fecha_creacion = models.DateTimeField(auto_now_add=True)    )

    fecha_lectura = models.DateTimeField(null=True, blank=True)    tareas_dependientes = models.ManyToManyField(

            'self', 

    class Meta:        symmetrical=False,

        verbose_name = 'Notificación'        blank=True,

        verbose_name_plural = 'Notificaciones'        help_text="Tareas que deben completarse antes que esta"

        ordering = ['-fecha_creacion']    )

        indexes = [    

            models.Index(fields=['usuario', 'leida']),    # Control de visibilidad

            models.Index(fields=['fecha_creacion']),    es_personal = models.BooleanField(

        ]        default=True,

            help_text="Si es True, solo el usuario asignado puede ver la tarea"

    def __str__(self):    )

        return f"{self.titulo} - {self.usuario.username}"    es_publica = models.BooleanField(

            default=False,

    def marcar_leida(self):        help_text="Si es True, todos los usuarios pueden ver la tarea"

        """Marca la notificación como leída"""    )

        if not self.leida:    

            self.leida = True    # Metadatos

            self.fecha_lectura = timezone.now()    fecha_creacion = models.DateTimeField(auto_now_add=True)

            self.save()    fecha_actualizacion = models.DateTimeField(auto_now=True)

    

    # Archivos adjuntos

class Agenda(models.Model):    archivo_adjunto = models.FileField(upload_to='tareas/archivos/', blank=True, null=True)

    """Eventos de agenda personal de usuarios"""    

        class Meta:

    TIPO_EVENTO_CHOICES = [        verbose_name = "Tarea"

        ('REUNION', 'Reunión'),        verbose_name_plural = "Tareas"

        ('CITA', 'Cita'),        ordering = ['fecha_vencimiento', '-prioridad', '-fecha_creacion']

        ('EVENTO', 'Evento'),        indexes = [

        ('RECORDATORIO', 'Recordatorio'),            models.Index(fields=['asignado_a', 'estado']),

        ('TAREA', 'Tarea Programada'),            models.Index(fields=['creado_por']),

    ]            models.Index(fields=['fecha_vencimiento']),

                models.Index(fields=['prioridad']),

    titulo = models.CharField(max_length=200)        ]

    descripcion = models.TextField(blank=True)        

    tipo_evento = models.CharField(max_length=15, choices=TIPO_EVENTO_CHOICES, default='EVENTO')    def __str__(self):

            return f"{self.titulo} - {self.get_estado_display()}"

    # Fechas y horarios    

    fecha_inicio = models.DateTimeField()    def esta_vencida(self):

    fecha_fin = models.DateTimeField()        """Determina si la tarea está vencida"""

    todo_el_dia = models.BooleanField(default=False)        if self.fecha_vencimiento and self.estado not in ['COMPLETADA', 'CANCELADA']:

                return timezone.now() > self.fecha_vencimiento

    # Ubicación        return False

    ubicacion = models.CharField(max_length=200, blank=True)    

        def dias_hasta_vencimiento(self):

    # Usuarios        """Calcula los días hasta el vencimiento"""

    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_organizados')        if self.fecha_vencimiento:

    asistentes = models.ManyToManyField(User, related_name='eventos_asistiendo', blank=True)            diff = self.fecha_vencimiento.date() - timezone.now().date()

                return diff.days

    # Recordatorios        return None

    recordatorio_activo = models.BooleanField(default=True)    

    minutos_recordatorio = models.PositiveIntegerField(default=15)    def puede_ver(self, usuario):

            """Determina si un usuario puede ver esta tarea"""

    # Control        # El creador y el asignado siempre pueden ver

    activo = models.BooleanField(default=True)        if usuario in [self.creado_por, self.asignado_a]:

    fecha_creacion = models.DateTimeField(auto_now_add=True)            return True

            

    class Meta:        # Si es pública, todos pueden ver

        verbose_name = 'Evento de Agenda'        if self.es_publica:

        verbose_name_plural = 'Eventos de Agenda'            return True

        ordering = ['fecha_inicio']        

        indexes = [        # Si no es personal, los miembros del equipo pueden ver

            models.Index(fields=['organizador', 'fecha_inicio']),        if not self.es_personal and self.proyecto and self.proyecto.equipo:

            models.Index(fields=['fecha_inicio']),            return usuario in self.proyecto.equipo.miembros.all()

        ]        

            # Los administradores y gerencia pueden ver todas

    def __str__(self):        if usuario.puede_administrar_sistema():

        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"            return True

        

        return False

# Signals para crear perfil automáticamente    

from django.db.models.signals import post_save    def puede_editar(self, usuario):

from django.dispatch import receiver        """Determina si un usuario puede editar esta tarea"""

        # El creador y el asignado pueden editar

@receiver(post_save, sender=User)        if usuario in [self.creado_por, self.asignado_a]:

def crear_perfil_usuario(sender, instance, created, **kwargs):            return True

    """Crear perfil automáticamente cuando se crea un usuario"""        

    if created:        # Los administradores pueden editar todas

        PerfilUsuario.objects.create(user=instance)        if usuario.puede_administrar_sistema():

            return True

@receiver(post_save, sender=User)        

def guardar_perfil_usuario(sender, instance, **kwargs):        return False

    """Guardar perfil cuando se guarda el usuario"""

    if hasattr(instance, 'perfil'):

        instance.perfil.save()class ComentarioTarea(models.Model):
    """
    Comentarios y seguimiento de tareas
    """
    tarea = models.ForeignKey(
        Tarea, 
        on_delete=models.CASCADE, 
        related_name='comentarios'
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()
    es_interno = models.BooleanField(
        default=False,
        help_text="Si es True, solo el creador y asignado pueden ver el comentario"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comentario de Tarea"
        verbose_name_plural = "Comentarios de Tareas"
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"Comentario de {self.usuario.get_full_name_or_username()} en {self.tarea.titulo}"


class HistorialTarea(models.Model):
    """
    Historial de cambios en las tareas
    """
    tarea = models.ForeignKey(
        Tarea, 
        on_delete=models.CASCADE, 
        related_name='historial'
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Tarea"
        verbose_name_plural = "Historial de Tareas"
        ordering = ['-fecha']
        
    def __str__(self):
        return f"{self.accion} - {self.tarea.titulo}"


class Notificacion(models.Model):
    """
    Notificaciones del sistema para usuarios
    """
    TIPO_CHOICES = [
        ('TAREA_ASIGNADA', 'Tarea Asignada'),
        ('TAREA_VENCIDA', 'Tarea Vencida'),
        ('TAREA_COMPLETADA', 'Tarea Completada'),
        ('COMENTARIO_TAREA', 'Nuevo Comentario'),
        ('PROYECTO_ACTUALIZADO', 'Proyecto Actualizado'),
        ('SISTEMA', 'Notificación del Sistema'),
    ]
    
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Referencias opcionales
    tarea = models.ForeignKey(
        Tarea, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"{self.titulo} - {self.usuario.get_full_name_or_username()}"


class Agenda(models.Model):
    """
    Eventos de agenda personal y compartida
    """
    TIPO_CHOICES = [
        ('REUNION', 'Reunión'),
        ('LLAMADA', 'Llamada'),
        ('TAREA', 'Tarea'),
        ('EVENTO', 'Evento'),
        ('RECORDATORIO', 'Recordatorio'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='EVENTO')
    
    # Fechas y hora
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    todo_el_dia = models.BooleanField(default=False)
    
    # Ubicación
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    
    # Asistentes
    organizador = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='eventos_organizados'
    )
    asistentes = models.ManyToManyField(
        Usuario, 
        related_name='eventos_asistencia',
        blank=True
    )
    
    # Configuración
    es_privado = models.BooleanField(default=True)
    recordatorio = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Minutos antes del evento para recordar"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento de Agenda"
        verbose_name_plural = "Eventos de Agenda"
        ordering = ['fecha_inicio']
        
    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def puede_ver(self, usuario):
        """Determina si un usuario puede ver este evento"""
        if usuario == self.organizador:
            return True
        if usuario in self.asistentes.all():
            return True
        if not self.es_privado:
            return True
        if usuario.puede_administrar_sistema():
            return True
        return False
