#!/usr/bin/env python3
"""
Script para crear datos de ejemplo para el módulo de transportes.
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from django.contrib.auth.models import User
from transportes.models import TipoCamion, Camion, Chofer, Viaje, TicketBalanza
from cuentas.models import cuenta

def crear_datos_ejemplo():
    """Crear datos de ejemplo para transportes."""
    
    # Obtener o crear un usuario admin
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'email': 'admin@aglsrl.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Obtener tipos de camión
    tipo_mediano = TipoCamion.objects.get(nombre='Camión Mediano')
    tipo_grande = TipoCamion.objects.get(nombre='Camión Grande')
    
    # Crear camiones de ejemplo
    camiones_data = [
        {
            'patente': 'ABC123',
            'marca': 'Mercedes-Benz',
            'modelo': 'Atego 1725',
            'año': 2020,
            'tipo_camion': tipo_mediano,
            'capacidad_carga': 7.5,
            'numero_motor': 'MB123456789',
            'numero_chasis': 'WDB9701651L123456',
            'estado': 'disponible',
            'ubicacion_actual': 'Depósito Central',
            'kilometraje': 85000,
            'fecha_vencimiento_vtv': date.today() + timedelta(days=180),
            'fecha_vencimiento_seguro': date.today() + timedelta(days=365),
            'numero_poliza': 'POL-2024-001',
            'creado_por': user
        },
        {
            'patente': 'DEF456',
            'marca': 'Scania',
            'modelo': 'R 450',
            'año': 2021,
            'tipo_camion': tipo_grande,
            'capacidad_carga': 15.0,
            'numero_motor': 'SC987654321',
            'numero_chasis': 'YS2R4X20005123456',
            'estado': 'disponible',
            'ubicacion_actual': 'Base Norte',
            'kilometraje': 45000,
            'fecha_vencimiento_vtv': date.today() + timedelta(days=120),
            'fecha_vencimiento_seguro': date.today() + timedelta(days=300),
            'numero_poliza': 'POL-2024-002',
            'creado_por': user
        }
    ]
    
    for camion_data in camiones_data:
        camion, created = Camion.objects.get_or_create(
            patente=camion_data['patente'],
            defaults=camion_data
        )
        if created:
            print(f"✅ Camión creado: {camion.patente} - {camion.marca} {camion.modelo}")
        else:
            print(f"ℹ️  Camión ya existe: {camion.patente}")
    
    # Crear choferes de ejemplo
    choferes_data = [
        {
            'nombre': 'Carlos',
            'apellido': 'González',
            'dni': '12345678',
            'fecha_nacimiento': date(1980, 5, 15),
            'telefono': '+54 11 1234-5678',
            'email': 'carlos.gonzalez@aglsrl.com',
            'direccion': 'Av. Corrientes 1234, CABA',
            'legajo': 'CH001',
            'fecha_ingreso': date(2020, 1, 15),
            'tipo_licencia': 'D2',
            'numero_licencia': 'LIC123456789',
            'fecha_vencimiento_licencia': date.today() + timedelta(days=730),
            'estado': 'disponible',
            'contacto_emergencia_nombre': 'María González',
            'contacto_emergencia_telefono': '+54 11 9876-5432',
            'creado_por': user
        },
        {
            'nombre': 'Roberto',
            'apellido': 'Martínez',
            'dni': '87654321',
            'fecha_nacimiento': date(1975, 8, 22),
            'telefono': '+54 11 5555-1234',
            'email': 'roberto.martinez@aglsrl.com',
            'direccion': 'San Martín 567, San Isidro',
            'legajo': 'CH002',
            'fecha_ingreso': date(2019, 6, 10),
            'tipo_licencia': 'E2',
            'numero_licencia': 'LIC987654321',
            'fecha_vencimiento_licencia': date.today() + timedelta(days=600),
            'estado': 'disponible',
            'contacto_emergencia_nombre': 'Ana Martínez',
            'contacto_emergencia_telefono': '+54 11 7777-8888',
            'creado_por': user
        }
    ]
    
    for chofer_data in choferes_data:
        chofer, created = Chofer.objects.get_or_create(
            dni=chofer_data['dni'],
            defaults=chofer_data
        )
        if created:
            print(f"✅ Chofer creado: {chofer.nombre_completo} (Legajo: {chofer.legajo})")
        else:
            print(f"ℹ️  Chofer ya existe: {chofer.nombre_completo}")

def main():
    """Función principal."""
    print("🚛 Creando datos de ejemplo para transportes...")
    
    try:
        crear_datos_ejemplo()
        print("\n✅ Datos de ejemplo creados exitosamente!")
        
        # Mostrar resumen
        total_camiones = Camion.objects.count()
        total_choferes = Chofer.objects.count()
        total_tipos = TipoCamion.objects.count()
        
        print(f"\n📊 Resumen:")
        print(f"   - Tipos de camión: {total_tipos}")
        print(f"   - Camiones: {total_camiones}")
        print(f"   - Choferes: {total_choferes}")
        
    except Exception as e:
        print(f"\n❌ Error al crear datos de ejemplo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())