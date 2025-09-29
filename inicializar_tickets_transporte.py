#!/usr/bin/env python3
"""
Script para inicializar datos del nuevo sistema de tickets de transporte.
Refleja el flujo real del negocio de AGL SRL.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from tickets.models import TipoMovimiento, EstadoTicket


def inicializar_tipos_movimiento():
    """Crear tipos de movimiento según el flujo real."""
    tipos = [
        {
            'codigo': 'REC',
            'nombre': 'Recepción de Mercadería',
            'descripcion': 'Recepción de camiones con mercadería desde proveedores/productores',
            'requiere_origen': True,  # Requiere proveedor/productor
            'requiere_destinatario': False,
            'activo': True
        },
        {
            'codigo': 'ENV',
            'nombre': 'Envío de Mercadería',
            'descripcion': 'Envío de mercadería hacia clientes/destinos',
            'requiere_origen': False,
            'requiere_destinatario': True,  # Requiere cliente/destino
            'activo': True
        }
    ]
    
    for tipo_data in tipos:
        tipo, created = TipoMovimiento.objects.get_or_create(
            codigo=tipo_data['codigo'],
            defaults=tipo_data
        )
        if created:
            print(f"✓ Tipo de movimiento creado: {tipo.nombre}")
        else:
            print(f"• Tipo de movimiento ya existe: {tipo.nombre}")


def inicializar_estados_ticket():
    """Crear estados que reflejan el flujo real del negocio."""
    estados = [
        {
            'codigo': 'LLEGADA',
            'nombre': 'Camión Llegado',
            'descripcion': 'Camión ha llegado, se registra patente y datos básicos',
            'color': '#17a2b8',
            'es_inicial': True,
            'es_final': False,
            'permite_edicion': True,
            'activo': True
        },
        {
            'codigo': 'ANALISIS',
            'nombre': 'En Análisis',
            'descripcion': 'Se están realizando análisis de las mercaderías',
            'color': '#ffc107',
            'es_inicial': False,
            'es_final': False,
            'permite_edicion': True,
            'activo': True
        },
        {
            'codigo': 'PESAJE',
            'nombre': 'En Pesaje',
            'descripcion': 'Se está realizando el pesaje (bruto/tara)',
            'color': '#fd7e14',
            'es_inicial': False,
            'es_final': False,
            'permite_edicion': True,
            'activo': True
        },
        {
            'codigo': 'PROCESO',
            'nombre': 'En Proceso',
            'descripcion': 'Ticket completo, procesando mercadería',
            'color': '#6f42c1',
            'es_inicial': False,
            'es_final': False,
            'permite_edicion': True,
            'activo': True
        },
        {
            'codigo': 'COMPLETADO',
            'nombre': 'Completado',
            'descripcion': 'Proceso completado, camión puede retirarse',
            'color': '#28a745',
            'es_inicial': False,
            'es_final': True,
            'permite_edicion': False,
            'activo': True
        },
        {
            'codigo': 'SALIDA',
            'nombre': 'Camión Retirado',
            'descripcion': 'Camión se ha retirado del establecimiento',
            'color': '#6c757d',
            'es_inicial': False,
            'es_final': True,
            'permite_edicion': False,
            'activo': True
        },
        {
            'codigo': 'CANCELADO',
            'nombre': 'Cancelado',
            'descripcion': 'Ticket cancelado por algún motivo',
            'color': '#dc3545',
            'es_inicial': False,
            'es_final': True,
            'permite_edicion': False,
            'activo': True
        }
    ]
    
    for estado_data in estados:
        estado, created = EstadoTicket.objects.get_or_create(
            codigo=estado_data['codigo'],
            defaults=estado_data
        )
        if created:
            print(f"✓ Estado creado: {estado.nombre}")
        else:
            print(f"• Estado ya existe: {estado.nombre}")


def mostrar_resumen():
    """Mostrar resumen del sistema inicializado."""
    print("\n" + "="*60)
    print("SISTEMA DE TICKETS DE TRANSPORTE - AGL SRL")
    print("="*60)
    
    print(f"\n🚛 Tipos de Movimiento: {TipoMovimiento.objects.count()}")
    for tipo in TipoMovimiento.objects.all():
        reqs = []
        if tipo.requiere_origen:
            reqs.append("origen")
        if tipo.requiere_destinatario:
            reqs.append("destinatario")
        req_text = f" (requiere: {', '.join(reqs)})" if reqs else ""
        print(f"   • {tipo.codigo}: {tipo.nombre}{req_text}")
    
    print(f"\n📋 Estados de Ticket: {EstadoTicket.objects.count()}")
    for estado in EstadoTicket.objects.all():
        tipo_estado = ""
        if estado.es_inicial:
            tipo_estado = " [INICIAL]"
        elif estado.es_final:
            tipo_estado = " [FINAL]"
        print(f"   • {estado.codigo}: {estado.nombre}{tipo_estado}")
    
    print("\n" + "="*60)
    print("✅ SISTEMA INICIALIZADO - FLUJO REAL DEL NEGOCIO")
    print("="*60)
    
    print("\n🔄 FLUJO TÍPICO DE RECEPCIÓN:")
    print("1. Llega camión → Estado: LLEGADA")
    print("2. Se registra patente, chofer, mercaderías")
    print("3. Se realizan análisis → Estado: ANALISIS")
    print("4. Se pesa camión → Estado: PESAJE")
    print("5. Se procesa mercadería → Estado: PROCESO")
    print("6. Se completa → Estado: COMPLETADO")
    print("7. Camión se retira → Estado: SALIDA")
    
    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Iniciar servidor: python manage.py runserver")
    print("2. Acceder al admin: http://localhost:8000/admin/")
    print("3. Crear tickets en: http://localhost:8000/tickets/")
    print("4. Verificar que existan datos de:")
    print("   - Mercaderías en el módulo correspondiente")
    print("   - Cuentas (proveedores/clientes)")
    print("   - Choferes en transportes")
    print("   - Ubicaciones de almacenaje")


def main():
    """Función principal."""
    print("🚀 Inicializando sistema de tickets de transporte...")
    print("Basado en el flujo real del negocio de AGL SRL\n")
    
    try:
        inicializar_tipos_movimiento()
        print()
        inicializar_estados_ticket()
        mostrar_resumen()
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()