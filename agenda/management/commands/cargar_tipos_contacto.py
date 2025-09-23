"""
Comando para cargar tipos de contacto iniciales.
"""
from django.core.management.base import BaseCommand
from agenda.models import TipoContacto


class Command(BaseCommand):
    help = 'Carga tipos de contacto iniciales en la base de datos'

    def handle(self, *args, **options):
        tipos_contacto = [
            {
                'nombre': 'Cliente',
                'descripcion': 'Contactos que son clientes de la empresa',
                'color': '#28a745'  # Verde
            },
            {
                'nombre': 'Proveedor',
                'descripcion': 'Contactos que son proveedores de la empresa',
                'color': '#17a2b8'  # Azul claro
            },
            {
                'nombre': 'Empleado',
                'descripcion': 'Contactos que son empleados de la empresa',
                'color': '#ffc107'  # Amarillo
            },
            {
                'nombre': 'Profesional',
                'descripcion': 'Contactos profesionales (abogados, contadores, etc.)',
                'color': '#6f42c1'  # Púrpura
            },
            {
                'nombre': 'Personal',
                'descripcion': 'Contactos personales y familiares',
                'color': '#fd7e14'  # Naranja
            },
            {
                'nombre': 'Gobierno',
                'descripcion': 'Contactos de organismos gubernamentales',
                'color': '#dc3545'  # Rojo
            },
            {
                'nombre': 'Transporte',
                'descripcion': 'Contactos relacionados con logística y transporte',
                'color': '#20c997'  # Verde azulado
            },
            {
                'nombre': 'Banco/Financiero',
                'descripcion': 'Contactos de entidades bancarias y financieras',
                'color': '#6c757d'  # Gris
            },
            {
                'nombre': 'Socio',
                'descripcion': 'Socios comerciales y de negocios',
                'color': '#007bff'  # Azul
            },
            {
                'nombre': 'Referencia',
                'descripcion': 'Contactos que pueden brindar referencias',
                'color': '#e83e8c'  # Rosa
            }
        ]

        created_count = 0
        updated_count = 0

        for tipo_data in tipos_contacto:
            tipo_contacto, created = TipoContacto.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={
                    'descripcion': tipo_data['descripcion'],
                    'color': tipo_data['color'],
                    'activo': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado tipo de contacto: {tipo_contacto.nombre}')
                )
            else:
                # Actualizar descripción y color si ya existe
                if tipo_contacto.descripcion != tipo_data['descripcion'] or tipo_contacto.color != tipo_data['color']:
                    tipo_contacto.descripcion = tipo_data['descripcion']
                    tipo_contacto.color = tipo_data['color']
                    tipo_contacto.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Actualizado tipo de contacto: {tipo_contacto.nombre}')
                    )
                else:
                    self.stdout.write(
                        self.style.HTTP_INFO(f'◦ Ya existe tipo de contacto: {tipo_contacto.nombre}')
                    )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Proceso completado: {created_count} creados, {updated_count} actualizados'
            )
        )

        # Mostrar todos los tipos de contacto disponibles
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('📋 Tipos de contacto disponibles:'))
        for tipo in TipoContacto.objects.filter(activo=True).order_by('nombre'):
            self.stdout.write(f'   • {tipo.nombre} ({tipo.color}) - {tipo.descripcion}')