from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# ==========================================
# GRANOS Y MERCADERÍAS
# ==========================================

class Grano(models.Model):
    """Tipos de granos"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Grano"
        verbose_name_plural = "Granos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def mercaderias_activas_count(self):
        """Cuenta las mercaderías activas de este grano"""
        return self.mercaderias.filter(estado='ACTIVO').count()


class TipoMercaderia(models.TextChoices):
    """Tipos de mercadería"""
    PROPIO = 'PROPIO', 'Propio'
    TERCERO = 'TERCERO', 'Tercero'


class EstadoMercaderia(models.TextChoices):
    """Estados de la mercadería"""
    ACTIVO = 'ACTIVO', 'Activo'
    VENDIDO = 'VENDIDO', 'Vendido'
    TRANSFERIDO = 'TRANSFERIDO', 'Transferido'
    RECHAZADO = 'RECHAZADO', 'Rechazado'


class Mercaderia(models.Model):
    """Mercadería específica con sus características"""
    id = models.AutoField(primary_key=True)
    grano = models.ForeignKey(Grano, on_delete=models.CASCADE, related_name='mercaderias')
    tipo = models.CharField(max_length=20, choices=TipoMercaderia.choices)
    estado = models.CharField(max_length=20, choices=EstadoMercaderia.choices, 
                             default=EstadoMercaderia.ACTIVO)
    
    # Datos del propietario/origen
    propietario_nombre = models.CharField(max_length=100, blank=True, null=True)
    propietario_contacto = models.CharField(max_length=100, blank=True, null=True)
    
    # Características del grano
    humedad_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    proteina_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    cuerpos_extranos_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    granos_danados_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    peso_hectolitro = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Control de fechas
    fecha_ingreso = models.DateField()
    fecha_analisis = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True,
                                        help_text="Fecha límite para almacenamiento")
    
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Mercadería"
        verbose_name_plural = "Mercaderías"
        ordering = ['-fecha_ingreso', 'grano__nombre']
    
    def __str__(self):
        propietario = f" ({self.propietario_nombre})" if self.propietario_nombre else ""
        return f"{self.grano.nombre} - {self.get_tipo_display()}{propietario}"


class Calidad(models.Model):
    """Tipos de calidad para clasificación de mercaderías"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    orden_presentacion = models.PositiveIntegerField(default=0, 
                                                    help_text="Orden de presentación en listas")
    activo = models.BooleanField(default=True)
    
    # Colores para visualización
    color_hex = models.CharField(max_length=7, blank=True, null=True,
                                help_text="Color hexadecimal para visualización (#RRGGBB)")
    
    class Meta:
        verbose_name = "Calidad"
        verbose_name_plural = "Calidades"
        ordering = ['orden_presentacion', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


# ==========================================
# CLASIFICACIÓN DE CALIDADES Y AJUSTES
# ==========================================

class TipoClasificacion(models.TextChoices):
    """Tipos de clasificación de calidad"""
    TAMANO = 'TAMANO', 'Por Tamaño (mm)'
    GRAMAJE = 'GRAMAJE', 'Por Gramaje' 
    CALIDAD = 'CALIDAD', 'Por Calidad'
    DESCARTE = 'DESCARTE', 'Descarte/Aprovechable'
    MIXTA = 'MIXTA', 'Clasificación Mixta'


class EstadoClasificacion(models.TextChoices):
    """Estados de la clasificación"""
    BORRADOR = 'BORRADOR', 'Borrador'
    REGISTRADO = 'REGISTRADO', 'Registrado'
    VERIFICADO = 'VERIFICADO', 'Verificado'
    CANCELADO = 'CANCELADO', 'Cancelado'


class TipoAjuste(models.TextChoices):
    """Tipos de ajuste de stock"""
    BAJA = 'BAJA', 'Baja por Corrección'
    ALTA = 'ALTA', 'Alta por Corrección'


class ClasificacionCalidad(models.Model):
    """Registro de clasificación de calidades de mercadería"""
    id = models.AutoField(primary_key=True)
    
    # Información básica
    codigo = models.CharField(max_length=50, unique=True, 
                             help_text="Código único del registro")
    fecha_registro = models.DateField(help_text="Fecha del registro de clasificación")
    
    # Stock/Mercadería clasificada
    stock_origen = models.ForeignKey('almacenamiento.Stock', on_delete=models.CASCADE,
                                   related_name='clasificaciones',
                                   help_text="Stock que se está clasificando")
    
    # Tipo de clasificación
    tipo_clasificacion = models.CharField(max_length=20, choices=TipoClasificacion.choices,
                                        default=TipoClasificacion.TAMANO)
    
    # Estado del proceso
    estado = models.CharField(max_length=20, choices=EstadoClasificacion.choices,
                            default=EstadoClasificacion.BORRADOR)
    
    # Cantidades
    cantidad_stock_original = models.DecimalField(max_digits=12, decimal_places=2,
                                                help_text="Cantidad original del stock al momento de clasificar")
    cantidad_total_registrada = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'),
                                                  help_text="Suma de todas las cantidades clasificadas")
    
    # Personal
    registrado_por = models.CharField(max_length=100, 
                                    help_text="Empleado que registró la clasificación")
    responsable = models.CharField(max_length=100, blank=True, null=True,
                                 help_text="Responsable de la clasificación física")
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    # Control de fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Clasificación de Calidad"
        verbose_name_plural = "Clasificaciones de Calidad"
        ordering = ['-fecha_registro', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.codigo} - {self.stock_origen.mercaderia.grano.nombre}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código automático
            from django.utils import timezone
            fecha = timezone.now()
            ultimo = ClasificacionCalidad.objects.filter(
                codigo__startswith=f"CL-{fecha.strftime('%Y%m')}"
            ).order_by('-codigo').first()
            
            if ultimo:
                numero = int(ultimo.codigo.split('-')[-1]) + 1
            else:
                numero = 1
            
            self.codigo = f"CL-{fecha.strftime('%Y%m')}-{numero:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def diferencia_cantidad(self):
        """Diferencia entre cantidad original y registrada"""
        return self.cantidad_stock_original - self.cantidad_total_registrada
    
    @property
    def tiene_diferencia(self):
        """Indica si hay diferencia en las cantidades"""
        return abs(self.diferencia_cantidad) > Decimal('0.01')
    
    @property
    def porcentaje_total(self):
        """Suma de todos los porcentajes de los detalles"""
        return sum(detalle.porcentaje for detalle in self.detalles.all())


