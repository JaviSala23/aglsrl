"""
Script para inicializar el sistema de tickets de mercadería.
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from tickets.models import TipoMovimiento, EstadoTicket


def crear_tipos_movimiento():
    """Crear tipos de movimiento de mercadería."""
    tipos = [
        {
            'tipo': 'ingreso',
            'nombre': 'Ingreso de Mercadería',
            'descripcion': 'Ingreso de mercadería desde proveedores',
            'icono': 'fas fa-arrow-down',
            'color': '#28a745',
        },
        {
            'tipo': 'egreso',
            'nombre': 'Egreso de Mercadería',
            'descripcion': 'Egreso de mercadería hacia clientes',
            'icono': 'fas fa-arrow-up',
            'color': '#dc3545',
        },
    ]
    
    print("Creando tipos de movimiento...")
    for tipo_data in tipos:
        tipo, created = TipoMovimiento.objects.get_or_create(
            tipo=tipo_data['tipo'],
            defaults=tipo_data
        )
        if created:
            print(f"  ✓ Creado: {tipo.nombre}")
        else:
            print(f"  - Ya existe: {tipo.nombre}")


def crear_estados():
    """Crear estados de tickets."""
    estados = [
        {
            'codigo': 'pendiente',
            'nombre': 'Pendiente',
            'descripcion': 'Ticket creado, pendiente de procesamiento',
            'color': '#ffc107',
            'es_inicial': True,
            'es_final': False,
        },
        {
            'codigo': 'procesando',
            'nombre': 'Procesando',
            'descripcion': 'Ticket en proceso de ejecución',
            'color': '#17a2b8',
            'es_inicial': False,
            'es_final': False,
        },
        {
            'codigo': 'completado',
            'nombre': 'Completado',
            'descripcion': 'Ticket completado exitosamente',
            'color': '#28a745',
            'es_inicial': False,
            'es_final': True,
        },
        {
            'codigo': 'cancelado',
            'nombre': 'Cancelado',
            'descripcion': 'Ticket cancelado',
            'color': '#dc3545',
            'es_inicial': False,
            'es_final': True,
        },
    ]
    
    print("Creando estados...")
    for estado_data in estados:
        estado, created = EstadoTicket.objects.get_or_create(
            codigo=estado_data['codigo'],
            defaults=estado_data
        )
        if created:
            print(f"  ✓ Creado: {estado.nombre}")
        else:
            print(f"  - Ya existe: {estado.nombre}")


def main():
    """Función principal."""
    print("=" * 60)
    print("INICIALIZANDO SISTEMA DE TICKETS DE MERCADERÍA - AGL SRL")
    print("=" * 60)
    
    try:
        crear_tipos_movimiento()
        print()
        crear_estados()
        print()
        print("=" * 60)
        print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print()
        print("El sistema de tickets de mercadería está listo para usar.")
        print("Próximos pasos:")
        print("1. Crear usuarios en el admin de Django")
        print("2. Verificar datos de mercaderías, clientes y almacenajes")
        print("3. Comenzar a crear tickets de ingreso y egreso")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        return False
    
    return True


if __name__ == '__main__':
    main()