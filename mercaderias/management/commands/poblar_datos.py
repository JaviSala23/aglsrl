# Import necesario para agregaciones
from django.db import models
from django.core.management.base import BaseCommand
from django.db import transaction
from mercaderias.models import Grano, Mercaderia
from almacenamiento.models import Ubicacion, Almacenaje, Stock
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de ejemplo para mercaderías y almacenamiento'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando población de datos...'))
        
        with transaction.atomic():
            self.create_granos()
            self.create_ubicaciones()
            self.create_almacenajes()
            self.create_mercaderias()
            self.create_stocks()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Datos de ejemplo creados exitosamente!')
        )

    def create_granos(self):
        """Crear granos de ejemplo"""
        granos_data = [
            {'nombre': 'Soja', 'codigo': 'SOJ'},
            {'nombre': 'Maíz', 'codigo': 'MAI'},
            {'nombre': 'Trigo', 'codigo': 'TRI'},
            {'nombre': 'Girasol', 'codigo': 'GIR'},
            {'nombre': 'Cebada', 'codigo': 'CEB'},
            {'nombre': 'Avena', 'codigo': 'AVE'},
        ]
        
        for data in granos_data:
            grano, created = Grano.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'codigo': data['codigo'], 'activo': True}
            )
            if created:
                self.stdout.write(f'  ✓ Grano creado: {grano.nombre}')

    def create_ubicaciones(self):
        """Crear ubicaciones de ejemplo"""
        ubicaciones_data = [
            {
                'nombre': 'Planta Central',
                'tipo': 'PLANTA',
                'encargado_nombre': 'Juan Pérez',
                'direccion': 'Ruta Nacional 7 Km 145, Buenos Aires'
            },
            {
                'nombre': 'Depósito Norte',
                'tipo': 'ZONA_MIXTA',
                'direccion': 'Zona Industrial Norte, Córdoba'
            },
            {
                'nombre': 'Planta Sur',
                'tipo': 'PLANTA',
                'encargado_nombre': 'María González',
                'direccion': 'Zona Rural Sur, Santa Fe'
            },
            {
                'nombre': 'Almacén Oeste',
                'tipo': 'ZONA_MIXTA',
                'direccion': 'Ruta Provincial 23, La Pampa'
            },
        ]
        
        for data in ubicaciones_data:
            ubicacion, created = Ubicacion.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✓ Ubicación creada: {ubicacion.nombre}')

    def create_almacenajes(self):
        """Crear almacenajes de ejemplo"""
        ubicaciones = list(Ubicacion.objects.all())
        tipos_almacenaje = ['SILO', 'SILO_BOLSA', 'GALPON']
        
        almacenajes_data = []
        
        # Para cada ubicación, crear varios almacenajes
        for ubicacion in ubicaciones:
            num_almacenajes = random.randint(3, 8)
            
            for i in range(1, num_almacenajes + 1):
                tipo = random.choice(tipos_almacenaje)
                codigo = f"{ubicacion.nombre[:3].upper()}-{tipo[:3]}-{i:02d}"
                
                # Capacidades según tipo
                capacidad_ranges = {
                    'SILO': (50000, 200000),
                    'SILO_BOLSA': (20000, 80000),
                    'GALPON': (30000, 150000),
                }
                
                capacidad = random.randint(*capacidad_ranges[tipo])
                
                almacenaje_data = {
                    'ubicacion': ubicacion,
                    'tipo': tipo,
                    'codigo': codigo,
                    'capacidad_kg': Decimal(str(capacidad)),
                    'estado': 'DISPONIBLE',
                    'activo': True
                }
                
                # Campos específicos para silo bolsa
                if tipo == 'SILO_BOLSA':
                    almacenaje_data['longitud_metros'] = Decimal(str(random.randint(50, 200)))
                    almacenaje_data['sentido'] = random.choice(['Norte-Sur', 'Este-Oeste', 'NE-SO', 'NO-SE'])
                
                almacenajes_data.append(almacenaje_data)
        
        for data in almacenajes_data:
            almacenaje, created = Almacenaje.objects.get_or_create(
                ubicacion=data['ubicacion'],
                codigo=data['codigo'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✓ Almacenaje creado: {almacenaje}')

    def create_mercaderias(self):
        """Crear mercaderías de ejemplo"""
        granos = list(Grano.objects.all())
        tipos = ['PROPIO', 'TERCERO']
        estados = ['ACTIVO', 'ACTIVO', 'ACTIVO', 'VENDIDO']  # Más probabilidad de ACTIVO
        
        propietarios = [
            'Estancia La Esperanza',
            'Agropecuaria San Martín',
            'Cooperativa Agrícola Unidos',
            'Campos del Sur S.A.',
            'Establecimiento El Progreso',
            'Granja Santa María',
            None,  # Para mercaderías propias
        ]
        
        # Crear entre 20 y 40 mercaderías
        num_mercaderias = random.randint(20, 40)
        
        for i in range(num_mercaderias):
            grano = random.choice(granos)
            tipo = random.choice(tipos)
            estado = random.choice(estados)
            
            # Datos del propietario solo para TERCERO
            propietario_nombre = None
            propietario_contacto = None
            
            if tipo == 'TERCERO':
                propietario_nombre = random.choice(propietarios)
                if propietario_nombre:
                    propietario_contacto = f"contacto@{propietario_nombre.lower().replace(' ', '').replace('.', '')}.com"
            
            # Fechas
            fecha_ingreso = date.today() - timedelta(days=random.randint(1, 365))
            fecha_analisis = fecha_ingreso + timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None
            fecha_vencimiento = fecha_ingreso + timedelta(days=random.randint(30, 180)) if random.choice([True, False]) else None
            
            # Características del grano (valores aleatorios realistas)
            mercaderia_data = {
                'grano': grano,
                'tipo': tipo,
                'estado': estado,
                'propietario_nombre': propietario_nombre,
                'propietario_contacto': propietario_contacto,
                'fecha_ingreso': fecha_ingreso,
                'fecha_analisis': fecha_analisis,
                'fecha_vencimiento': fecha_vencimiento,
            }
            
            # Agregar características técnicas según el grano
            if grano.nombre in ['Soja', 'Maíz']:
                mercaderia_data.update({
                    'humedad_porcentaje': Decimal(str(round(random.uniform(12.5, 16.0), 2))),
                    'proteina_porcentaje': Decimal(str(round(random.uniform(18.0, 24.0), 2))),
                    'cuerpos_extranos_porcentaje': Decimal(str(round(random.uniform(0.5, 2.0), 2))),
                    'granos_danados_porcentaje': Decimal(str(round(random.uniform(1.0, 4.0), 2))),
                    'peso_hectolitro': Decimal(str(round(random.uniform(72.0, 78.0), 2))),
                })
            elif grano.nombre == 'Trigo':
                mercaderia_data.update({
                    'humedad_porcentaje': Decimal(str(round(random.uniform(11.0, 14.5), 2))),
                    'proteina_porcentaje': Decimal(str(round(random.uniform(10.0, 16.0), 2))),
                    'peso_hectolitro': Decimal(str(round(random.uniform(75.0, 82.0), 2))),
                })
            
            mercaderia = Mercaderia.objects.create(**mercaderia_data)
            self.stdout.write(f'  ✓ Mercadería creada: {mercaderia}')

    def create_stocks(self):
        """Crear stocks de ejemplo"""
        mercaderias_activas = list(Mercaderia.objects.filter(estado='ACTIVO'))
        almacenajes = list(Almacenaje.objects.all())
        
        # Para cada mercadería activa, crear stock en 1-3 almacenajes
        for mercaderia in mercaderias_activas:
            num_ubicaciones = random.randint(1, min(3, len(almacenajes)))
            almacenajes_seleccionados = random.sample(almacenajes, num_ubicaciones)
            
            for almacenaje in almacenajes_seleccionados:
                # Cantidad entre 5,000 y 50,000 kg
                cantidad = random.randint(5000, 50000)
                
                # Verificar que no exceda la capacidad del almacenaje (si está definida)
                if almacenaje.capacidad_kg:
                    stock_actual = Stock.objects.filter(almacenaje=almacenaje).aggregate(
                        total=models.Sum('cantidad_kg')
                    )['total'] or Decimal('0')
                    
                    cantidad_disponible = float(almacenaje.capacidad_kg - stock_actual)
                    if cantidad_disponible > 0:
                        cantidad = min(cantidad, int(cantidad_disponible * 0.8))  # Usar máximo 80% del espacio disponible
                    else:
                        continue  # Saltar si no hay espacio
                
                if cantidad > 0:
                    stock, created = Stock.objects.get_or_create(
                        ubicacion=almacenaje.ubicacion,
                        almacenaje=almacenaje,
                        mercaderia=mercaderia,
                        defaults={'cantidad_kg': Decimal(str(cantidad))}
                    )
                    
                    if created:
                        self.stdout.write(f'  ✓ Stock creado: {stock}')
        
        # Actualizar estados de almacenajes según ocupación
        for almacenaje in almacenajes:
            stock_total = Stock.objects.filter(almacenaje=almacenaje).aggregate(
                total=models.Sum('cantidad_kg')
            )['total'] or Decimal('0')
            
            if stock_total > 0:
                almacenaje.estado = 'OCUPADO'
                almacenaje.save()
                self.stdout.write(f'  ✓ Almacenaje {almacenaje.codigo} marcado como OCUPADO')