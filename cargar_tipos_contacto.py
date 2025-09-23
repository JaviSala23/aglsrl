#!/usr/bin/env python
"""
Script para cargar tipos de contacto iniciales.
"""
import os
import sys
import django

# Configurar el path y Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

# Importar modelos después de configurar Django
from agenda.models import TipoContacto

def cargar_tipos_contacto():
    """Cargar tipos de contacto iniciales."""
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
    existing_count = 0

    print("🔄 Cargando tipos de contacto...")
    
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
            print(f'✓ Creado: {tipo_contacto.nombre} ({tipo_contacto.color})')
        else:
            existing_count += 1
            print(f'◦ Ya existe: {tipo_contacto.nombre}')

    print(f'\n✅ Proceso completado:')
    print(f'   📊 {created_count} tipos de contacto creados')
    print(f'   📊 {existing_count} tipos de contacto ya existían')
    print(f'   📊 {TipoContacto.objects.filter(activo=True).count()} tipos disponibles en total')

    print('\n📋 Tipos de contacto disponibles:')
    for tipo in TipoContacto.objects.filter(activo=True).order_by('nombre'):
        print(f'   • {tipo.nombre} - {tipo.descripcion}')

if __name__ == '__main__':
    cargar_tipos_contacto()