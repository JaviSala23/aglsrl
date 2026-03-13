"""
Modelos para el sistema de tickets de transporte de mercadería - AGL SRL.
Refleja el flujo real del negocio: llegada de camión, análisis, pesaje.
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal


class TipoMovimiento(models.Model):
    """Tipos de movimiento: Recepción/Envío."""
    
    codigo = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    # Configuración específica del tipo
    requiere_origen = models.BooleanField(default=False, help_text="Si requiere cuenta de origen")
    requiere_destinatario = models.BooleanField(default=False, help_text="Si requiere cuenta destinatario")
    
    class Meta:
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimientos'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class EstadoTicket(models.Model):
    """Estados del ticket durante su ciclo de vida."""
    
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text='Color hexadecimal')
    
    # Control de flujo
    es_inicial = models.BooleanField(default=False)
    es_final = models.BooleanField(default=False)
    permite_edicion = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Estado de Ticket'
        verbose_name_plural = 'Estados de Tickets'
        ordering = ['codigo']
    
    def __str__(self):
        return self.nombre


class Ticket(models.Model):
    """
    Ticket principal de transporte de mercadería.
    Representa la llegada/salida de un camión con mercaderías.
    """
    
    # Información básica del ticket
    numero_ticket = models.CharField(max_length=20, unique=True, editable=False)
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    estado = models.ForeignKey(EstadoTicket, on_delete=models.PROTECT)
    
    # Información del transporte - OBLIGATORIO
    patente_camion = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[A-Z]{2,3}[\d]{3}[A-Z]{2,3}$|^[A-Z]{3}[\d]{3}$',
            message='Formato de patente inválido'
        )],
        help_text='Patente del camión (ej: ABC123DE o ABC123)'
    )
    
    # Información del chofer - OPCIONAL
    chofer = models.ForeignKey(
        'transportes.Chofer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Chofer asignado (opcional)'
    )
    
    # Cuenta de transporte - OPCIONAL
    cuenta_transporte = models.ForeignKey(
        'cuentas.cuenta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_transporte',
        help_text='Empresa de transporte (opcional)'
    )
    
    # Origen y Destinatario según tipo de movimiento
    origen = models.ForeignKey(
        'cuentas.cuenta',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='tickets_origen',
        help_text='Cuenta de origen (para recepciones)'
    )
    
    destinatario = models.ForeignKey(
        'cuentas.cuenta',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='tickets_destinatario',
        help_text='Cuenta destinatario (para envíos)'
    )
    
    # Pesos del camión - Pueden estar vacíos inicialmente
    peso_bruto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Peso bruto del camión en kg'
    )
    
    peso_tara = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Peso tara (camión vacío) en kg'
    )
    
    peso_neto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,  # Se calcula automáticamente
        help_text='Peso neto (bruto - tara) en kg'
    )
    
    # Fechas y control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_llegada = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de llegada del camión'
    )
    fecha_salida = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora de salida del camión'
    )
    
    # Usuario que crea el ticket
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='tickets_creados'
    )
    
    # Planta donde se registra el ticket (asignada automáticamente desde el perfil del encargado)
    planta = models.ForeignKey(
        'almacenamiento.Ubicacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        help_text='Planta donde se registra el pesaje',
    )

    # Observaciones generales
    observaciones = models.TextField(blank=True, help_text='Observaciones generales del ticket')

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['numero_ticket']),
            models.Index(fields=['patente_camion']),
            models.Index(fields=['tipo_movimiento', 'fecha_creacion']),
            models.Index(fields=['estado', 'fecha_creacion']),
            models.Index(fields=['creado_por', 'fecha_creacion']),
        ]
    
    def save(self, *args, **kwargs):
        # Generar número de ticket si no existe
        if not self.numero_ticket:
            self.numero_ticket = self.generar_numero_ticket()
        
        # Calcular peso neto si tenemos bruto y tara
        if self.peso_bruto and self.peso_tara:
            self.peso_neto = self.peso_bruto - self.peso_tara
        
        super().save(*args, **kwargs)
    
    def generar_numero_ticket(self):
        """Generar número de ticket único."""
        from datetime import datetime
        prefix = self.tipo_movimiento.codigo if self.tipo_movimiento_id else 'TKT'
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"{prefix}-{timestamp}"
    
    def __str__(self):
        return f"{self.numero_ticket} - {self.patente_camion}"
    
    @property
    def tiene_pesos_completos(self):
        """Verifica si el ticket tiene todos los pesos registrados."""
        return self.peso_bruto is not None and self.peso_tara is not None
    
    @property
    def total_mercaderias_kg(self):
        """Suma total de kg de todas las mercaderías del ticket."""
        return self.detalle_mercaderias.aggregate(
            total=models.Sum('cantidad_kg')
        )['total'] or Decimal('0')


class DetalleMercaderia(models.Model):
    """
    Detalle de mercaderías en un ticket.
    Un ticket puede tener múltiples mercaderías con diferentes cantidades.
    """
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='detalle_mercaderias'
    )
    
    mercaderia = models.ForeignKey(
        'mercaderias.Mercaderia',
        on_delete=models.PROTECT,
        help_text='Tipo de mercadería'
    )
    
    cantidad_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Cantidad en kilogramos'
    )
    
    # Para análisis de calidad
    calidad_clasificacion = models.ForeignKey(
        'mercaderias.ClasificacionCalidad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Clasificación de calidad (después del análisis)'
    )
    
    # Ubicación de almacenaje (para recepciones)
    ubicacion_almacenaje = models.ForeignKey(
        'almacenamiento.Almacenaje',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Ubicación donde se almacena'
    )
    
    # Control de análisis
    analisis_realizado = models.BooleanField(default=False)
    fecha_analisis = models.DateTimeField(null=True, blank=True)
    analizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analisis_realizados'
    )
    
    # Observaciones específicas de esta mercadería
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Detalle de Mercadería'
        verbose_name_plural = 'Detalles de Mercaderías'
        unique_together = [['ticket', 'mercaderia']]  # Una mercadería por ticket
    
    def __str__(self):
        return f"{self.ticket.numero_ticket} - {self.mercaderia.nombre} ({self.cantidad_kg} kg)"


class AnalisisMercaderia(models.Model):
    """
    Registro detallado de análisis de calidad por mercadería.
    Se puede hacer al ingreso o al egreso según el flujo.
    """
    
    detalle_mercaderia = models.ForeignKey(
        DetalleMercaderia,
        on_delete=models.CASCADE,
        related_name='analisis'
    )
    
    fecha_analisis = models.DateTimeField(default=timezone.now)
    analista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='analisis_realizados_detalle'
    )
    
    # Resultados del análisis
    humedad = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Porcentaje de humedad'
    )
    
    proteina = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Porcentaje de proteína'
    )
    
    grasa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Porcentaje de grasa'
    )
    
    # Otros parámetros según necesidad
    parametros_adicionales = models.JSONField(
        default=dict,
        blank=True,
        help_text='Otros parámetros de análisis en formato JSON'
    )
    
    # Conclusión del análisis
    observaciones_analisis = models.TextField(blank=True)
    aprobado = models.BooleanField(default=True, help_text='Si la mercadería cumple con los estándares')
    
    class Meta:
        verbose_name = 'Análisis de Mercadería'
        verbose_name_plural = 'Análisis de Mercaderías'
        ordering = ['-fecha_analisis']
    
    def __str__(self):
        return f"Análisis - {self.detalle_mercaderia.mercaderia.nombre} ({self.fecha_analisis.strftime('%d/%m/%Y')})"


class ComentarioTicket(models.Model):
    """Comentarios y seguimiento del ticket."""
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField()
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_comentario']
    
    def __str__(self):
        return f"Comentario en {self.ticket.numero_ticket} por {self.autor.username}"


class ArchivoTicket(models.Model):
    """Archivos adjuntos al ticket."""
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='tickets/archivos/%Y/%m/')
    descripcion = models.CharField(max_length=200, blank=True)
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"Archivo: {self.descripcion or self.archivo.name}"