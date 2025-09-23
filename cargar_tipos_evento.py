#!/usr/bin/env python
"""
Script para cargar tipos de evento iniciales.
"""
import os
import sys
import django

# Configurar el path y Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

# Importar modelos después de configurar Django
from agenda.models import TipoEvento

def cargar_tipos_evento():
    """Cargar tipos de evento iniciales."""
    tipos_evento = [
        {
            'nombre': 'Reunión',
            'descripcion': 'Reuniones de trabajo, juntas, etc.',
            'color': '#007bff',
            'icono': 'bi-people'
        },
        {
            'nombre': 'Cita',
            'descripcion': 'Citas personales o profesionales',
            'color': '#28a745',
            'icono': 'bi-calendar-check'
        },
        {
            'nombre': 'Llamada',
            'descripcion': 'Llamadas telefónicas programadas',
            'color': '#17a2b8',
            'icono': 'bi-telephone'
        },
        {
            'nombre': 'Viaje',
            'descripcion': 'Viajes de trabajo o personales',
            'color': '#ffc107',
            'icono': 'bi-airplane'
        },
        {
            'nombre': 'Capacitación',
            'descripcion': 'Cursos, talleres, entrenamientos',
            'color': '#6f42c1',
            'icono': 'bi-book'
        },
        {
            'nombre': 'Evento Social',
            'descripcion': 'Eventos sociales y de networking',
            'color': '#fd7e14',
            'icono': 'bi-chat-heart'
        },
        {
            'nombre': 'Mantenimiento',
            'descripcion': 'Mantenimiento de equipos, vehículos, etc.',
            'color': '#6c757d',
            'icono': 'bi-tools'
        },
        {
            'nombre': 'Inspección',
            'descripcion': 'Inspecciones, auditorías, controles',
            'color': '#dc3545',
            'icono': 'bi-search'
        },
        {
            'nombre': 'Entrega',
            'descripcion': 'Entregas de productos o servicios',
            'color': '#20c997',
            'icono': 'bi-truck'
        },
        {
            'nombre': 'Recordatorio',
            'descripcion': 'Recordatorios generales',
            'color': '#e83e8c',
            'icono': 'bi-bell'
        }
    ]

    created_count = 0
    existing_count = 0

    print("🔄 Cargando tipos de evento...")
    
    for tipo_data in tipos_evento:
        tipo_evento, created = TipoEvento.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults={
                'descripcion': tipo_data['descripcion'],
                'color': tipo_data['color'],
                'icono': tipo_data['icono'],
                'activo': True
            }
        )
        
        if created:
            created_count += 1
            print(f'✓ Creado: {tipo_evento.nombre} ({tipo_evento.color})')
        else:
            existing_count += 1
            print(f'◦ Ya existe: {tipo_evento.nombre}')

    print(f'\n✅ Proceso completado:')
    print(f'   📊 {created_count} tipos de evento creados')
    print(f'   📊 {existing_count} tipos de evento ya existían')
    print(f'   📊 {TipoEvento.objects.filter(activo=True).count()} tipos disponibles en total')

    print('\n📋 Tipos de evento disponibles:')
    for tipo in TipoEvento.objects.filter(activo=True).order_by('nombre'):
        print(f'   • {tipo.nombre} - {tipo.descripcion}')

if __name__ == '__main__':
    cargar_tipos_evento()