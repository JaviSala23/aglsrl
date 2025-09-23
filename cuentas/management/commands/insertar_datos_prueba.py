from django.core.management.base import BaseCommand
from cuentas.models import tipo_documento, tipo_cuenta, situacionIva, pais, provincia

class Command(BaseCommand):
    help = 'Insertar datos de prueba en las tablas maestras'

    def handle(self, *args, **options):
        self.stdout.write("Insertando datos de prueba...")
        
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
                self.stdout.write(f"✅ Creado tipo documento: {tipo_doc.descripcion}")
            else:
                self.stdout.write(f"⚠️  Ya existe tipo documento: {tipo_doc.descripcion}")
        
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
                self.stdout.write(f"✅ Creado tipo cuenta: {tipo_cta.descripcion}")
            else:
                self.stdout.write(f"⚠️  Ya existe tipo cuenta: {tipo_cta.descripcion}")
        
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
                self.stdout.write(f"✅ Creada situación IVA: {situacion.descripcion}")
            else:
                self.stdout.write(f"⚠️  Ya existe situación IVA: {situacion.descripcion}")
        
        # Países
        pais_arg, created = pais.objects.get_or_create(
            nombre='Argentina'
        )
        if created:
            self.stdout.write(f"✅ Creado país: {pais_arg.nombre}")
        else:
            self.stdout.write(f"⚠️  Ya existe país: {pais_arg.nombre}")
        
        # Provincias de Argentina (solo algunas principales)
        provincias_data = [
            {'nombre_provincia': 'Buenos Aires', 'codigo_provincia': 'BA'},
            {'nombre_provincia': 'Córdoba', 'codigo_provincia': 'CB'},
            {'nombre_provincia': 'Santa Fe', 'codigo_provincia': 'SF'},
            {'nombre_provincia': 'Ciudad Autónoma de Buenos Aires', 'codigo_provincia': 'CABA'},
            {'nombre_provincia': 'Mendoza', 'codigo_provincia': 'MZ'},
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
                self.stdout.write(f"✅ Creada provincia: {provincia_obj.nombre_provincia}")
            else:
                self.stdout.write(f"⚠️  Ya existe provincia: {provincia_obj.nombre_provincia}")
        
        self.stdout.write("\n🎉 ¡Datos de prueba insertados correctamente!")
        
        # Mostrar resumen
        self.stdout.write(f"\n📊 Resumen:")
        self.stdout.write(f"   - Tipos de documento: {tipo_documento.objects.count()}")
        self.stdout.write(f"   - Tipos de cuenta: {tipo_cuenta.objects.count()}")
        self.stdout.write(f"   - Situaciones IVA: {situacionIva.objects.count()}")
        self.stdout.write(f"   - Países: {pais.objects.count()}")
        self.stdout.write(f"   - Provincias: {provincia.objects.count()}")