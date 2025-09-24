#!/usr/bin/env python3
"""
Script para cargar datos iniciales de mercaderías y ubicaciones
Basado en las especificaciones del sistema AGL
"""

import os
import sys
import django
from decimal import Decimal

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
    django.setup()

def cargar_tipos_grano():
    """Cargar tipos de grano básicos"""
    from mercaderias.models import TipoGrano
    
    granos = [
        {'nombre': 'Soja', 'codigo': 'SOJ'},
        {'nombre': 'Maíz', 'codigo': 'MAI'},
        {'nombre': 'Girasol', 'codigo': 'GIR'},
        {'nombre': 'Trigo', 'codigo': 'TRI'},
        {'nombre': 'Sorgo', 'codigo': 'SOR'},
        {'nombre': 'Avena', 'codigo': 'AVE'},
        {'nombre': 'Cebada', 'codigo': 'CEB'},
    ]
    
    for grano_data in granos:
        grano, created = TipoGrano.objects.get_or_create(
            codigo=grano_data['codigo'],
            defaults={'nombre': grano_data['nombre']}
        )
        if created:
            print(f"✓ Creado tipo de grano: {grano}")
        else:
            print(f"- Ya existe tipo de grano: {grano}")

def cargar_calidades_grado():
    """Cargar calidades y grados"""
    from mercaderias.models import CalidadGrado
    
    calidades = [
        {'descripcion': 'Premium', 'codigo': 'PREM'},
        {'descripcion': 'Estándar', 'codigo': 'EST'},
        {'descripcion': 'FAS', 'codigo': 'FAS'},
        {'descripcion': 'FAQ', 'codigo': 'FAQ'},
        {'descripcion': 'Húmedo', 'codigo': 'HUM'},
        {'descripcion': 'Averiado', 'codigo': 'AVE'},
        {'descripcion': 'Condicional', 'codigo': 'COND'},
    ]
    
    for calidad_data in calidades:
        calidad, created = CalidadGrado.objects.get_or_create(
            codigo=calidad_data['codigo'],
            defaults={'descripcion': calidad_data['descripcion']}
        )
        if created:
            print(f"✓ Creada calidad/grado: {calidad}")
        else:
            print(f"- Ya existe calidad/grado: {calidad}")

def cargar_pesos_unitarios():
    """Cargar pesos unitarios de referencia"""
    from mercaderias.models import PesoUnitarioReferencia, TipoPresentacion
    
    pesos = [
        {'presentacion': TipoPresentacion.BOLSA_25, 'peso_kg': Decimal('25.00')},
        {'presentacion': TipoPresentacion.BOLSA_50, 'peso_kg': Decimal('50.00')},
        {'presentacion': TipoPresentacion.BIGBAG_500, 'peso_kg': Decimal('500.00')},
        {'presentacion': TipoPresentacion.BIGBAG_1000, 'peso_kg': Decimal('1000.00')},
    ]
    
    for peso_data in pesos:
        peso, created = PesoUnitarioReferencia.objects.get_or_create(
            presentacion=peso_data['presentacion'],
            defaults={'peso_kg': peso_data['peso_kg']}
        )
        if created:
            print(f"✓ Creado peso unitario: {peso}")
        else:
            print(f"- Ya existe peso unitario: {peso}")

def cargar_factores_conversion():
    """Cargar factores de conversión"""
    from mercaderias.models import FactorConversion, UnidadMedida
    
    factores = [
        {'origen': UnidadMedida.TN, 'destino': UnidadMedida.KG, 'factor': Decimal('1000.0000')},
        {'origen': UnidadMedida.KG, 'destino': UnidadMedida.TN, 'factor': Decimal('0.0010')},
    ]
    
    for factor_data in factores:
        factor, created = FactorConversion.objects.get_or_create(
            unidad_origen=factor_data['origen'],
            unidad_destino=factor_data['destino'],
            defaults={'factor': factor_data['factor']}
        )
        if created:
            print(f"✓ Creado factor de conversión: {factor}")
        else:
            print(f"- Ya existe factor de conversión: {factor}")

