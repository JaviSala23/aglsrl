#!/usr/bin/env python3
"""
Script para crear mercaderías de ejemplo
"""

import os
import sys
import django
from decimal import Decimal

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
    django.setup()

def crear_mercaderias_ejemplo():
    """Crear algunas mercaderías de ejemplo"""
    from mercaderias.models import TipoGrano, CalidadGrado, Mercaderia
    
    # Obtener tipos de grano y calidades
    soja = TipoGrano.objects.get(codigo='SOJ')
    maiz = TipoGrano.objects.get(codigo='MAI')
    trigo = TipoGrano.objects.get(codigo='TRI')
    
    premium = CalidadGrado.objects.get(codigo='PREM')
    estandar = CalidadGrado.objects.get(codigo='EST')
    fas = CalidadGrado.objects.get(codigo='FAS')
    
    mercaderias_ejemplo = [
        {
            'grano': soja,
            'calidad_grado': premium,
            'cantidad_kg': Decimal('25000.00'),  # 25 toneladas
            'observaciones': 'Soja premium para exportación'
        },
        {
            'grano': soja,
            'calidad_grado': estandar,
            'cantidad_kg': Decimal('50000.00'),  # 50 toneladas
            'observaciones': 'Soja estándar para mercado interno'
        },
        {
            'grano': maiz,
            'calidad_grado': fas,
            'cantidad_kg': Decimal('30000.00'),  # 30 toneladas
            'observaciones': 'Maíz FAS para exportación'
        },
        {
            'grano': trigo,
            'calidad_grado': estandar,
            'cantidad_kg': Decimal('20000.00'),  # 20 toneladas
            'observaciones': 'Trigo estándar para molienda'
        },
        {
            'grano': maiz,
            'calidad_grado': premium,
            'cantidad_kg': Decimal('15000.00'),  # 15 toneladas
            'observaciones': 'Maíz premium especial'
        }
    ]
    
    for mercaderia_data in mercaderias_ejemplo:
        mercaderia = Mercaderia.objects.create(**mercaderia_data)
        print(f"✓ Creada mercadería: {mercaderia}")

def main():
    """Función principal"""
    setup_django()
    
    print("=== CREANDO MERCADERÍAS DE EJEMPLO ===\n")
    
    crear_mercaderias_ejemplo()
    
    print("\n=== MERCADERÍAS CREADAS ===")

if __name__ == '__main__':
    main()