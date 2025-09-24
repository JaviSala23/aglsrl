from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class TipoGrano(models.Model):
    """Catálogo de tipos de grano"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)  # soja, maíz, girasol, trigo, etc.
    codigo = models.CharField(max_length=10, unique=True)  # SOJ, MAI, GIR, TRI, etc.
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tipo de Grano"
        verbose_name_plural = "Tipos de Grano"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class CalidadGrado(models.Model):
    """Catálogo de calidades y grados"""
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)  # Premium, Estándar, FAS, etc.
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Calidad/Grado"
        verbose_name_plural = "Calidades/Grados"
        ordering = ['descripcion']
    
    def __str__(self):
        return f"{self.descripcion} ({self.codigo})"


class Mercaderia(models.Model):
    """Mercadería específica (grano + tipo + cantidad)"""
    id = models.AutoField(primary_key=True)
    grano = models.ForeignKey(TipoGrano, on_delete=models.PROTECT, related_name='mercaderias')
    calidad_grado = models.ForeignKey(CalidadGrado, on_delete=models.PROTECT, 
                                     related_name='mercaderias', blank=True, null=True)
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=2, 
                                     validators=[MinValueValidator(Decimal('0.01'))])
    observaciones = models.TextField(blank=True, null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Mercadería"
        verbose_name_plural = "Mercaderías"
        ordering = ['-fecha_ingreso']
    
    def __str__(self):
        calidad = f" - {self.calidad_grado.descripcion}" if self.calidad_grado else ""
        return f"{self.grano.nombre}{calidad} ({self.cantidad_kg} kg)"


# ==========================================
# UBICACIONES Y ALMACENAJES
# ==========================================

class TipoUbicacion(models.TextChoices):
    """Tipos de ubicación"""
    PLANTA = 'PLANTA', 'Planta'
    ZONA_MIXTA = 'ZONA_MIXTA', 'Zona Mixta'


class Ubicacion(models.Model):
    """Ubicaciones donde se almacenan mercaderías"""
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TipoUbicacion.choices)
    encargado_nombre = models.CharField(max_length=100, blank=True, null=True,
                                       help_text="Nombre del encargado (solo para plantas)")
    direccion = models.TextField(blank=True, null=True)
    
    # Geodatos opcionales
    latitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']
    
    def __str__(self):
        encargado = f" - {self.encargado_nombre}" if self.encargado_nombre else ""
        return f"{self.nombre} ({self.get_tipo_display()}){encargado}"


class TipoAlmacenaje(models.TextChoices):
    """Tipos de almacenaje"""
    SILO = 'SILO', 'Silo'
    SILO_BOLSA = 'SILO_BOLSA', 'Silo Bolsa'
    GALPON = 'GALPON', 'Galpón'


class EstadoAlmacenaje(models.TextChoices):
    """Estados de almacenaje"""
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    OCUPADO = 'OCUPADO', 'Ocupado'
    FUMIGACION = 'FUMIGACION', 'En Fumigación'
    MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
    BLOQUEADO = 'BLOQUEADO', 'Bloqueado'


class Almacenaje(models.Model):
    """Almacenajes dentro de una ubicación"""
    id = models.AutoField(primary_key=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='almacenajes')
    tipo = models.CharField(max_length=20, choices=TipoAlmacenaje.choices)
    codigo = models.CharField(max_length=50)  # Código identificador del almacenaje
    capacidad_kg = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    estado = models.CharField(max_length=20, choices=EstadoAlmacenaje.choices, 
                             default=EstadoAlmacenaje.DISPONIBLE)
    
    # Geodatos opcionales para ubicación específica dentro de la ubicación
    latitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    
    # Campos específicos para silo bolsa
    longitud_metros = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
                                         help_text="Longitud en metros (para silo bolsa)")
    sentido = models.CharField(max_length=50, blank=True, null=True,
                              help_text="Sentido de orientación (para silo bolsa)")
    
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Almacenaje"
        verbose_name_plural = "Almacenajes"
        ordering = ['ubicacion__nombre', 'codigo']
        unique_together = [['ubicacion', 'codigo']]
    
    def __str__(self):
        return f"{self.ubicacion.nombre} - {self.codigo} ({self.get_tipo_display()})"


# ==========================================
# PRESENTACIONES Y UNIDADES
# ==========================================

class TipoPresentacion(models.TextChoices):
    """Tipos de presentación"""
    GRANEL = 'GRANEL', 'Granel'
    BOLSA_25 = 'BOLSA_25', 'Bolsa 25kg'
    BOLSA_50 = 'BOLSA_50', 'Bolsa 50kg'
    BIGBAG_500 = 'BIGBAG_500', 'Big Bag 500kg'
    BIGBAG_1000 = 'BIGBAG_1000', 'Big Bag 1000kg'


class UnidadMedida(models.TextChoices):
    """Unidades de medida"""
    KG = 'KG', 'Kilogramos'
    TN = 'TN', 'Toneladas'
    BOLSAS = 'BOLSAS', 'Bolsas'
    UNIDADES = 'UNIDADES', 'Unidades'


class PesoUnitarioReferencia(models.Model):
    """Pesos unitarios de referencia por presentación"""
    id = models.AutoField(primary_key=True)
    presentacion = models.CharField(max_length=20, choices=TipoPresentacion.choices, unique=True)
    peso_kg = models.DecimalField(max_digits=8, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        verbose_name = "Peso Unitario de Referencia"
        verbose_name_plural = "Pesos Unitarios de Referencia"
        ordering = ['presentacion']
    
    def __str__(self):
        return f"{self.get_presentacion_display()}: {self.peso_kg} kg"


class FactorConversion(models.Model):
    """Factores de conversión entre unidades"""
    id = models.AutoField(primary_key=True)
    unidad_origen = models.CharField(max_length=20, choices=UnidadMedida.choices)
    unidad_destino = models.CharField(max_length=20, choices=UnidadMedida.choices)
    factor = models.DecimalField(max_digits=10, decimal_places=4,
                                validators=[MinValueValidator(Decimal('0.0001'))])
    
    class Meta:
        verbose_name = "Factor de Conversión"
        verbose_name_plural = "Factores de Conversión"
        unique_together = [['unidad_origen', 'unidad_destino']]
        ordering = ['unidad_origen', 'unidad_destino']
    
    def __str__(self):
        return f"1 {self.get_unidad_origen_display()} = {self.factor} {self.get_unidad_destino_display()}"


class ReglaAlmacenajePresentacion(models.Model):
    """Reglas de compatibilidad entre tipos de almacenaje y presentaciones"""
    id = models.AutoField(primary_key=True)
    tipo_almacenaje = models.CharField(max_length=20, choices=TipoAlmacenaje.choices)
    tipo_presentacion = models.CharField(max_length=20, choices=TipoPresentacion.choices)
    es_compatible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Regla Almacenaje-Presentación"
        verbose_name_plural = "Reglas Almacenaje-Presentación"
        unique_together = [['tipo_almacenaje', 'tipo_presentacion']]
        ordering = ['tipo_almacenaje', 'tipo_presentacion']
    
    def __str__(self):
        estado = "Compatible" if self.es_compatible else "No Compatible"
        return f"{self.get_tipo_almacenaje_display()} - {self.get_tipo_presentacion_display()}: {estado}"


# ==========================================
# STOCK
# ==========================================

class Stock(models.Model):
    """Stock consolidado por ubicación, almacenaje y mercadería"""
    id = models.AutoField(primary_key=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='stocks')
    almacenaje = models.ForeignKey(Almacenaje, on_delete=models.CASCADE, related_name='stocks')
    mercaderia = models.ForeignKey(Mercaderia, on_delete=models.CASCADE, related_name='stocks')
    cantidad_kg = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = [['ubicacion', 'almacenaje', 'mercaderia']]
        ordering = ['ubicacion__nombre', 'almacenaje__codigo', 'mercaderia__grano__nombre']
    
    def __str__(self):
        return f"{self.ubicacion.nombre} - {self.almacenaje.codigo}: {self.mercaderia.grano.nombre} ({self.cantidad_kg} kg)"