def cargar_reglas_compatibilidad():
    """Cargar reglas de compatibilidad almacenaje-presentación"""
    from mercaderias.models import ReglaAlmacenajePresentacion, TipoAlmacenaje, TipoPresentacion
    
    # Matriz de compatibilidad según el documento de diseño
    reglas = [
        # SILO - solo GRANEL
        {'almacenaje': TipoAlmacenaje.SILO, 'presentacion': TipoPresentacion.GRANEL, 'compatible': True},
        {'almacenaje': TipoAlmacenaje.SILO, 'presentacion': TipoPresentacion.BOLSA_25, 'compatible': False},
        {'almacenaje': TipoAlmacenaje.SILO, 'presentacion': TipoPresentacion.BOLSA_50, 'compatible': False},
        {'almacenaje': TipoAlmacenaje.SILO, 'presentacion': TipoPresentacion.BIGBAG_500, 'compatible': False},
        {'almacenaje': TipoAlmacenaje.SILO, 'presentacion': TipoPresentacion.BIGBAG_1000, 'compatible': False},
        
        # SILO_BOLSA - solo GRANEL
        {'almacenaje': TipoAlmacenaje.SILO_BOLSA, 'presentacion': TipoPresentacion.GRANEL, 'compatible': True},
        {'almacenaje': TipoAlmacenaje.SILO_BOLSA, 'presentacion': TipoPresentacion.BOLSA_25, 'compatible': False},
        {'almacenaje': TipoAlmacenaje.SILO_BOLSA, 'presentacion': TipoPresentacion.BOLSA_50, 'compatible': False},
        {'almacenaje': TipoAlmacenaje.SILO_BOLSA, 'presentacion': TipoPresentacion.BIGBAG_500, 'compatible': False},
        {'almacenaje': TipoAlmacenaje.SILO_BOLSA, 'presentacion': TipoPresentacion.BIGBAG_1000, 'compatible': False},
        
        # GALPON - todas las presentaciones
        {'almacenaje': TipoAlmacenaje.GALPON, 'presentacion': TipoPresentacion.GRANEL, 'compatible': True},
        {'almacenaje': TipoAlmacenaje.GALPON, 'presentacion': TipoPresentacion.BOLSA_25, 'compatible': True},
        {'almacenaje': TipoAlmacenaje.GALPON, 'presentacion': TipoPresentacion.BOLSA_50, 'compatible': True},
        {'almacenaje': TipoAlmacenaje.GALPON, 'presentacion': TipoPresentacion.BIGBAG_500, 'compatible': True},
        {'almacenaje': TipoAlmacenaje.GALPON, 'presentacion': TipoPresentacion.BIGBAG_1000, 'compatible': True},
    ]
    
    for regla_data in reglas:
        regla, created = ReglaAlmacenajePresentacion.objects.get_or_create(
            tipo_almacenaje=regla_data['almacenaje'],
            tipo_presentacion=regla_data['presentacion'],
            defaults={'es_compatible': regla_data['compatible']}
        )
        if created:
            estado = "Compatible" if regla_data['compatible'] else "No Compatible"
            print(f"✓ Creada regla: {regla_data['almacenaje']} - {regla_data['presentacion']}: {estado}")

def cargar_ubicaciones():
    """Cargar ubicaciones según especificaciones"""
    from mercaderias.models import Ubicacion, TipoUbicacion
    
    ubicaciones = [
        # Plantas (cada una con su encargado)
        {
            'nombre': 'Planta Norte',
            'tipo': TipoUbicacion.PLANTA,
            'encargado_nombre': 'Juan Pérez',
            'direccion': 'Ruta Nacional 9 Km 25, Zona Norte'
        },
        {
            'nombre': 'Planta Sur',
            'tipo': TipoUbicacion.PLANTA,
            'encargado_nombre': 'María González',
            'direccion': 'Camino Rural 15, Zona Sur'
        },
        {
            'nombre': 'Planta Este',
            'tipo': TipoUbicacion.PLANTA,
            'encargado_nombre': 'Carlos Rodríguez',
            'direccion': 'Ruta Provincial 12 Km 8, Zona Este'
        },
        
        # Galpones alquilados en otra localización
        {
            'nombre': 'Galpón Alquilado 1',
            'tipo': TipoUbicacion.ZONA_MIXTA,
            'direccion': 'Parque Industrial, Lote 25'
        },
        {
            'nombre': 'Galpón Alquilado 2',
            'tipo': TipoUbicacion.ZONA_MIXTA,
            'direccion': 'Parque Industrial, Lote 26'
        },
        
        # Silos en el campo (gestión mixta)
        {
            'nombre': 'Campo Los Álamos',
            'tipo': TipoUbicacion.ZONA_MIXTA,
            'direccion': 'Campo Los Álamos, Ruta 33 Km 180'
        },
        {
            'nombre': 'Campo San Martín',
            'tipo': TipoUbicacion.ZONA_MIXTA,
            'direccion': 'Campo San Martín, Camino Vecinal s/n'
        },
    ]
    
    for ubicacion_data in ubicaciones:
        ubicacion, created = Ubicacion.objects.get_or_create(
            nombre=ubicacion_data['nombre'],
            defaults=ubicacion_data
        )
        if created:
            print(f"✓ Creada ubicación: {ubicacion}")
        else:
            print(f"- Ya existe ubicación: {ubicacion}")

