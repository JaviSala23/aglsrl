"""
Serializers avanzados para el módulo de cuentas.
Incluye validaciones personalizadas, campos anidados y optimizaciones.
"""
from rest_framework import serializers
from django.db import transaction
from django.core.validators import RegexValidator, EmailValidator
from .models import (
    pais, provincia, localidad, tipo_documento, situacionIva, tipo_cuenta,
    cuenta, contacto_cuenta, direccion
)


class BaseReadOnlySerializer(serializers.ModelSerializer):
    """Serializer base para modelos de solo lectura como maestros."""
    
    class Meta:
        abstract = True


class PaisSerializer(BaseReadOnlySerializer):
    """Serializer para países."""
    
    class Meta:
        model = pais
        fields = ['id_pais', 'nombre']
        read_only_fields = ['id_pais']


class ProvinciaSerializer(BaseReadOnlySerializer):
    """Serializer para provincias con información del país."""
    
    pais_nombre = serializers.CharField(source='pais_idpais.nombre', read_only=True)
    
    class Meta:
        model = provincia
        fields = ['id_provincia', 'nombre_provincia', 'codigo_provincia', 'pais_idpais', 'pais_nombre']
        read_only_fields = ['id_provincia']


class LocalidadSerializer(BaseReadOnlySerializer):
    """Serializer para localidades con información jerárquica completa."""
    
    provincia_nombre = serializers.CharField(source='provincia_id_provincia.nombre_provincia', read_only=True)
    pais_nombre = serializers.CharField(source='provincia_id_provincia.pais_idpais.nombre', read_only=True)
    
    class Meta:
        model = localidad
        fields = [
            'id_localidad', 'nombre_localidad', 'cp_localidad', 
            'provincia_id_provincia', 'provincia_nombre', 'pais_nombre'
        ]
        read_only_fields = ['id_localidad']


class TipoDocumentoSerializer(BaseReadOnlySerializer):
    """Serializer para tipos de documento."""
    
    class Meta:
        model = tipo_documento
        fields = ['idtipo_documento', 'descripcion', 'cod_afip']
        read_only_fields = ['idtipo_documento']


class SituacionIvaSerializer(BaseReadOnlySerializer):
    """Serializer para situaciones de IVA."""
    
    class Meta:
        model = situacionIva
        fields = ['idsituacionIva', 'descripcion', 'reducida', 'codigo_afip']
        read_only_fields = ['idsituacionIva']


class TipoCuentaSerializer(BaseReadOnlySerializer):
    """Serializer para tipos de cuenta."""
    
    class Meta:
        model = tipo_cuenta
        fields = ['id_tipo_cuenta', 'descripcion']
        read_only_fields = ['id_tipo_cuenta']


class DireccionSerializer(serializers.ModelSerializer):
    """Serializer para direcciones con validaciones geográficas."""
    
    # Campos de solo lectura para mostrar información jerárquica
    localidad_nombre = serializers.CharField(source='localidad_idlocalidad.nombre_localidad', read_only=True)
    provincia_nombre = serializers.CharField(source='provincia_idprovincia.nombre_provincia', read_only=True)
    pais_nombre = serializers.CharField(source='pais_id.nombre', read_only=True)
    
    # Validador para código postal argentino
    cp = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]?\d{4}[A-Z]{3}?$',
                message="Código postal inválido. Formato: 1234 o A1234ABC"
            )
        ]
    )
    
    class Meta:
        model = direccion
        fields = [
            'id_direccion', 'cuenta_id', 'etiqueta', 'calle', 'numero', 
            'piso', 'dpto', 'pais_id', 'provincia_idprovincia', 
            'localidad_idlocalidad', 'cp', 'es_principal',
            'localidad_nombre', 'provincia_nombre', 'pais_nombre'
        ]
        read_only_fields = ['id_direccion']
    
    def validate(self, data):
        """Validación de negocio para direcciones."""
        cuenta_id = data.get('cuenta_id')
        es_principal = data.get('es_principal', False)
        
        # Validar que solo haya una dirección principal por cuenta
        if es_principal and cuenta_id:
            existing_principal = direccion.objects.filter(
                cuenta_id=cuenta_id, 
                es_principal=True
            ).exclude(id_direccion=self.instance.id_direccion if self.instance else None)
            
            if existing_principal.exists():
                raise serializers.ValidationError(
                    "Ya existe una dirección principal para esta cuenta."
                )
        
        return data


