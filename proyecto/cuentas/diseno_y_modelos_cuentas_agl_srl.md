# Diseño de **Cuentas** para CRUD (agl srl)

> Objetivo: Definir un modelo de datos simple y extensible para gestionar **cuentas** (Cliente, Proveedor, Transportista, Propia) y su **agenda/contacts** centralizada, sin acoplar roles operativos que corresponden a los **tickets** (remitente comercial, origen, destinatario, destino, etc.).

---

## Alcance
- **Incluye:** modelos Django, relaciones, validaciones básicas, administración y endpoints CRUD (DRF).
- **No incluye:** lógica de tickets (solo se referencia cómo se vinculan), contabilidad, facturación o impuestos avanzados.

---

## Modelo de datos (UML textual)
```
Cuenta (1) ───< Direccion (N)
   │             └─ campos de ubicación normalizados
   └──< Contacto (N)

Cuenta [tipo=CLIENTE|PROVEEDOR|TRANSPORTISTA|PROPIA]

Si tipo == TRANSPORTISTA (opcional, extensible):
   Cuenta (1) ───< Vehiculo (N)
   Cuenta (1) ───< Chofer   (N)
```

> Los **roles del ticket** (remitente comercial, origen, destinatario, destino, remitente) **NO** se modelan en `Cuenta`. Se asignan en el **Ticket** con FKs a `Cuenta`.

![Diagrama de cuentas](proyecto/cuentas/bd_cuenta.png)

---

## Campos propuestos
### `Cuenta`
- `id`
- `tipo` (choices: CLIENTE, PROVEEDOR, TRANSPORTISTA, PROPIA)
- `razon_social` (**requerido**)
- `nombre_fantasia` (opcional)
- `doc_tipo` (choices: CUIT, CUIL, DNI, PAS)
- `doc_numero`
- `iibb` (opcional)
- `condicion_iva` (choices: RI, Monotributo, Exento, CF)
- `email`, `telefono`
- `observaciones` (Text)
- `activo` (bool, default True)
- `fecha_alta`, `fecha_baja`

### `Direccion`
- `cuenta` (FK)
- `calle`, `numero`, `piso`, `dpto`
- `localidad`, `provincia`, `pais`, `cp`
- `lat`, `lng` (Decimal)
- `es_principal` (bool)

### `Contacto`
- `cuenta` (FK)
- `nombre` (requerido)
- `cargo`
- `email`, `telefono`
- `notas`
- `activo` (bool)

### (Opcional) `Vehiculo` y `Chofer` para Transportistas
- `Vehiculo`: `cuenta`, `dominio`, `tipo`, `marca`, `modelo`, `anio`, `capacidad_kg`, `activo`
- `Chofer`: `cuenta`, `nombre`, `dni`, `licencia`, `telefono`, `activo`

---

## Reglas y validaciones
- **Unicidad** documental: `(doc_tipo, doc_numero)` único cuando ambos no son nulos.
- **Soft delete** por `activo` + `fecha_baja`.
- `Direccion.es_principal` única por cuenta (a lo sumo una principal).
- Si `tipo=TRANSPORTISTA`, `Vehiculo`/`Chofer` habilitados pero **no obligatorios**.

---

## Django: `models.py`
```python
from django.db import models

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
```

---

## DRF: serializers y viewsets (adaptados)
```python
# serializers.py
from rest_framework import serializers
from .models import (
    pais, provincia, localidad, tipo_documento, situacionIva, tipo_cuenta,
    cuenta, contacto_cuenta, direccion,
)

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = pais
        fields = "__all__"

class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = provincia
        fields = "__all__"

class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = localidad
        fields = "__all__"

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = tipo_documento
        fields = "__all__"

class SituacionIvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = situacionIva
        fields = "__all__"

class TipoCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = tipo_cuenta
        fields = "__all__"

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = direccion
        fields = "__all__"

class ContactoCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = contacto_cuenta
        fields = "__all__"

class CuentaSerializer(serializers.ModelSerializer):
    contactos = ContactoCuentaSerializer(many=True, read_only=True)
    direcciones = DireccionSerializer(many=True, read_only=True)

    class Meta:
        model = cuenta
        fields = "__all__"
```

