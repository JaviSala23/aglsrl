"""
Script para crear datos iniciales de tickets.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from tickets.models import TipoTicket, PrioridadTicket, EstadoTicket

def crear_datos_iniciales():
    print("Creando datos iniciales para tickets...")
    
    # Tipos de tickets
    tipos = [
        {
            'nombre': 'Mantenimiento',
            'descripcion': 'Tickets relacionados con mantenimiento de equipos',
            'color': '#28a745',
            'icono': 'fas fa-tools'
        },
        {
            'nombre': 'Incidencia Técnica',
            'descripcion': 'Problemas técnicos o fallas en sistemas',
            'color': '#dc3545',
            'icono': 'fas fa-exclamation-triangle'
        },
        {
            'nombre': 'Solicitud de Servicio',
            'descripcion': 'Solicitudes de servicios diversos',
            'color': '#007bff',
            'icono': 'fas fa-hand-holding'
        },
        {
            'nombre': 'Mejora',
            'descripcion': 'Propuestas de mejora o modificaciones',
            'color': '#17a2b8',
            'icono': 'fas fa-lightbulb'
        },
        {
            'nombre': 'Consulta',
            'descripcion': 'Consultas generales o información',
            'color': '#6f42c1',
            'icono': 'fas fa-question-circle'
        }
    ]
    
    for tipo_data in tipos:
        tipo, created = TipoTicket.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"✓ Creado tipo: {tipo.nombre}")
        else:
            print(f"- Ya existe tipo: {tipo.nombre}")
    
    # Prioridades
    prioridades = [
        {
            'nombre': 'Baja',
            'nivel': 1,
            'color': '#28a745',
            'descripcion': 'Prioridad baja - No urgente'
        },
        {
            'nombre': 'Normal',
            'nivel': 2,
            'color': '#17a2b8',
            'descripcion': 'Prioridad normal - Rutinario'
        },
        {
            'nombre': 'Alta',
            'nivel': 3,
            'color': '#ffc107',
            'descripcion': 'Prioridad alta - Requiere atención pronta'
        },
        {
            'nombre': 'Urgente',
            'nivel': 4,
            'color': '#fd7e14',
            'descripcion': 'Prioridad urgente - Atención inmediata'
        },
        {
            'nombre': 'Crítica',
            'nivel': 5,
            'color': '#dc3545',
            'descripcion': 'Prioridad crítica - Máxima urgencia'
        }
    ]
    
    for prioridad_data in prioridades:
        prioridad, created = PrioridadTicket.objects.get_or_create(
            nivel=prioridad_data['nivel'],
            defaults=prioridad_data
        )
        if created:
            print(f"✓ Creada prioridad: {prioridad.nombre}")
        else:
            print(f"- Ya existe prioridad: {prioridad.nombre}")
    
    # Estados
    estados = [
        {
            'nombre': 'Nuevo',
            'descripcion': 'Ticket recién creado',
            'color': '#6c757d',
            'es_inicial': True,
            'es_final': False
        },
        {
            'nombre': 'En Proceso',
            'descripcion': 'Ticket en proceso de resolución',
            'color': '#007bff',
            'es_inicial': False,
            'es_final': False
        },
        {
            'nombre': 'Esperando Respuesta',
            'descripcion': 'Aguardando respuesta del solicitante',
            'color': '#ffc107',
            'es_inicial': False,
            'es_final': False
        },
        {
            'nombre': 'Resuelto',
            'descripcion': 'Ticket resuelto satisfactoriamente',
            'color': '#28a745',
            'es_inicial': False,
            'es_final': True
        },
        {
            'nombre': 'Cerrado',
            'descripcion': 'Ticket cerrado',
            'color': '#6c757d',
            'es_inicial': False,
            'es_final': True
        },
        {
            'nombre': 'Cancelado',
            'descripcion': 'Ticket cancelado por el solicitante',
            'color': '#dc3545',
            'es_inicial': False,
            'es_final': True
        }
    ]
    
    for estado_data in estados:
        estado, created = EstadoTicket.objects.get_or_create(
            nombre=estado_data['nombre'],
            defaults=estado_data
        )
        if created:
            print(f"✓ Creado estado: {estado.nombre}")
        else:
            print(f"- Ya existe estado: {estado.nombre}")
    
    print("\n¡Datos iniciales creados exitosamente!")
    print("\nPuedes empezar a usar el sistema de tickets.")

if __name__ == '__main__':
    crear_datos_iniciales()