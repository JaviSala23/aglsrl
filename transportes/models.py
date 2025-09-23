"""
Modelos para el módulo de transportes y logística.
Incluye gestión de camiones, choferes, viajes y tickets de balanza.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from cuentas.models import cuenta


class TipoCamion(models.Model):
    """Tipos de camiones para categorización."""
    id_tipo_camion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(max_length=200, blank=True)
    capacidad_maxima = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text='Capacidad máxima en toneladas'
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Camión'
        verbose_name_plural = 'Tipos de Camión'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.capacidad_maxima}t)"


class Camion(models.Model):
    """Modelo simplificado para camiones de transporte."""
    
    id_camion = models.AutoField(primary_key=True)
    
    # Información básica (solo lo esencial)
    patente = models.CharField(max_length=10, unique=True, help_text='Patente del camión')
    
    # Acoplados (opcional)
    acoplado_1 = models.CharField(max_length=10, blank=True, help_text='Patente del primer acoplado')
    acoplado_2 = models.CharField(max_length=10, blank=True, help_text='Patente del segundo acoplado')
    
    # Capacidades
    capacidad_carga = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Capacidad de carga en toneladas'
    )
    tara = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Tara del camión en toneladas'
    )
    
    # Cuenta asociada (obligatorio)
    cuenta_asociada = models.ForeignKey(
        cuenta,
        on_delete=models.PROTECT,
        help_text='Cuenta/empresa propietaria del camión'
    )
    
    # Documentación (opcional, puede ser null)
    fecha_vencimiento_vtv = models.DateField(null=True, blank=True)
    fecha_vencimiento_seguro = models.DateField(null=True, blank=True)
    numero_poliza = models.CharField(max_length=50, blank=True)
    
    # Control
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, help_text='Observaciones adicionales')
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Camión'
        verbose_name_plural = 'Camiones'
        ordering = ['patente']
        indexes = [
            models.Index(fields=['patente']),
            models.Index(fields=['cuenta_asociada']),
        ]
    
    def __str__(self):
        acoplados = []
        if self.acoplado_1:
            acoplados.append(self.acoplado_1)
        if self.acoplado_2:
            acoplados.append(self.acoplado_2)
        
        if acoplados:
            return f"{self.patente} + {' + '.join(acoplados)}"
        return self.patente
    
    @property
    def conjunto_completo(self):
        """Retorna el conjunto completo de vehículos."""
        conjunto = [self.patente]
        if self.acoplado_1:
            conjunto.append(self.acoplado_1)
        if self.acoplado_2:
            conjunto.append(self.acoplado_2)
        return " + ".join(conjunto)
    
    @property
    def vtv_vencida(self):
        """Verifica si la VTV está vencida."""
        if self.fecha_vencimiento_vtv:
            return self.fecha_vencimiento_vtv < timezone.now().date()
        return False  # Si no hay fecha, asumimos que está ok
    
    @property
    def seguro_vencido(self):
        """Verifica si el seguro está vencido."""
        if self.fecha_vencimiento_seguro:
            return self.fecha_vencimiento_seguro < timezone.now().date()
        return False  # Si no hay fecha, asumimos que está ok
    
    @property
    def documentacion_ok(self):
        """Verifica si la documentación está al día."""
        return not self.vtv_vencida and not self.seguro_vencido


class Chofer(models.Model):
    """Modelo para choferes."""
    
    TIPO_LICENCIA_CHOICES = [
        ('A1', 'Licencia A1'),
        ('A2', 'Licencia A2'),
        ('A3', 'Licencia A3'),
        ('B1', 'Licencia B1'),
        ('B2', 'Licencia B2'),
        ('C1', 'Licencia C1'),
        ('C2', 'Licencia C2'),
        ('D1', 'Licencia D1'),
        ('D2', 'Licencia D2'),
        ('D3', 'Licencia D3'),
        ('E1', 'Licencia E1'),
        ('E2', 'Licencia E2'),
        ('E3', 'Licencia E3'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_viaje', 'En Viaje'),
        ('descanso', 'En Descanso'),
        ('vacaciones', 'De Vacaciones'),
        ('licencia', 'Con Licencia'),
        ('suspendido', 'Suspendido'),
    ]
    
    id_chofer = models.AutoField(primary_key=True)
    
    # Información personal
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    direccion = models.TextField(max_length=200)
    
    # Información laboral
    legajo = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField()
    tipo_licencia = models.CharField(max_length=5, choices=TIPO_LICENCIA_CHOICES)
    numero_licencia = models.CharField(max_length=20)
    fecha_vencimiento_licencia = models.DateField()
    
    # Estado y disponibilidad
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='disponible')
    camion_asignado = models.ForeignKey(
        Camion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Camión habitualmente asignado a este chofer'
    )
    
    # Datos de emergencia
    contacto_emergencia_nombre = models.CharField(max_length=100)
    contacto_emergencia_telefono = models.CharField(max_length=20)
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Chofer'
        verbose_name_plural = 'Choferes'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['legajo']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.legajo})"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def licencia_vencida(self):
        """Verifica si la licencia está vencida."""
        return self.fecha_vencimiento_licencia < timezone.now().date()
    
    @property
    def puede_manejar(self):
        """Verifica si el chofer puede manejar (licencia vigente)."""
        return not self.licencia_vencida and self.activo and self.estado in ['disponible', 'en_viaje']


class Viaje(models.Model):
    """Modelo para registrar viajes y rutas."""
    
    ESTADO_CHOICES = [
        ('planificado', 'Planificado'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('demorado', 'Demorado'),
    ]
    
    TIPO_CARGA_CHOICES = [
        ('carga', 'Carga'),
        ('descarga', 'Descarga'),
        ('traslado', 'Traslado'),
        ('retorno_vacio', 'Retorno Vacío'),
    ]
    
    id_viaje = models.AutoField(primary_key=True)
    
    # Información básica
    numero_viaje = models.CharField(max_length=20, unique=True)
    fecha_programada = models.DateTimeField()
    fecha_inicio_real = models.DateTimeField(null=True, blank=True)
    fecha_fin_real = models.DateTimeField(null=True, blank=True)
    
    # Recursos asignados
    camion = models.ForeignKey(Camion, on_delete=models.PROTECT)
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT)
    
    # Origen y destino
    origen = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    distancia_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Información de carga
    tipo_carga = models.CharField(max_length=15, choices=TIPO_CARGA_CHOICES)
    descripcion_carga = models.TextField(blank=True)
    peso_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Peso estimado en toneladas'
    )
    peso_real = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Peso real medido en balanza'
    )
    
    # Cliente y facturación
    cliente = models.ForeignKey(
        cuenta,
        on_delete=models.PROTECT,
        help_text='Cliente que solicita el transporte'
    )
    precio_acordado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Estado y control
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='planificado')
    observaciones = models.TextField(blank=True)
    
    # Control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Viaje'
        verbose_name_plural = 'Viajes'
        ordering = ['-fecha_programada']
        indexes = [
            models.Index(fields=['numero_viaje']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['camion']),
            models.Index(fields=['chofer']),
        ]
    
    def __str__(self):
        return f"Viaje {self.numero_viaje} - {self.origen} → {self.destino}"
    
    @property
    def duracion_estimada(self):
        """Duración estimada del viaje en horas."""
        if self.distancia_km:
            # Asumiendo velocidad promedio de 60 km/h
            return float(self.distancia_km) / 60
        return None
    
    @property
    def duracion_real(self):
        """Duración real del viaje."""
        if self.fecha_inicio_real and self.fecha_fin_real:
            delta = self.fecha_fin_real - self.fecha_inicio_real
            return round(delta.total_seconds() / 3600, 2)  # en horas
        return None
    
    @property
    def esta_en_curso(self):
        """Verifica si el viaje está en curso."""
        return self.estado == 'en_curso'
    
    @property
    def puede_iniciar(self):
        """Verifica si el viaje puede iniciarse."""
        return (self.estado == 'planificado' and 
                self.camion.puede_circular and 
                self.chofer.puede_manejar)


class TicketBalanza(models.Model):
    """Modelo para tickets de balanza (pesajes)."""
    
    TIPO_PESAJE_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('control', 'Control'),
    ]
    
    id_ticket = models.AutoField(primary_key=True)
    
    # Información básica
    numero_ticket = models.CharField(max_length=20, unique=True)
    fecha_pesaje = models.DateTimeField(default=timezone.now)
    tipo_pesaje = models.CharField(max_length=10, choices=TIPO_PESAJE_CHOICES)
    
    # Vehículo y conductor
    camion = models.ForeignKey(Camion, on_delete=models.PROTECT)
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT)
    viaje = models.ForeignKey(
        Viaje, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text='Viaje al que corresponde este pesaje'
    )
    
    # Datos del pesaje
    peso_bruto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Peso bruto en kilogramos'
    )
    peso_tara = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        help_text='Peso de la tara en kilogramos'
    )
    peso_neto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Peso neto en kilogramos'
    )
    
    # Información adicional
    producto = models.CharField(max_length=100)
    cliente_carga = models.ForeignKey(
        cuenta,
        on_delete=models.PROTECT,
        help_text='Cliente de la carga'
    )
    destino_carga = models.CharField(max_length=200)
    
    # Observaciones y control
    observaciones = models.TextField(blank=True)
    balanza_operador = models.CharField(max_length=100)
    
    # Control del sistema
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Ticket de Balanza'
        verbose_name_plural = 'Tickets de Balanza'
        ordering = ['-fecha_pesaje']
        indexes = [
            models.Index(fields=['numero_ticket']),
            models.Index(fields=['fecha_pesaje']),
            models.Index(fields=['camion']),
            models.Index(fields=['tipo_pesaje']),
        ]
    
    def __str__(self):
        return f"Ticket {self.numero_ticket} - {self.camion.patente} ({self.fecha_pesaje.strftime('%d/%m/%Y %H:%M')})"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el peso neto al guardar."""
        self.peso_neto = self.peso_bruto - self.peso_tara
        super().save(*args, **kwargs)
    
    @property
    def peso_neto_toneladas(self):
        """Retorna el peso neto en toneladas."""
        return float(self.peso_neto) / 1000
    
    @property
    def peso_bruto_toneladas(self):
        """Retorna el peso bruto en toneladas."""
        return float(self.peso_bruto) / 1000
