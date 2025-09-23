#!/usr/bin/env python3
"""
Script para crear datos iniciales del módulo de transportes.
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from django.contrib.auth.models import User
from transportes.models import TipoCamion, Camion, Chofer, Viaje, TicketBalanza
from cuentas.models import cuenta

def crear_tipos_camion():
    """Crear tipos de camión básicos."""
    tipos_camion = [
        {
            'nombre': 'Camión Pequeño',
            'descripcion': 'Camión para cargas ligeras y medianas',
            'capacidad_maxima': 3.5
        },
        {
            'nombre': 'Camión Mediano',
            'descripcion': 'Camión para cargas medianas y pesadas',
            'capacidad_maxima': 7.5
        },
        {
            'nombre': 'Camión Grande',
            'descripcion': 'Camión para cargas pesadas',
            'capacidad_maxima': 15.0
        },
        {
            'nombre': 'Semi-remolque',
            'descripcion': 'Tractocamión con semi-remolque',
            'capacidad_maxima': 30.0
        },
        {
            'nombre': 'Camión Volcador',
            'descripcion': 'Camión volcador para materiales de construcción',
            'capacidad_maxima': 20.0
        }
    ]
    
    for tipo_data in tipos_camion:
        tipo, created = TipoCamion.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"✅ Tipo de camión creado: {tipo.nombre}")
        else:
            print(f"ℹ️  Tipo de camión ya existe: {tipo.nombre}")

def main():
    """Función principal."""
    print("🚛 Inicializando datos del módulo de transportes...")
    
    try:
        crear_tipos_camion()
        print("\n✅ Datos iniciales creados exitosamente!")
        
        # Mostrar resumen
        total_tipos = TipoCamion.objects.count()
        print(f"\n📊 Resumen:")
        print(f"   - Tipos de camión: {total_tipos}")
        
    except Exception as e:
        print(f"\n❌ Error al crear datos iniciales: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())