from django.core.management.base import BaseCommand
from mercaderias.models import Calidad


class Command(BaseCommand):
    help = 'Crear calidades de ejemplo para el sistema de clasificación'

    def handle(self, *args, **options):
        # Crear calidades típicas para granos
        calidades = [
            {
                'nombre': 'Primera', 
                'codigo': 'P1', 
                'descripcion': 'Calidad premium, sin daños', 
                'orden_presentacion': 1, 
                'color_hex': '#28a745'
            },
            {
                'nombre': 'Segunda', 
                'codigo': 'P2', 
                'descripcion': 'Buena calidad, mínimos defectos', 
                'orden_presentacion': 2, 
                'color_hex': '#17a2b8'
            },
            {
                'nombre': 'Tercera', 
                'codigo': 'P3', 
                'descripcion': 'Calidad comercial estándar', 
                'orden_presentacion': 3, 
                'color_hex': '#ffc107'
            },
            {
                'nombre': 'Rechazo', 
                'codigo': 'REC', 
                'descripcion': 'No apto para comercialización', 
                'orden_presentacion': 4, 
                'color_hex': '#dc3545'
            },
            {
                'nombre': 'Húmedo', 
                'codigo': 'HUM', 
                'descripcion': 'Exceso de humedad, requiere secado', 
                'orden_presentacion': 5, 
                'color_hex': '#6c757d'
            },
            {
                'nombre': 'Partido', 
                'codigo': 'PAR', 
                'descripcion': 'Granos partidos o dañados', 
                'orden_presentacion': 6, 
                'color_hex': '#fd7e14'
            },
        ]

        self.stdout.write("Creando calidades de ejemplo...")
        
        for calidad_data in calidades:
            calidad, created = Calidad.objects.get_or_create(
                codigo=calidad_data['codigo'],
                defaults=calidad_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada calidad: {calidad.nombre} ({calidad.codigo})')
                )
            else:
                self.stdout.write(f'- Ya existe calidad: {calidad.nombre} ({calidad.codigo})')

        total = Calidad.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de calidades: {total}')
        )
        self.stdout.write("¡Listo! Ahora puedes usar el sistema de clasificación de calidades.")