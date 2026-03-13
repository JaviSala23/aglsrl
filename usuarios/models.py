"""
Modelos para gestión de usuarios y perfiles en AGL SRL.
Sistema de roles: ADMINISTRADOR, ENCARGADO, AUXILIAR.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """Perfil extendido del usuario con rol y planta asignada."""

    TIPO_USUARIO_CHOICES = [
        ('AUXILIAR', 'Auxiliar'),
        ('ENCARGADO', 'Encargado'),
        ('ADMINISTRADOR', 'Administrador'),
        ('GERENCIA', 'Gerencia'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    tipo_usuario = models.CharField(
        max_length=15,
        choices=TIPO_USUARIO_CHOICES,
        default='AUXILIAR',
        help_text='Rol que determina los accesos del usuario.',
    )
    # Planta asignada — obligatoria para ENCARGADO, opcional para el resto
    planta = models.ForeignKey(
        'almacenamiento.Ubicacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encargados',
        help_text='Planta asignada al usuario (requerida para Encargado).',
    )

    # Datos básicos
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        planta_str = f' | {self.planta.nombre}' if self.planta else ''
        return (
            f"{self.user.get_full_name() or self.user.username}"
            f" ({self.get_tipo_usuario_display()}{planta_str})"
        )

    # --- Propiedades de conveniencia ---

    @property
    def es_administrador(self):
        return self.tipo_usuario in ('ADMINISTRADOR', 'GERENCIA')

    @property
    def es_encargado(self):
        return self.tipo_usuario == 'ENCARGADO'

    @property
    def nombre_completo(self):
        return self.user.get_full_name() or self.user.username

    @property
    def iniciales(self):
        fn = self.user.first_name
        ln = self.user.last_name
        if fn and ln:
            return f"{fn[0]}{ln[0]}".upper()
        return self.user.username[:2].upper()


# ---------------------------------------------------------------------------
# Signal: crear perfil automáticamente cuando se crea un User
# ---------------------------------------------------------------------------

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
