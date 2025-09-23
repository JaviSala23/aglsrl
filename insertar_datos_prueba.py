#!/usr/bin/env python
"""
Script para insertar datos de prueba en las tablas maestras
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from cuentas.models import tipo_documento, tipo_cuenta, situacionIva, pais, provincia

def insertar_datos():
    print("Insertando datos de prueba...")
    
    # Tipos de documento
    tipos_doc = [
        {'descripcion': 'DNI', 'cod_afip': 96},
        {'descripcion': 'CUIT', 'cod_afip': 80},
        {'descripcion': 'CUIL', 'cod_afip': 86},
        {'descripcion': 'Pasaporte', 'cod_afip': 94},
    ]
    
    for tipo_data in tipos_doc:
        tipo_doc, created = tipo_documento.objects.get_or_create(
            descripcion=tipo_data['descripcion'],
            defaults={'cod_afip': tipo_data['cod_afip']}
        )
        if created:
            print(f"✅ Creado tipo documento: {tipo_doc.descripcion}")
        else:
            print(f"⚠️  Ya existe tipo documento: {tipo_doc.descripcion}")
    
    # Tipos de cuenta
    tipos_cuenta_data = [
        {'descripcion': 'Cliente'},
        {'descripcion': 'Proveedor'},
        {'descripcion': 'Cliente y Proveedor'},
        {'descripcion': 'Empleado'},
    ]
    
    for tipo_data in tipos_cuenta_data:
        tipo_cta, created = tipo_cuenta.objects.get_or_create(
            descripcion=tipo_data['descripcion']
        )
        if created:
            print(f"✅ Creado tipo cuenta: {tipo_cta.descripcion}")
        else:
            print(f"⚠️  Ya existe tipo cuenta: {tipo_cta.descripcion}")
    
    # Situaciones de IVA
    situaciones_iva_data = [
        {'descripcion': 'IVA Responsable Inscripto', 'reducida': 'RI', 'codigo_afip': 1},
        {'descripcion': 'IVA Responsable no Inscripto', 'reducida': 'RNI', 'codigo_afip': 2},
        {'descripcion': 'IVA no Responsable', 'reducida': 'NR', 'codigo_afip': 3},
        {'descripcion': 'IVA Sujeto Exento', 'reducida': 'EX', 'codigo_afip': 4},
        {'descripcion': 'Consumidor Final', 'reducida': 'CF', 'codigo_afip': 5},
        {'descripcion': 'Responsable Monotributo', 'reducida': 'MT', 'codigo_afip': 6},
        {'descripcion': 'Sujeto no Categorizado', 'reducida': 'NC', 'codigo_afip': 7},
    ]
    
    for sit_data in situaciones_iva_data:
        situacion, created = situacionIva.objects.get_or_create(
            codigo_afip=sit_data['codigo_afip'],
            defaults={
                'descripcion': sit_data['descripcion'],
                'reducida': sit_data['reducida']
            }
        )
        if created:
            print(f"✅ Creada situación IVA: {situacion.descripcion}")
        else:
            print(f"⚠️  Ya existe situación IVA: {situacion.descripcion}")
    
    # Países
    pais_arg, created = pais.objects.get_or_create(
        nombre='Argentina'
    )
    if created:
        print(f"✅ Creado país: {pais_arg.nombre}")
    else:
        print(f"⚠️  Ya existe país: {pais_arg.nombre}")
    
    # Provincias de Argentina
    provincias_data = [
        {'nombre_provincia': 'Buenos Aires', 'codigo_provincia': 'BA'},
        {'nombre_provincia': 'Catamarca', 'codigo_provincia': 'CT'},
        {'nombre_provincia': 'Chaco', 'codigo_provincia': 'CC'},
        {'nombre_provincia': 'Chubut', 'codigo_provincia': 'CB'},
        {'nombre_provincia': 'Córdoba', 'codigo_provincia': 'CB'},
        {'nombre_provincia': 'Corrientes', 'codigo_provincia': 'CR'},
        {'nombre_provincia': 'Entre Ríos', 'codigo_provincia': 'ER'},
        {'nombre_provincia': 'Formosa', 'codigo_provincia': 'FO'},
        {'nombre_provincia': 'Jujuy', 'codigo_provincia': 'JY'},
        {'nombre_provincia': 'La Pampa', 'codigo_provincia': 'LP'},
        {'nombre_provincia': 'La Rioja', 'codigo_provincia': 'LR'},
        {'nombre_provincia': 'Mendoza', 'codigo_provincia': 'MZ'},
        {'nombre_provincia': 'Misiones', 'codigo_provincia': 'MN'},
        {'nombre_provincia': 'Neuquén', 'codigo_provincia': 'NQ'},
        {'nombre_provincia': 'Río Negro', 'codigo_provincia': 'RN'},
        {'nombre_provincia': 'Salta', 'codigo_provincia': 'SA'},
        {'nombre_provincia': 'San Juan', 'codigo_provincia': 'SJ'},
        {'nombre_provincia': 'San Luis', 'codigo_provincia': 'SL'},
        {'nombre_provincia': 'Santa Cruz', 'codigo_provincia': 'SC'},
        {'nombre_provincia': 'Santa Fe', 'codigo_provincia': 'SF'},
        {'nombre_provincia': 'Santiago del Estero', 'codigo_provincia': 'SE'},
        {'nombre_provincia': 'Tierra del Fuego', 'codigo_provincia': 'TF'},
        {'nombre_provincia': 'Tucumán', 'codigo_provincia': 'TM'},
        {'nombre_provincia': 'Ciudad Autónoma de Buenos Aires', 'codigo_provincia': 'CABA'},
    ]
    
    for prov_data in provincias_data:
        provincia_obj, created = provincia.objects.get_or_create(
            nombre_provincia=prov_data['nombre_provincia'],
            defaults={
                'codigo_provincia': prov_data['codigo_provincia'],
                'pais_idpais': pais_arg
            }
        )
        if created:
            print(f"✅ Creada provincia: {provincia_obj.nombre_provincia}")
        else:
            print(f"⚠️  Ya existe provincia: {provincia_obj.nombre_provincia}")
    
    print("\n🎉 ¡Datos de prueba insertados correctamente!")
    
    # Mostrar resumen
    print(f"\n📊 Resumen:")
    print(f"   - Tipos de documento: {tipo_documento.objects.count()}")
    print(f"   - Tipos de cuenta: {tipo_cuenta.objects.count()}")
    print(f"   - Situaciones IVA: {situacionIva.objects.count()}")
    print(f"   - Países: {pais.objects.count()}")
    print(f"   - Provincias: {provincia.objects.count()}")

if __name__ == '__main__':
    insertar_datos()