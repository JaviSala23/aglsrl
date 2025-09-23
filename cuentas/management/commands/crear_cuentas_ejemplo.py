"""
Comando para crear cuentas de ejemplo para testing.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from cuentas.models import (
    cuenta, tipo_cuenta, tipo_documento, situacionIva,
    pais, provincia, localidad, contacto_cuenta, direccion
)


class Command(BaseCommand):
    help = 'Crea cuentas de ejemplo para testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=10,
            help='Cantidad de cuentas de ejemplo a crear (default: 10)',
        )
    
    def handle(self, *args, **options):
        """Crear cuentas de ejemplo."""
        cantidad = options['cantidad']
        
        self.stdout.write(
            self.style.SUCCESS(f'Creando {cantidad} cuentas de ejemplo...')
        )
        
        try:
            with transaction.atomic():
                self._crear_cuenta_propia()
                self._crear_cuentas_ejemplo(cantidad - 1)
            
            self.stdout.write(
                self.style.SUCCESS('¡Cuentas de ejemplo creadas exitosamente!')
            )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear cuentas de ejemplo: {e}')
            )
            raise
    
    def _crear_cuenta_propia(self):
        """Crear cuenta propia de la empresa AGL SRL."""
        try:
            # Obtener datos maestros
            tipo_propia = tipo_cuenta.objects.get(descripcion='Propia')
            tipo_cuit = tipo_documento.objects.get(descripcion='CUIT')
            situacion_ri = situacionIva.objects.get(reducida='RI')
            argentina = pais.objects.get(nombre='Argentina')
            cordoba_prov = provincia.objects.get(nombre_provincia='Córdoba')
            cordoba_city = localidad.objects.get(nombre_localidad='Córdoba')
            
            # Crear cuenta propia
            cuenta_propia, created = cuenta.objects.get_or_create(
                numero_documento='30-71234567-8',
                defaults={
                    'razon_social': 'AGL S.R.L.',
                    'nombre_fantasia': 'AGL Transporte y Logística',
                    'tipo_documento_idtipo_documento': tipo_cuit,
                    'direccion_cuenta': 'Av. Colón 1234',
                    'pais_id': argentina,
                    'provincia_idprovincia': cordoba_prov,
                    'localidad_idlocalidad': cordoba_city,
                    'telefono_cuenta': '0351-4567890',
                    'celular_cuenta': '351-155-123456',
                    'email_cuenta': 'administracion@agl.com.ar',
                    'tipo_cuenta_id_tipo_cuenta': tipo_propia,
                    'situacionIva_idsituacionIva': situacion_ri,
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(f'  Cuenta propia creada: {cuenta_propia.razon_social}')
                
                # Crear contacto principal
                contacto_cuenta.objects.create(
                    cuenta_id=cuenta_propia,
                    nombre='Juan Pérez',
                    cargo='Gerente General',
                    email='gerencia@agl.com.ar',
                    telefono='0351-4567890',
                    celular='351-155-123456',
                    activo=True
                )
                
                # Crear dirección principal
                direccion.objects.create(
                    cuenta_id=cuenta_propia,
                    etiqueta='Sede Central',
                    calle='Av. Colón',
                    numero='1234',
                    pais_id=argentina,
                    provincia_idprovincia=cordoba_prov,
                    localidad_idlocalidad=cordoba_city,
                    cp='X5000ABC',
                    es_principal=True
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'No se pudo crear cuenta propia: {e}')
            )
    
    def _crear_cuentas_ejemplo(self, cantidad):
        """Crear cuentas de ejemplo con datos realistas."""
        cuentas_data = [
            {
                'razon_social': 'METALÚRGICA SAN MARTÍN S.A.',
                'nombre_fantasia': 'Metalúrgica San Martín',
                'tipo_cuenta': 'Cliente',
                'cuit': '30-56789012-3',
                'situacion_iva': 'RI',
                'email': 'ventas@metalurgicasm.com.ar',
                'telefono': '0351-4234567',
            },
            {
                'razon_social': 'TRANSPORTES DEL SUR S.R.L.',
                'nombre_fantasia': 'Transportes del Sur',
                'tipo_cuenta': 'Transportista',
                'cuit': '30-67890123-4',
                'situacion_iva': 'RI',
                'email': 'operaciones@transportesdelsur.com',
                'telefono': '0351-4345678',
            },
            {
                'razon_social': 'AGRO SERVICIOS LA PAMPA S.A.',
                'nombre_fantasia': 'Agro Servicios La Pampa',
                'tipo_cuenta': 'Proveedor',
                'cuit': '30-78901234-5',
                'situacion_iva': 'RI',
                'email': 'compras@agroslavampa.com.ar',
                'telefono': '02954-456789',
            },
            {
                'razon_social': 'JUAN CARLOS GONZÁLEZ',
                'nombre_fantasia': 'Fletes González',
                'tipo_cuenta': 'Transportista',
                'cuit': '20-12345678-9',
                'situacion_iva': 'MONO',
                'email': 'fletasgonzalez@gmail.com',
                'telefono': '351-155-987654',
            },
            {
                'razon_social': 'INDUSTRIAS QUÍMICAS DEL NORTE S.A.',
                'nombre_fantasia': 'IQ Norte',
                'tipo_cuenta': 'Cliente',
                'cuit': '30-89012345-6',
                'situacion_iva': 'RI',
                'email': 'logistica@iqnorte.com.ar',
                'telefono': '0387-4567890',
            },
            {
                'razon_social': 'MARÍA EUGENIA TORRES',
                'nombre_fantasia': 'Distribuciones Torres',
                'tipo_cuenta': 'Cliente',
                'cuit': '27-23456789-0',
                'situacion_iva': 'MONO',
                'email': 'distribuciones.torres@outlook.com',
                'telefono': '351-155-234567',
            },
            {
                'razon_social': 'COMBUSTIBLES Y LUBRICANTES S.R.L.',
                'nombre_fantasia': 'CombuLub',
                'tipo_cuenta': 'Proveedor',
                'cuit': '30-90123456-7',
                'situacion_iva': 'RI',
                'email': 'administracion@combulub.com.ar',
                'telefono': '0341-4678901',
            },
            {
                'razon_social': 'COOPERATIVA DE TRABAJO UNIÓN LTDA.',
                'nombre_fantasia': 'Coop. Unión',
                'tipo_cuenta': 'Transportista',
                'cuit': '30-01234567-8',
                'situacion_iva': 'EX',
                'email': 'coordinacion@coopunion.org.ar',
                'telefono': '0299-4789012',
            },
            {
                'razon_social': 'PEDRO LÓPEZ E HIJOS S.A.',
                'nombre_fantasia': 'López Hnos.',
                'tipo_cuenta': 'Cliente y Proveedor',
                'cuit': '30-12345678-0',
                'situacion_iva': 'RI',
                'email': 'contacto@lopezhnos.com',
                'telefono': '0261-4890123',
            }
        ]
        
        # Obtener datos maestros
        try:
            argentina = pais.objects.get(nombre='Argentina')
            cordoba_prov = provincia.objects.get(nombre_provincia='Córdoba')
            cordoba_city = localidad.objects.get(nombre_localidad='Córdoba')
            tipo_cuit = tipo_documento.objects.get(descripcion='CUIT')
            
            created_count = 0
            for i, cuenta_data in enumerate(cuentas_data[:cantidad]):
                try:
                    # Obtener referencias
                    tipo_cuenta_obj = tipo_cuenta.objects.get(descripcion=cuenta_data['tipo_cuenta'])
                    situacion_iva_obj = situacionIva.objects.get(reducida=cuenta_data['situacion_iva'])
                    
                    # Crear cuenta
                    nueva_cuenta, created = cuenta.objects.get_or_create(
                        numero_documento=cuenta_data['cuit'],
                        defaults={
                            'razon_social': cuenta_data['razon_social'],
                            'nombre_fantasia': cuenta_data['nombre_fantasia'],
                            'tipo_documento_idtipo_documento': tipo_cuit,
                            'direccion_cuenta': f'Calle Ejemplo {100 + i}',
                            'pais_id': argentina,
                            'provincia_idprovincia': cordoba_prov,
                            'localidad_idlocalidad': cordoba_city,
                            'telefono_cuenta': cuenta_data['telefono'],
                            'email_cuenta': cuenta_data['email'],
                            'tipo_cuenta_id_tipo_cuenta': tipo_cuenta_obj,
                            'situacionIva_idsituacionIva': situacion_iva_obj,
                            'activo': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f'  Cuenta creada: {nueva_cuenta.razon_social}')
                        
                        # Crear un contacto
                        contacto_cuenta.objects.create(
                            cuenta_id=nueva_cuenta,
                            nombre=f'Contacto {nueva_cuenta.nombre_fantasia}',
                            cargo='Responsable',
                            email=cuenta_data['email'],
                            telefono=cuenta_data['telefono'],
                            activo=True
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'No se pudo crear cuenta {cuenta_data["razon_social"]}: {e}')
                    )
            
            self.stdout.write(f'Total de cuentas nuevas creadas: {created_count}')
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al obtener datos maestros: {e}')
            )