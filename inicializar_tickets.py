"""
Script para poblar la base de datos con datos iniciales del sistema de tickets.
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from tickets.models import TipoTicket, PrioridadTicket, EstadoTicket


def crear_tipos_ticket():
    """Crear tipos de ticket."""
    tipos = [
        {
            'nombre': 'Mantenimiento Preventivo',
            'descripcion': 'Mantenimiento programado de equipos y sistemas',
            'icono': 'fas fa-tools',
            'color': '#28a745',
        },
        {
            'nombre': 'Mantenimiento Correctivo',
            'descripcion': 'Reparación de equipos averiados',
            'icono': 'fas fa-wrench',
            'color': '#dc3545',
        },
        {
            'nombre': 'Incidencia Técnica',
            'descripcion': 'Problemas técnicos con equipos o sistemas',
            'icono': 'fas fa-exclamation-triangle',
            'color': '#fd7e14',
        },
        {
            'nombre': 'Solicitud de Instalación',
            'descripcion': 'Instalación de nuevos equipos o sistemas',
            'icono': 'fas fa-plus-circle',
            'color': '#007bff',
        },
        {
            'nombre': 'Mejora del Sistema',
            'descripcion': 'Mejoras y optimizaciones de sistemas existentes',
            'icono': 'fas fa-arrow-up',
            'color': '#17a2b8',
        },
        {
            'nombre': 'Capacitación',
            'descripcion': 'Capacitación del personal en uso de equipos',
            'icono': 'fas fa-graduation-cap',
            'color': '#6f42c1',
        },
        {
            'nombre': 'Calibración',
            'descripcion': 'Calibración de instrumentos de medición',
            'icono': 'fas fa-balance-scale',
            'color': '#20c997',
        },
        {
            'nombre': 'Consulta Técnica',
            'descripcion': 'Consultas sobre procedimientos técnicos',
            'icono': 'fas fa-question-circle',
            'color': '#6c757d',
        },
    ]
    
    print("Creando tipos de ticket...")
    for tipo_data in tipos:
        tipo, created = TipoTicket.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"  ✓ Creado: {tipo.nombre}")
        else:
            print(f"  - Ya existe: {tipo.nombre}")


def crear_prioridades():
    """Crear niveles de prioridad."""
    prioridades = [
        {
            'nombre': 'Baja',
            'nivel': 1,
            'descripcion': 'Problema menor que no afecta las operaciones críticas',
            'color': '#6c757d',
        },
        {
            'nombre': 'Normal',
            'nivel': 2,
            'descripcion': 'Problema que afecta moderadamente las operaciones',
            'color': '#28a745',
        },
        {
            'nombre': 'Alta',
            'nivel': 3,
            'descripcion': 'Problema que afecta significativamente las operaciones',
            'color': '#ffc107',
        },
        {
            'nombre': 'Urgente',
            'nivel': 4,
            'descripcion': 'Problema urgente que requiere atención rápida',
            'color': '#fd7e14',
        },
        {
            'nombre': 'Crítica',
            'nivel': 5,
            'descripcion': 'Requiere atención inmediata - Sistema caído o peligro de seguridad',
            'color': '#dc3545',
        },
    ]
    
    print("Creando prioridades...")
    for prioridad_data in prioridades:
        prioridad, created = PrioridadTicket.objects.get_or_create(
            nivel=prioridad_data['nivel'],
            defaults=prioridad_data
        )
        if created:
            print(f"  ✓ Creado: {prioridad.nombre} (Nivel {prioridad.nivel})")
        else:
            print(f"  - Ya existe: {prioridad.nombre}")


def crear_estados():
    """Crear estados de ticket."""
    estados = [
        {
            'nombre': 'Nuevo',
            'descripcion': 'Ticket recién creado, pendiente de asignación',
            'color': '#17a2b8',
            'es_inicial': True,
            'es_final': False,
        },
        {
            'nombre': 'Asignado',
            'descripcion': 'Ticket asignado a un técnico',
            'color': '#007bff',
            'es_inicial': False,
            'es_final': False,
        },
        {
            'nombre': 'En Proceso',
            'descripcion': 'Se está trabajando en el ticket',
            'color': '#ffc107',
            'es_inicial': False,
            'es_final': False,
        },
        {
            'nombre': 'En Espera',
            'descripcion': 'Ticket pausado, esperando información o recursos',
            'color': '#6c757d',
            'es_inicial': False,
            'es_final': False,
        },
        {
            'nombre': 'Resuelto',
            'descripcion': 'Problema resuelto, pendiente de verificación',
            'color': '#28a745',
            'es_inicial': False,
            'es_final': False,
        },
        {
            'nombre': 'Cerrado',
            'descripcion': 'Ticket completado y cerrado',
            'color': '#343a40',
            'es_inicial': False,
            'es_final': True,
        },
        {
            'nombre': 'Cancelado',
            'descripcion': 'Ticket cancelado por el solicitante o administrador',
            'color': '#dc3545',
            'es_inicial': False,
            'es_final': True,
        },
    ]
    
    print("Creando estados...")
    for estado_data in estados:
        estado, created = EstadoTicket.objects.get_or_create(
            nombre=estado_data['nombre'],
            defaults=estado_data
        )
        if created:
            print(f"  ✓ Creado: {estado.nombre}")
        else:
            print(f"  - Ya existe: {estado.nombre}")


def main():
    """Función principal."""
    print("=" * 50)
    print("INICIALIZANDO SISTEMA DE TICKETS - AGL SRL")
    print("=" * 50)
    
    try:
        crear_tipos_ticket()
        print()
        crear_prioridades()
        print()
        crear_estados()
        print()
        print("=" * 50)
        print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        print()
        print("El sistema de tickets está listo para usar.")
        print("Próximos pasos:")
        print("1. Crear usuarios en el admin de Django")
        print("2. Asignar permisos apropiados")
        print("3. Comenzar a crear tickets")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        return False
    
    return True


if __name__ == '__main__':
    main()