```python
# views.py
from rest_framework import viewsets, filters
from .models import (
    pais, provincia, localidad, tipo_documento, situacionIva, tipo_cuenta,
    cuenta, contacto_cuenta, direccion,
)
from .serializers import (
    PaisSerializer, ProvinciaSerializer, LocalidadSerializer,
    TipoDocumentoSerializer, SituacionIvaSerializer, TipoCuentaSerializer,
    CuentaSerializer, ContactoCuentaSerializer, DireccionSerializer,
)

class BaseSearchMixin:
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

class PaisViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = pais.objects.all().order_by('nombre')
    serializer_class = PaisSerializer
    search_fields = ['nombre']

class ProvinciaViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = provincia.objects.all().order_by('nombre_provincia')
    serializer_class = ProvinciaSerializer
    search_fields = ['nombre_provincia', 'codigo_provincia']

class LocalidadViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = localidad.objects.all().order_by('nombre_localidad')
    serializer_class = LocalidadSerializer
    search_fields = ['nombre_localidad', 'cp_localidad']

class TipoDocumentoViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = tipo_documento.objects.all()
    serializer_class = TipoDocumentoSerializer
    search_fields = ['descripcion', 'cod_afip']

class SituacionIvaViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = situacionIva.objects.all()
    serializer_class = SituacionIvaSerializer
    search_fields = ['descripcion', 'codigo_afip']

class TipoCuentaViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = tipo_cuenta.objects.all()
    serializer_class = TipoCuentaSerializer
    search_fields = ['descripcion']

class CuentaViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = cuenta.objects.all().order_by('-id_cuenta')
    serializer_class = CuentaSerializer
    search_fields = ['razon_social', 'nombre_fantasia', 'numero_documento', 'email_cuenta', 'telefono_cuenta']
    ordering_fields = ['id_cuenta', 'razon_social']

class ContactoCuentaViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = contacto_cuenta.objects.all().order_by('-id_contacto')
    serializer_class = ContactoCuentaSerializer
    search_fields = ['nombre', 'email', 'telefono', 'celular']

class DireccionViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = direccion.objects.all().order_by('-id_direccion')
    serializer_class = DireccionSerializer
    search_fields = ['calle']
```

```python
# urls.py (extracto)
from rest_framework.routers import DefaultRouter
from .views import (
    PaisViewSet, ProvinciaViewSet, LocalidadViewSet,
    TipoDocumentoViewSet, SituacionIvaViewSet, TipoCuentaViewSet,
    CuentaViewSet, ContactoCuentaViewSet, DireccionViewSet,
)

router = DefaultRouter()
router.register(r'paises', PaisViewSet)
router.register(r'provincias', ProvinciaViewSet)
router.register(r'localidades', LocalidadViewSet)
router.register(r'tipos-documento', TipoDocumentoViewSet)
router.register(r'situaciones-iva', SituacionIvaViewSet)
router.register(r'tipos-cuenta', TipoCuentaViewSet)
router.register(r'cuentas', CuentaViewSet)
router.register(r'contactos', ContactoCuentaViewSet)
router.register(r'direcciones', DireccionViewSet)

urlpatterns = router.urls
```

---


## Administración (`admin.py`)
```python
from django.contrib import admin
from .models import Cuenta, Direccion, Contacto, Vehiculo, Chofer

class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 0

class ContactoInline(admin.TabularInline):
    model = Contacto
    extra = 0

class VehiculoInline(admin.TabularInline):
    model = Vehiculo
    extra = 0

class ChoferInline(admin.TabularInline):
    model = Chofer
    extra = 0

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "nombre_fantasia", "doc_tipo", "doc_numero", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre_fantasia", "razon_social", "doc_numero", "email", "telefono")
    inlines = [DireccionInline, ContactoInline, VehiculoInline, ChoferInline]

admin.site.register(Direccion)
admin.site.register(Contacto)
admin.site.register(Vehiculo)
admin.site.register(Chofer)
```

---