class ContactoCuentaSerializer(serializers.ModelSerializer):
    """Serializer para contactos con validaciones de comunicación."""
    
    # Validadores personalizados
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        validators=[EmailValidator(message="Email inválido")]
    )
    
    telefono = serializers.CharField(
        max_length=40,
        required=False,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex=r'^[\d\s\-\+\(\)]{7,15}$',
                message="Teléfono inválido. Solo números, espacios, guiones y paréntesis."
            )
        ]
    )
    
    celular = serializers.CharField(
        max_length=40,
        required=False,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex=r'^[\d\s\-\+\(\)]{7,15}$',
                message="Celular inválido. Solo números, espacios, guiones y paréntesis."
            )
        ]
    )
    
    class Meta:
        model = contacto_cuenta
        fields = [
            'id_contacto', 'cuenta_id', 'nombre', 'cargo', 
            'email', 'telefono', 'celular', 'notas', 'activo'
        ]
        read_only_fields = ['id_contacto']
    
    def validate(self, data):
        """Validar que al menos un medio de contacto esté presente."""
        email = data.get('email', '').strip()
        telefono = data.get('telefono', '').strip()
        celular = data.get('celular', '').strip()
        
        if not any([email, telefono, celular]):
            raise serializers.ValidationError(
                "Debe proporcionar al menos un medio de contacto (email, teléfono o celular)."
            )
        
        return data


class CuentaListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de cuentas."""
    
    tipo_cuenta_descripcion = serializers.CharField(
        source='tipo_cuenta_id_tipo_cuenta.descripcion', 
        read_only=True
    )
    situacion_iva_descripcion = serializers.CharField(
        source='situacionIva_idsituacionIva.descripcion', 
        read_only=True
    )
    tipo_documento_descripcion = serializers.CharField(
        source='tipo_documento_idtipo_documento.descripcion', 
        read_only=True
    )
    
    class Meta:
        model = cuenta
        fields = [
            'id_cuenta', 'razon_social', 'nombre_fantasia', 
            'numero_documento', 'tipo_documento_descripcion',
            'email_cuenta', 'telefono_cuenta', 'activo',
            'tipo_cuenta_descripcion', 'situacion_iva_descripcion'
        ]


class CuentaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de cuenta con relaciones anidadas."""
    
    # Campos de solo lectura para información descriptiva
    tipo_documento_descripcion = serializers.CharField(
        source='tipo_documento_idtipo_documento.descripcion', 
        read_only=True
    )
    situacion_iva_descripcion = serializers.CharField(
        source='situacionIva_idsituacionIva.descripcion', 
        read_only=True
    )
    tipo_cuenta_descripcion = serializers.CharField(
        source='tipo_cuenta_id_tipo_cuenta.descripcion', 
        read_only=True
    )
    localidad_nombre = serializers.CharField(
        source='localidad_idlocalidad.nombre_localidad', 
        read_only=True
    )
    provincia_nombre = serializers.CharField(
        source='provincia_idprovincia.nombre_provincia', 
        read_only=True
    )
    pais_nombre = serializers.CharField(
        source='pais_id.nombre', 
        read_only=True
    )
    
    # Relaciones anidadas
    contactos = ContactoCuentaSerializer(many=True, read_only=True)
    direcciones = DireccionSerializer(many=True, read_only=True)
    
    # Campos calculados
    contactos_count = serializers.SerializerMethodField()
    direcciones_count = serializers.SerializerMethodField()
    
    # Validadores para campos específicos
    numero_documento = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^[\d\-]{8,13}$',
                message="Número de documento inválido. Solo números y guiones."
            )
        ]
    )
    
    email_cuenta = serializers.EmailField(
        required=False,
        allow_blank=True,
        validators=[EmailValidator(message="Email inválido")]
    )
    
    class Meta:
        model = cuenta
        fields = [
            'id_cuenta', 'razon_social', 'nombre_fantasia',
            'numero_documento', 'tipo_documento_idtipo_documento', 'tipo_documento_descripcion',
            'direccion_cuenta', 'pais_id', 'provincia_idprovincia', 'localidad_idlocalidad',
            'pais_nombre', 'provincia_nombre', 'localidad_nombre',
            'telefono_cuenta', 'celular_cuenta', 'email_cuenta',
            'tipo_cuenta_id_tipo_cuenta', 'tipo_cuenta_descripcion',
            'situacionIva_idsituacionIva', 'situacion_iva_descripcion',
            'activo', 'fecha_alta', 'fecha_baja',
            'contactos', 'direcciones',
            'contactos_count', 'direcciones_count'
        ]
        read_only_fields = ['id_cuenta', 'fecha_alta']
    
    def get_contactos_count(self, obj):
        """Contador de contactos activos."""
        return obj.contactos.filter(activo=True).count()
    
    def get_direcciones_count(self, obj):
        """Contador de direcciones."""
        return obj.direcciones.count()
    
    def validate_numero_documento(self, value):
        """Validación específica del número de documento."""
        # Remover guiones y espacios para validación
        clean_value = value.replace('-', '').replace(' ', '')
        
        # Validar longitud según tipo de documento
        if hasattr(self.instance, 'tipo_documento_idtipo_documento'):
            tipo_doc = self.instance.tipo_documento_idtipo_documento
            if tipo_doc and tipo_doc.descripcion == 'CUIT' and len(clean_value) != 11:
                raise serializers.ValidationError("CUIT debe tener 11 dígitos")
            elif tipo_doc and tipo_doc.descripcion == 'DNI' and len(clean_value) not in [7, 8]:
                raise serializers.ValidationError("DNI debe tener 7 u 8 dígitos")
        
        return value
    
    def validate(self, data):
        """Validaciones de negocio a nivel de cuenta."""
        # Validar unicidad de documento
        numero_documento = data.get('numero_documento')
        tipo_documento = data.get('tipo_documento_idtipo_documento')
        
        if numero_documento and tipo_documento:
            existing_cuenta = cuenta.objects.filter(
                numero_documento=numero_documento,
                tipo_documento_idtipo_documento=tipo_documento
            ).exclude(id_cuenta=self.instance.id_cuenta if self.instance else None)
            
            if existing_cuenta.exists():
                raise serializers.ValidationError(
                    "Ya existe una cuenta con este tipo y número de documento."
                )
        
        # Validar fecha de baja
        fecha_baja = data.get('fecha_baja')
        activo = data.get('activo', True)
        
        if not activo and not fecha_baja:
            from django.utils import timezone
            data['fecha_baja'] = timezone.now().date()
        elif activo and fecha_baja:
            data['fecha_baja'] = None
        
        return data


class CuentaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para creación y actualización de cuentas con transacciones."""
    
    # Campos anidados para creación/actualización
    contactos_data = ContactoCuentaSerializer(many=True, required=False, write_only=True)
    direcciones_data = DireccionSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = cuenta
        fields = [
            'razon_social', 'nombre_fantasia',
            'numero_documento', 'tipo_documento_idtipo_documento',
            'direccion_cuenta', 'pais_id', 'provincia_idprovincia', 'localidad_idlocalidad',
            'telefono_cuenta', 'celular_cuenta', 'email_cuenta',
            'tipo_cuenta_id_tipo_cuenta', 'situacionIva_idsituacionIva',
            'activo', 'contactos_data', 'direcciones_data'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear cuenta con contactos y direcciones de forma transaccional."""
        contactos_data = validated_data.pop('contactos_data', [])
        direcciones_data = validated_data.pop('direcciones_data', [])
        
        # Crear la cuenta
        cuenta_instance = cuenta.objects.create(**validated_data)
        
        # Crear contactos
        for contacto_data in contactos_data:
            contacto_data['cuenta_id'] = cuenta_instance
            contacto_cuenta.objects.create(**contacto_data)
        
        # Crear direcciones
        for direccion_data in direcciones_data:
            direccion_data['cuenta_id'] = cuenta_instance
            direccion.objects.create(**direccion_data)
        
        return cuenta_instance
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Actualizar cuenta con manejo de relaciones anidadas."""
        contactos_data = validated_data.pop('contactos_data', None)
        direcciones_data = validated_data.pop('direcciones_data', None)
        
        # Actualizar campos de la cuenta
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Manejar contactos si se proporcionan
        if contactos_data is not None:
            # Por simplicidad, eliminar contactos existentes y crear nuevos
            # En producción, considerar un PATCH más sofisticado
            instance.contactos.all().delete()
            for contacto_data in contactos_data:
                contacto_data['cuenta_id'] = instance
                contacto_cuenta.objects.create(**contacto_data)
        
        # Manejar direcciones si se proporcionan
        if direcciones_data is not None:
            instance.direcciones.all().delete()
            for direccion_data in direcciones_data:
                direccion_data['cuenta_id'] = instance
                direccion.objects.create(**direccion_data)
        
        return instance