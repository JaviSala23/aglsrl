#!/usr/bin/env python3
import os
import sys
import django

# Configurar Django
sys.path.append('/home/javisala/Documentos/code/aglsrl')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agl_project.settings')
django.setup()

from tickets.models import TipoMovimiento

print('=== VERIFICANDO TIPOS DE MOVIMIENTO ===')
count = TipoMovimiento.objects.count()
print(f'Total de tipos: {count}')

if count == 0:
    print('❌ NO HAY TIPOS DE MOVIMIENTO - CREANDO...')
    # Crear tipos básicos
    rec = TipoMovimiento.objects.create(
        codigo='REC',
        nombre='Recibido',
        descripcion='Recepción de mercadería',
        activo=True,
        requiere_origen=False,
        requiere_destinatario=True
    )
    env = TipoMovimiento.objects.create(
        codigo='ENV',
        nombre='Enviado', 
        descripcion='Envío de mercadería',
        activo=True,
        requiere_origen=True,
        requiere_destinatario=False
    )
    print(f'✅ Creados: {rec.codigo} y {env.codigo}')
    print(f'Total después de crear: {TipoMovimiento.objects.count()}')
else:
    print('✅ Tipos existentes:')
    for tipo in TipoMovimiento.objects.all():
        print(f'  - {tipo.codigo}: {tipo.nombre} (activo: {tipo.activo})')