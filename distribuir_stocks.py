#!/usr/bin/env python3
"""
Script para crear stocks de ejemplo distribuyendo mercaderías
"""

import os
import sys
import django
from decimal import Decimal
import random

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
    django.setup()

def distribuir_stocks():
    """Distribuir las mercaderías en diferentes ubicaciones y almacenajes"""
    from mercaderias.models import Mercaderia, Ubicacion, Almacenaje, Stock
    
    # Obtener todas las mercaderías
    mercaderias = Mercaderia.objects.filter(activo=True)
    
    # Obtener algunas ubicaciones y almacenajes
    plantas = Ubicacion.objects.filter(tipo='PLANTA')
    
    for mercaderia in mercaderias:
        cantidad_restante = mercaderia.cantidad_kg
        print(f"\nDistribuyendo {mercaderia}:")
        
        # Distribuir la mercadería en 2-3 ubicaciones diferentes
        ubicaciones_elegidas = random.sample(list(plantas), min(2, len(plantas)))
        
        for i, ubicacion in enumerate(ubicaciones_elegidas):
            # Para la última ubicación, poner todo lo que queda
            if i == len(ubicaciones_elegidas) - 1:
                cantidad_a_asignar = cantidad_restante
            else:
                # Asignar entre 30% y 60% de lo que queda
                porcentaje = Decimal(str(random.uniform(0.3, 0.6)))
                cantidad_a_asignar = (cantidad_restante * porcentaje).quantize(Decimal('0.01'))
            
            if cantidad_a_asignar <= 0:
                continue
                
            # Elegir tipo de almacenaje apropiado para el grano
            almacenajes_disponibles = ubicacion.almacenajes.filter(activo=True)
            
            # Para granel, preferir silos, para el resto galpones
            if mercaderia.grano.codigo in ['SOJ', 'MAI']:  # Granos que van bien a granel
                almacenajes_preferidos = almacenajes_disponibles.filter(tipo__in=['SILO', 'SILO_BOLSA'])
                if not almacenajes_preferidos.exists():
                    almacenajes_preferidos = almacenajes_disponibles.filter(tipo='GALPON')
            else:
                almacenajes_preferidos = almacenajes_disponibles.filter(tipo='GALPON')
            
            if almacenajes_preferidos.exists():
                almacenaje = random.choice(almacenajes_preferidos)
                
                # Crear el stock
                stock, created = Stock.objects.get_or_create(
                    ubicacion=ubicacion,
                    almacenaje=almacenaje,
                    mercaderia=mercaderia,
                    defaults={'cantidad_kg': cantidad_a_asignar}
                )
                
                if created:
                    print(f"  ✓ {ubicacion.nombre} - {almacenaje.codigo}: {cantidad_a_asignar} kg")
                else:
                    # Si ya existía, sumar la cantidad
                    stock.cantidad_kg += cantidad_a_asignar
                    stock.save()
                    print(f"  ✓ {ubicacion.nombre} - {almacenaje.codigo}: +{cantidad_a_asignar} kg (total: {stock.cantidad_kg} kg)")
                
                cantidad_restante -= cantidad_a_asignar

def main():
    """Función principal"""
    setup_django()
    
    print("=== DISTRIBUYENDO STOCKS EN UBICACIONES ===")
    
    distribuir_stocks()
    
    print("\n=== DISTRIBUCIÓN COMPLETADA ===")
    
    # Mostrar resumen
    from mercaderias.models import Stock
    
    print("\n=== RESUMEN DE STOCKS ===")
    stocks = Stock.objects.all().order_by('ubicacion__nombre', 'almacenaje__codigo')
    for stock in stocks:
        print(f"{stock.ubicacion.nombre} - {stock.almacenaje.codigo}: {stock.mercaderia.grano.nombre} ({stock.cantidad_kg} kg)")

if __name__ == '__main__':
    main()