class DetalleCalidad(models.Model):
    """Detalle de cada calidad específica encontrada"""
    id = models.AutoField(primary_key=True)
    
    # Clasificación a la que pertenece
    clasificacion = models.ForeignKey(ClasificacionCalidad, on_delete=models.CASCADE,
                                    related_name='detalles')
    
    # Tipo de calidad encontrada
    calidad = models.ForeignKey(Calidad, on_delete=models.PROTECT,
                               help_text="Tipo de calidad encontrada")
    
    # Cantidad de esta calidad
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=2,
                                    validators=[MinValueValidator(Decimal('0.01'))])
    
    # Porcentaje respecto al total
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2,
                                   validators=[MinValueValidator(Decimal('0')), 
                                             MaxValueValidator(Decimal('100'))],
                                   help_text="% respecto al total clasificado")
    
    # Ubicación específica donde se encuentra esta calidad
    ubicacion_especifica = models.ForeignKey('almacenamiento.Ubicacion', on_delete=models.PROTECT,
                                           related_name='calidades_ubicadas',
                                           help_text="Ubicación específica donde se ubica esta calidad")
    
    # Almacenaje específico (opcional, si se requiere mayor detalle)
    almacenaje_especifico = models.ForeignKey('almacenamiento.Almacenaje', on_delete=models.SET_NULL,
                                            blank=True, null=True,
                                            related_name='calidades_almacenadas',
                                            help_text="Almacenaje específico donde se ubica esta calidad")
    
    # Observaciones específicas
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Detalle de Calidad"
        verbose_name_plural = "Detalles de Calidad"
        ordering = ['-porcentaje', 'calidad__orden_presentacion']
    
    def __str__(self):
        return f"{self.calidad.nombre}: {self.cantidad_kg}kg ({self.porcentaje}%)"


class TicketAjuste(models.Model):
    """Ticket de ajuste automático por diferencias en clasificación"""
    id = models.AutoField(primary_key=True)
    
    # Información del ticket
    numero_ticket = models.CharField(max_length=50, unique=True)
    tipo_ajuste = models.CharField(max_length=10, choices=TipoAjuste.choices)
    fecha_ajuste = models.DateField()
    
    # Stock afectado
    stock_afectado = models.ForeignKey('almacenamiento.Stock', on_delete=models.PROTECT,
                                     related_name='ajustes')
    cantidad_ajuste_kg = models.DecimalField(max_digits=12, decimal_places=2,
                                           validators=[MinValueValidator(Decimal('0.01'))])
    
    # Justificación
    motivo = models.TextField()
    clasificacion_origen = models.ForeignKey(ClasificacionCalidad, on_delete=models.SET_NULL,
                                           blank=True, null=True,
                                           related_name='ajustes_generados',
                                           help_text="Clasificación que originó este ajuste")
    
    # Personal
    autorizado_por = models.CharField(max_length=100)
    registrado_por = models.CharField(max_length=100)
    
    # Control
    aplicado = models.BooleanField(default=False)
    fecha_aplicacion = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ticket de Ajuste"
        verbose_name_plural = "Tickets de Ajuste"
        ordering = ['-fecha_ajuste', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.numero_ticket} - {self.get_tipo_ajuste_display()}"