def cargar_almacenajes():
    """Cargar almacenajes para cada ubicación"""
    from mercaderias.models import Ubicacion, Almacenaje, TipoAlmacenaje
    
    # Obtener ubicaciones
    plantas = Ubicacion.objects.filter(tipo='PLANTA')
    galpones_alquilados = Ubicacion.objects.filter(nombre__icontains='Galpón Alquilado')
    campos = Ubicacion.objects.filter(nombre__icontains='Campo')
    
    # Para cada planta: galpon, silo, silos bolsa
    for planta in plantas:
        almacenajes_planta = [
            {
                'ubicacion': planta,
                'tipo': TipoAlmacenaje.GALPON,
                'codigo': f'GAL-{planta.nombre.split()[-1][:3].upper()}',
                'capacidad_kg': Decimal('500000.00')  # 500 toneladas
            },
            {
                'ubicacion': planta,
                'tipo': TipoAlmacenaje.SILO,
                'codigo': f'SIL-{planta.nombre.split()[-1][:3].upper()}-01',
                'capacidad_kg': Decimal('1000000.00')  # 1000 toneladas
            },
            {
                'ubicacion': planta,
                'tipo': TipoAlmacenaje.SILO_BOLSA,
                'codigo': f'SB-{planta.nombre.split()[-1][:3].upper()}-01',
                'longitud_metros': Decimal('60.00'),
                'sentido': 'Norte-Sur'
            },
            {
                'ubicacion': planta,
                'tipo': TipoAlmacenaje.SILO_BOLSA,
                'codigo': f'SB-{planta.nombre.split()[-1][:3].upper()}-02',
                'longitud_metros': Decimal('60.00'),
                'sentido': 'Este-Oeste'
            },
        ]
        
        for almacenaje_data in almacenajes_planta:
            almacenaje, created = Almacenaje.objects.get_or_create(
                ubicacion=almacenaje_data['ubicacion'],
                codigo=almacenaje_data['codigo'],
                defaults=almacenaje_data
            )
            if created:
                print(f"✓ Creado almacenaje: {almacenaje}")
    
    # Para galpones alquilados
    for i, galpon in enumerate(galpones_alquilados, 1):
        almacenaje_data = {
            'ubicacion': galpon,
            'tipo': TipoAlmacenaje.GALPON,
            'codigo': f'GAL-ALQ-{i:02d}',
            'capacidad_kg': Decimal('300000.00')  # 300 toneladas
        }
        
        almacenaje, created = Almacenaje.objects.get_or_create(
            ubicacion=almacenaje_data['ubicacion'],
            codigo=almacenaje_data['codigo'],
            defaults=almacenaje_data
        )
        if created:
            print(f"✓ Creado almacenaje: {almacenaje}")
    
    # Para campos (silos)
    for i, campo in enumerate(campos, 1):
        for j in range(1, 4):  # 3 silos por campo
            almacenaje_data = {
                'ubicacion': campo,
                'tipo': TipoAlmacenaje.SILO,
                'codigo': f'SIL-CAM-{i:02d}-{j:02d}',
                'capacidad_kg': Decimal('800000.00')  # 800 toneladas
            }
            
            almacenaje, created = Almacenaje.objects.get_or_create(
                ubicacion=almacenaje_data['ubicacion'],
                codigo=almacenaje_data['codigo'],
                defaults=almacenaje_data
            )
            if created:
                print(f"✓ Creado almacenaje: {almacenaje}")

def main():
    """Función principal"""
    setup_django()
    
    print("=== CARGANDO DATOS INICIALES DE MERCADERÍAS ===\n")
    
    print("1. Cargando tipos de grano...")
    cargar_tipos_grano()
    print()
    
    print("2. Cargando calidades y grados...")
    cargar_calidades_grado()
    print()
    
    print("3. Cargando pesos unitarios de referencia...")
    cargar_pesos_unitarios()
    print()
    
    print("4. Cargando factores de conversión...")
    cargar_factores_conversion()
    print()
    
    print("5. Cargando reglas de compatibilidad...")
    cargar_reglas_compatibilidad()
    print()
    
    print("6. Cargando ubicaciones...")
    cargar_ubicaciones()
    print()
    
    print("7. Cargando almacenajes...")
    cargar_almacenajes()
    print()
    
    print("=== CARGA COMPLETADA ===")

if __name__ == '__main__':
    main()