from rest_framework import serializers
from .models import Grano, Mercaderia


class GranoSerializer(serializers.ModelSerializer):
    """Serializer para Granos"""
    
    class Meta:
        model = Grano
        fields = ['id', 'nombre', 'codigo', 'descripcion', 'activo']
        

class MercaderiaSerializer(serializers.ModelSerializer):
    """Serializer para Mercaderías"""
    grano_nombre = serializers.CharField(source='grano.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Mercaderia
        fields = [
            'id', 'grano', 'grano_nombre', 'tipo', 'tipo_display', 
            'estado', 'estado_display', 'propietario_nombre', 'propietario_contacto',
            'humedad_porcentaje', 'proteina_porcentaje', 'cuerpos_extranos_porcentaje',
            'granos_danados_porcentaje', 'peso_hectolitro', 'fecha_ingreso',
            'fecha_analisis', 'fecha_vencimiento', 'observaciones'
        ]
        read_only_fields = ['grano_nombre', 'tipo_display', 'estado_display']