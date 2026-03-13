
"""
Carga masiva de tablas de configuración:
- Tipos de cuenta (tipo_cuenta)
- Tipos de movimiento (TipoMovimiento)
- Tipos de mercadería (Grano)

Ejecutar con el entorno virtual activado y Django configurado.
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from cuentas.models import tipo_cuenta, tipo_documento, situacionIva, pais, provincia, localidad
from tickets.models import TipoMovimiento
from mercaderias.models import Grano

# Tipos de cuenta
tipos_cuenta = [
    'Cliente',
    'Proveedor',
    'Transportista',
]
for desc in tipos_cuenta:
    obj, created = tipo_cuenta.objects.get_or_create(descripcion=desc)
    print(f"{'✔️' if created else '➖'} tipo_cuenta: {desc}")

# Tipos de movimiento
movimientos = [
    dict(codigo='REC', nombre='Recibido', descripcion='Recepción de mercadería', activo=True, requiere_origen=False, requiere_destinatario=True),
    dict(codigo='ENV', nombre='Enviado', descripcion='Envío de mercadería', activo=True, requiere_origen=True, requiere_destinatario=False),
]
for m in movimientos:
    obj, created = TipoMovimiento.objects.get_or_create(codigo=m['codigo'], defaults=m)
    print(f"{'✔️' if created else '➖'} TipoMovimiento: {m['nombre']}")

# Tipos de mercadería (Granos de ejemplo)
granos = [
    dict(nombre='Soja', codigo='SOJ', descripcion='Soja común'),
    dict(nombre='Maíz', codigo='MAI', descripcion='Maíz amarillo'),
    dict(nombre='Trigo', codigo='TRI', descripcion='Trigo pan'),
]
for g in granos:
    obj, created = Grano.objects.get_or_create(nombre=g['nombre'], defaults=g)
    print(f"{'✔️' if created else '➖'} Grano: {g['nombre']}")

# Tipos de documento
tipos_documento = [
    dict(descripcion='DNI', cod_afip=96),
    dict(descripcion='CUIT', cod_afip=80),
    dict(descripcion='CUIL', cod_afip=86),
    dict(descripcion='Pasaporte', cod_afip=94),
]
for td in tipos_documento:
    obj, created = tipo_documento.objects.get_or_create(descripcion=td['descripcion'], defaults={'cod_afip': td['cod_afip']})
    print(f"{'✔️' if created else '➖'} tipo_documento: {td['descripcion']}")

# Situaciones de IVA
situaciones_iva = [
    dict(descripcion='Responsable Inscripto', codigo_afip=1),
    dict(descripcion='Monotributista', codigo_afip=6),
    dict(descripcion='Exento', codigo_afip=4),
    dict(descripcion='Consumidor Final', codigo_afip=5),
]
for si in situaciones_iva:
    obj, created = situacionIva.objects.get_or_create(descripcion=si['descripcion'], defaults={'codigo_afip': si['codigo_afip']})
    print(f"{'✔️' if created else '➖'} situacionIva: {si['descripcion']}")

# Países, provincias y localidades de ejemplo
pais_arg, _ = pais.objects.get_or_create(nombre='Argentina')
prov_bsas, _ = provincia.objects.get_or_create(nombre_provincia='Buenos Aires', codigo_provincia='BA', pais_idpais=pais_arg)
prov_cba, _ = provincia.objects.get_or_create(nombre_provincia='Córdoba', codigo_provincia='CB', pais_idpais=pais_arg)
loc_laplata, _ = localidad.objects.get_or_create(nombre_localidad='La Plata', cp_localidad='1900', provincia_id_provincia=prov_bsas)
loc_cordoba, _ = localidad.objects.get_or_create(nombre_localidad='Córdoba', cp_localidad='5000', provincia_id_provincia=prov_cba)
print(f"✔️ pais: Argentina\n✔️ provincia: Buenos Aires, Córdoba\n✔️ localidad: La Plata, Córdoba")

print('\nCarga de tablas de configuración completada.')
