from django.db import models

# Create your models here.
# Maestro de ubicaciones y clasificadores (adaptado a tus tablas existentes)
class pais(models.Model):
    id_pais = models.AutoField(primary_key=True)
    nombre = models.TextField(max_length=150)
    def __str__(self):
        return f"{self.nombre}"

class provincia(models.Model):
    id_provincia = models.AutoField(primary_key=True)
    nombre_provincia = models.TextField(max_length=150)
    codigo_provincia = models.TextField(max_length=6)
    pais_idpais = models.ForeignKey(pais, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.nombre_provincia}"

class localidad(models.Model):
    id_localidad = models.AutoField(primary_key=True)
    nombre_localidad = models.TextField(max_length=150)
    cp_localidad = models.TextField(max_length=10)
    provincia_id_provincia = models.ForeignKey(provincia, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.nombre_localidad}"

class tipo_documento(models.Model):
    idtipo_documento = models.AutoField(primary_key=True)
    descripcion = models.TextField(max_length=150)
    cod_afip = models.IntegerField()
    def __str__(self):
        return f"{self.descripcion}"

class situacionIva(models.Model):
    idsituacionIva = models.AutoField(primary_key=True)
    descripcion = models.TextField(null=True, blank=True, max_length=150)
    reducida = models.TextField(null=True, blank=True, max_length=10)
    codigo_afip = models.IntegerField(
        null=True, blank=True, unique=True,
        help_text="Código oficial AFIP para la situación de IVA",
    )
    def __str__(self):
        return f"{self.descripcion or ''} ({self.codigo_afip or '-'})"

class tipo_cuenta(models.Model):
    id_tipo_cuenta = models.AutoField(primary_key=True)
    descripcion = models.TextField(max_length=150)
    def __str__(self):
        return f"{self.descripcion}"

# ----------------------
# Cuentas (adaptado)
# ----------------------
class cuenta(models.Model):
    id_cuenta = models.AutoField(primary_key=True)

    # Facturación
    razon_social = models.TextField(max_length=150)  # requerido para facturar
    nombre_fantasia = models.TextField(max_length=150, null=True, blank=True)  # opcional

    # Identificación
    numero_documento = models.TextField(max_length=15)
    tipo_documento_idtipo_documento = models.ForeignKey(
        tipo_documento, on_delete=models.PROTECT, null=True, blank=False
    )

    # Dirección (simple por ahora; ver extensión Direccion[] más abajo)
    direccion_cuenta = models.TextField(max_length=200)
    pais_id = models.ForeignKey(pais, on_delete=models.PROTECT, null=True, blank=True)
    provincia_idprovincia = models.ForeignKey(provincia, on_delete=models.PROTECT, null=True)
    localidad_idlocalidad = models.ForeignKey(localidad, on_delete=models.PROTECT, null=True)

    # Contacto rápido
    telefono_cuenta = models.TextField(max_length=15, null=True, blank=True)
    celular_cuenta = models.TextField(max_length=15, null=True, blank=True)
    email_cuenta = models.TextField(max_length=150, null=True, blank=True)

    # Clasificación
    tipo_cuenta_id_tipo_cuenta = models.ForeignKey(tipo_cuenta, on_delete=models.PROTECT, null=True)
    situacionIva_idsituacionIva = models.ForeignKey(situacionIva, on_delete=models.PROTECT, null=True)

    # Estado
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_documento_idtipo_documento", "numero_documento"],
                name="uq_cuenta_doc",
            )
        ]
        indexes = [
            models.Index(fields=["razon_social"]),
            models.Index(fields=["numero_documento"]),
            models.Index(fields=["tipo_cuenta_id_tipo_cuenta"]),
        ]

    def __str__(self):
        return f"{self.numero_documento} - {self.razon_social}"

# ----------------------
# Agenda / Contactos centralizados por cuenta
# ----------------------
class contacto_cuenta(models.Model):
    id_contacto = models.AutoField(primary_key=True)
    cuenta_id = models.ForeignKey(cuenta, on_delete=models.CASCADE, related_name="contactos")

    nombre = models.TextField(max_length=150)
    cargo = models.TextField(max_length=120, null=True, blank=True)
    email = models.TextField(max_length=150, null=True, blank=True)
    telefono = models.TextField(max_length=40, null=True, blank=True)
    celular = models.TextField(max_length=40, null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# ----------------------
# (Opcional futurible) Múltiples direcciones por cuenta
# ----------------------
class direccion(models.Model):
    id_direccion = models.AutoField(primary_key=True)
    cuenta_id = models.ForeignKey(cuenta, on_delete=models.CASCADE, related_name="direcciones")

    etiqueta = models.TextField(max_length=60, null=True, blank=True)  # Fiscal / Comercial / Depósito
    calle = models.TextField(max_length=200)
    numero = models.TextField(max_length=20, null=True, blank=True)
    piso = models.TextField(max_length=10, null=True, blank=True)
    dpto = models.TextField(max_length=10, null=True, blank=True)

    pais_id = models.ForeignKey(pais, on_delete=models.PROTECT, null=True, blank=True)
    provincia_idprovincia = models.ForeignKey(provincia, on_delete=models.PROTECT, null=True)
    localidad_idlocalidad = models.ForeignKey(localidad, on_delete=models.PROTECT, null=True)
    cp = models.TextField(max_length=10, null=True, blank=True)

    es_principal = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cuenta_id"],
                condition=models.Q(es_principal=True),
                name="uq_direccion_principal_por_cuenta",
            )
        ]

    def __str__(self):
        return f"{self.calle} {self.numero or ''}"