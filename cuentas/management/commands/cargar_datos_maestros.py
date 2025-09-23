"""
Comando para cargar datos maestros iniciales del módulo de cuentas.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from cuentas.models import (
    pais, provincia, localidad, tipo_documento, situacionIva, tipo_cuenta
)


class Command(BaseCommand):
    help = 'Carga datos maestros iniciales para el módulo de cuentas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recarga de datos existentes',
        )
    
    def handle(self, *args, **options):
        """Ejecutar carga de datos maestros."""
        self.stdout.write(
            self.style.SUCCESS('Iniciando carga de datos maestros...')
        )
        
        try:
            with transaction.atomic():
                self._cargar_paises()
                self._cargar_tipos_documento()
                self._cargar_situaciones_iva()
                self._cargar_tipos_cuenta()
                self._cargar_provincias_argentina()
                self._cargar_algunas_localidades()
            
            self.stdout.write(
                self.style.SUCCESS('¡Datos maestros cargados exitosamente!')
            )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al cargar datos maestros: {e}')
            )
            raise
    
    def _cargar_paises(self):
        """Cargar países iniciales."""
        paises_data = [
            {'nombre': 'Argentina'},
            {'nombre': 'Brasil'},
            {'nombre': 'Chile'},
            {'nombre': 'Uruguay'},
            {'nombre': 'Paraguay'},
            {'nombre': 'Bolivia'},
        ]
        
        for pais_data in paises_data:
            pais_obj, created = pais.objects.get_or_create(
                nombre=pais_data['nombre']
            )
            if created:
                self.stdout.write(f'  País creado: {pais_obj.nombre}')
    
    def _cargar_tipos_documento(self):
        """Cargar tipos de documento AFIP."""
        tipos_data = [
            {'descripcion': 'CUIT', 'cod_afip': 30},
            {'descripcion': 'CUIL', 'cod_afip': 27},
            {'descripcion': 'DNI', 'cod_afip': 96},
            {'descripcion': 'Pasaporte', 'cod_afip': 94},
            {'descripcion': 'CI Policía Federal', 'cod_afip': 92},
            {'descripcion': 'CI Buenos Aires', 'cod_afip': 93},
            {'descripcion': 'CI Catamarca', 'cod_afip': 91},
            {'descripcion': 'CI Córdoba', 'cod_afip': 90},
        ]
        
        for tipo_data in tipos_data:
            tipo_obj, created = tipo_documento.objects.get_or_create(
                cod_afip=tipo_data['cod_afip'],
                defaults={'descripcion': tipo_data['descripcion']}
            )
            if created:
                self.stdout.write(f'  Tipo documento creado: {tipo_obj.descripcion}')
    
    def _cargar_situaciones_iva(self):
        """Cargar situaciones de IVA AFIP."""
        situaciones_data = [
            {'descripcion': 'Responsable Inscripto', 'reducida': 'RI', 'codigo_afip': 1},
            {'descripcion': 'Responsable no Inscripto', 'reducida': 'RNI', 'codigo_afip': 2},
            {'descripcion': 'No Responsable', 'reducida': 'NR', 'codigo_afip': 3},
            {'descripcion': 'Sujeto Exento', 'reducida': 'EX', 'codigo_afip': 4},
            {'descripcion': 'Consumidor Final', 'reducida': 'CF', 'codigo_afip': 5},
            {'descripcion': 'Responsable Monotributo', 'reducida': 'MONO', 'codigo_afip': 6},
            {'descripcion': 'Sujeto no Categorizado', 'reducida': 'SNC', 'codigo_afip': 7},
            {'descripcion': 'Proveedor del Exterior', 'reducida': 'EXT', 'codigo_afip': 8},
            {'descripcion': 'Cliente del Exterior', 'reducida': 'CEXT', 'codigo_afip': 9},
            {'descripcion': 'IVA Liberado – Ley Nº 19.640', 'reducida': 'LIB', 'codigo_afip': 10},
        ]
        
        for situacion_data in situaciones_data:
            situacion_obj, created = situacionIva.objects.get_or_create(
                codigo_afip=situacion_data['codigo_afip'],
                defaults={
                    'descripcion': situacion_data['descripcion'],
                    'reducida': situacion_data['reducida']
                }
            )
            if created:
                self.stdout.write(f'  Situación IVA creada: {situacion_obj.descripcion}')
    
    def _cargar_tipos_cuenta(self):
        """Cargar tipos de cuenta del negocio."""
        tipos_data = [
            {'descripcion': 'Cliente'},
            {'descripcion': 'Proveedor'},
            {'descripcion': 'Transportista'},
            {'descripcion': 'Propia'},
            {'descripcion': 'Cliente y Proveedor'},
            {'descripcion': 'Empleado'},
            {'descripcion': 'Organismo Público'},
        ]
        
        for tipo_data in tipos_data:
            tipo_obj, created = tipo_cuenta.objects.get_or_create(
                descripcion=tipo_data['descripcion']
            )
            if created:
                self.stdout.write(f'  Tipo cuenta creado: {tipo_obj.descripcion}')
    
    def _cargar_provincias_argentina(self):
        """Cargar provincias de Argentina."""
        argentina = pais.objects.get(nombre='Argentina')
        
        provincias_data = [
            {'nombre': 'Buenos Aires', 'codigo': 'BA'},
            {'nombre': 'Ciudad Autónoma de Buenos Aires', 'codigo': 'CABA'},
            {'nombre': 'Catamarca', 'codigo': 'CT'},
            {'nombre': 'Chaco', 'codigo': 'CC'},
            {'nombre': 'Chubut', 'codigo': 'CH'},
            {'nombre': 'Córdoba', 'codigo': 'CB'},
            {'nombre': 'Corrientes', 'codigo': 'CN'},
            {'nombre': 'Entre Ríos', 'codigo': 'ER'},
            {'nombre': 'Formosa', 'codigo': 'FM'},
            {'nombre': 'Jujuy', 'codigo': 'JY'},
            {'nombre': 'La Pampa', 'codigo': 'LP'},
            {'nombre': 'La Rioja', 'codigo': 'LR'},
            {'nombre': 'Mendoza', 'codigo': 'MZ'},
            {'nombre': 'Misiones', 'codigo': 'MN'},
            {'nombre': 'Neuquén', 'codigo': 'NQ'},
            {'nombre': 'Río Negro', 'codigo': 'RN'},
            {'nombre': 'Salta', 'codigo': 'SA'},
            {'nombre': 'San Juan', 'codigo': 'SJ'},
            {'nombre': 'San Luis', 'codigo': 'SL'},
            {'nombre': 'Santa Cruz', 'codigo': 'SC'},
            {'nombre': 'Santa Fe', 'codigo': 'SF'},
            {'nombre': 'Santiago del Estero', 'codigo': 'SE'},
            {'nombre': 'Tierra del Fuego', 'codigo': 'TF'},
            {'nombre': 'Tucumán', 'codigo': 'TM'},
        ]
        
        for provincia_data in provincias_data:
            provincia_obj, created = provincia.objects.get_or_create(
                nombre_provincia=provincia_data['nombre'],
                pais_idpais=argentina,
                defaults={'codigo_provincia': provincia_data['codigo']}
            )
            if created:
                self.stdout.write(f'  Provincia creada: {provincia_obj.nombre_provincia}')
    
    def _cargar_algunas_localidades(self):
        """Cargar algunas localidades importantes."""
        try:
            caba = provincia.objects.get(nombre_provincia='Ciudad Autónoma de Buenos Aires')
            buenos_aires = provincia.objects.get(nombre_provincia='Buenos Aires')
            cordoba = provincia.objects.get(nombre_provincia='Córdoba')
            santa_fe = provincia.objects.get(nombre_provincia='Santa Fe')
            
            localidades_data = [
                # CABA
                {'nombre': 'Ciudad Autónoma de Buenos Aires', 'cp': 'C1000', 'provincia': caba},
                
                # Buenos Aires
                {'nombre': 'La Plata', 'cp': 'B1900', 'provincia': buenos_aires},
                {'nombre': 'Mar del Plata', 'cp': 'B7600', 'provincia': buenos_aires},
                {'nombre': 'Bahía Blanca', 'cp': 'B8000', 'provincia': buenos_aires},
                {'nombre': 'Tandil', 'cp': 'B7000', 'provincia': buenos_aires},
                {'nombre': 'San Nicolás', 'cp': 'B2900', 'provincia': buenos_aires},
                
                # Córdoba
                {'nombre': 'Córdoba', 'cp': 'X5000', 'provincia': cordoba},
                {'nombre': 'Villa Carlos Paz', 'cp': 'X5152', 'provincia': cordoba},
                {'nombre': 'Río Cuarto', 'cp': 'X5800', 'provincia': cordoba},
                
                # Santa Fe
                {'nombre': 'Santa Fe', 'cp': 'S3000', 'provincia': santa_fe},
                {'nombre': 'Rosario', 'cp': 'S2000', 'provincia': santa_fe},
                {'nombre': 'Rafaela', 'cp': 'S2300', 'provincia': santa_fe},
            ]
            
            for localidad_data in localidades_data:
                localidad_obj, created = localidad.objects.get_or_create(
                    nombre_localidad=localidad_data['nombre'],
                    provincia_id_provincia=localidad_data['provincia'],
                    defaults={'cp_localidad': localidad_data['cp']}
                )
                if created:
                    self.stdout.write(f'  Localidad creada: {localidad_obj.nombre_localidad}')
        
        except provincia.DoesNotExist as e:
            self.stdout.write(
                self.style.WARNING(f'Provincia no encontrada para cargar localidades: {e}')
            )