## DRF: serializers y viewsets
```python
# serializers.py
from rest_framework import serializers
from .models import Cuenta, Direccion, Contacto, Vehiculo, Chofer

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = "__all__"

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = "__all__"

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = "__all__"

class ChoferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chofer
        fields = "__all__"

class CuentaSerializer(serializers.ModelSerializer):
    direcciones = DireccionSerializer(many=True, read_only=True)
    contactos = ContactoSerializer(many=True, read_only=True)
    vehiculos = VehiculoSerializer(many=True, read_only=True)
    choferes = ChoferSerializer(many=True, read_only=True)

    class Meta:
        model = Cuenta
        fields = "__all__"

```

```python
# views.py
from rest_framework import viewsets, filters
from .models import Cuenta, Direccion, Contacto, Vehiculo, Chofer
from .serializers import (
    CuentaSerializer, DireccionSerializer, ContactoSerializer,
    VehiculoSerializer, ChoferSerializer,
)

class BaseSearchMixin:
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

class CuentaViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = Cuenta.objects.all().order_by('-id')
    serializer_class = CuentaSerializer
    search_fields = ['nombre_fantasia', 'razon_social', 'doc_numero', 'email', 'telefono']
    ordering_fields = ['id', 'nombre_fantasia', 'tipo']

class DireccionViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = Direccion.objects.all().order_by('-id')
    serializer_class = DireccionSerializer
    search_fields = ['calle', 'localidad', 'provincia']

class ContactoViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = Contacto.objects.all().order_by('-id')
    serializer_class = ContactoSerializer
    search_fields = ['nombre', 'cargo', 'email', 'telefono']

class VehiculoViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().order_by('-id')
    serializer_class = VehiculoSerializer
    search_fields = ['dominio', 'marca', 'modelo']

class ChoferViewSet(BaseSearchMixin, viewsets.ModelViewSet):
    queryset = Chofer.objects.all().order_by('-id')
    serializer_class = ChoferSerializer
    search_fields = ['nombre', 'dni', 'telefono']
```

```python
# urls.py (extracto)
from rest_framework.routers import DefaultRouter
from .views import (
    CuentaViewSet, DireccionViewSet, ContactoViewSet,
    VehiculoViewSet, ChoferViewSet,
)

router = DefaultRouter()
router.register(r'cuentas', CuentaViewSet)
router.register(r'direcciones', DireccionViewSet)
router.register(r'contactos', ContactoViewSet)
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'choferes', ChoferViewSet)

urlpatterns = router.urls
```

---

## Integración con Tickets (referencia)
En el modelo `Ticket`, agregar FKs a `Cuenta` **según el rol en la operación**:
```python
class Ticket(models.Model):
    remitente_comercial = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.PROTECT, related_name='tickets_remitente_comercial')
    remitente = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.PROTECT, related_name='tickets_remitente')
    origen = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.PROTECT, related_name='tickets_origen')
    destinatario = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.PROTECT, related_name='tickets_destinatario')
    destino = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.PROTECT, related_name='tickets_destino')
```
> Todos estos campos pueden apuntar a **Cuenta PROPIA** (ej. *AGL*) cuando corresponda.

---

## Semillas / pruebas rápidas (opcional)
```python
# shell_plus
from core.models import Cuenta
Cuenta.objects.create(tipo=Cuenta.Tipo.PROPIA, nombre_fantasia='AGL SRL', doc_tipo='CUIT', doc_numero='30-00000000-0')
Cuenta.objects.create(tipo=Cuenta.Tipo.CLIENTE, nombre_fantasia='Cliente Demo')
Cuenta.objects.create(tipo=Cuenta.Tipo.PROVEEDOR, nombre_fantasia='Proveedor Demo')
Cuenta.objects.create(tipo=Cuenta.Tipo.TRANSPORTISTA, nombre_fantasia='Transporte Demo')
```






---

## Notas de implementación
- Mantener **roles de ticket fuera de Cuenta** para evitar acoplamiento y permitir combinaciones libres en cada operación.
- `on_delete=PROTECT` en FKs desde `Ticket` para conservar integridad histórica.
- Indexar búsquedas frecuentes: `nombre_fantasia`, `doc_numero`, `tipo`.
- Extensiones futuras: cuentas bancarias, archivos adjuntos, etiquetas por industria.

---

## Próximos pasos
1. Ejecutar migraciones y registrar en admin.
2. Conectar rutas DRF y probar CRUD desde Postman.
3. Integrar selector de cuenta en formularios de Tickets (autocompletar y filtros por tipo).





