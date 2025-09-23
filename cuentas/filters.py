"""
Filtros personalizados para el módulo de cuentas.
Incluye filtros complejos y de búsqueda avanzada.
"""
import django_filters
from django.db.models import Q
from .models import cuenta, contacto_cuenta, direccion


class CuentaFilter(django_filters.FilterSet):
    """Filtro avanzado para cuentas con búsqueda inteligente."""
    
    # Filtros de texto con búsqueda parcial
    razon_social = django_filters.CharFilter(
        field_name='razon_social', 
        lookup_expr='icontains',
        help_text="Búsqueda parcial en razón social"
    )
    
    nombre_fantasia = django_filters.CharFilter(
        field_name='nombre_fantasia', 
        lookup_expr='icontains',
        help_text="Búsqueda parcial en nombre de fantasía"
    )
    
    numero_documento = django_filters.CharFilter(
        field_name='numero_documento', 
        lookup_expr='icontains',
        help_text="Búsqueda parcial en número de documento"
    )
    
    # Filtros de selección múltiple
    tipo_cuenta = django_filters.ModelMultipleChoiceFilter(
        field_name='tipo_cuenta_id_tipo_cuenta',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por uno o más tipos de cuenta"
    )
    
    situacion_iva = django_filters.ModelMultipleChoiceFilter(
        field_name='situacionIva_idsituacionIva',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por situaciones de IVA"
    )
    
    tipo_documento = django_filters.ModelMultipleChoiceFilter(
        field_name='tipo_documento_idtipo_documento',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por tipos de documento"
    )
    
    # Filtros geográficos
    provincia = django_filters.ModelChoiceFilter(
        field_name='provincia_idprovincia',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por provincia"
    )
    
    localidad = django_filters.ModelChoiceFilter(
        field_name='localidad_idlocalidad',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por localidad"
    )
    
    # Filtros de estado
    activo = django_filters.BooleanFilter(
        help_text="Filtrar por estado activo/inactivo"
    )
    
    # Filtros de fecha
    fecha_alta_desde = django_filters.DateFilter(
        field_name='fecha_alta',
        lookup_expr='gte',
        help_text="Cuentas creadas desde esta fecha"
    )
    
    fecha_alta_hasta = django_filters.DateFilter(
        field_name='fecha_alta',
        lookup_expr='lte',
        help_text="Cuentas creadas hasta esta fecha"
    )
    
    # Búsqueda global inteligente
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Búsqueda global en múltiples campos"
    )
    
    # Filtros de existencia de relaciones
    tiene_contactos = django_filters.BooleanFilter(
        method='filter_tiene_contactos',
        help_text="Filtrar cuentas que tienen contactos"
    )
    
    tiene_direcciones = django_filters.BooleanFilter(
        method='filter_tiene_direcciones',
        help_text="Filtrar cuentas que tienen direcciones adicionales"
    )
    
    class Meta:
        model = cuenta
        fields = []  # Definimos campos personalizados arriba
    
    def __init__(self, *args, **kwargs):
        """Inicializar querysets dinámicos."""
        super().__init__(*args, **kwargs)
        
        # Importar modelos aquí para evitar circular imports
        from .models import tipo_cuenta, situacionIva, tipo_documento, provincia, localidad
        
        # Configurar querysets
        self.filters['tipo_cuenta'].queryset = tipo_cuenta.objects.all()
        self.filters['situacion_iva'].queryset = situacionIva.objects.all()
        self.filters['tipo_documento'].queryset = tipo_documento.objects.all()
        self.filters['provincia'].queryset = provincia.objects.all().order_by('nombre_provincia')
        self.filters['localidad'].queryset = localidad.objects.all().order_by('nombre_localidad')
    
    def filter_search(self, queryset, name, value):
        """Búsqueda global inteligente en múltiples campos."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(razon_social__icontains=value) |
            Q(nombre_fantasia__icontains=value) |
            Q(numero_documento__icontains=value) |
            Q(email_cuenta__icontains=value) |
            Q(telefono_cuenta__icontains=value) |
            Q(celular_cuenta__icontains=value) |
            Q(direccion_cuenta__icontains=value) |
            Q(contactos__nombre__icontains=value) |
            Q(contactos__email__icontains=value)
        ).distinct()
    
    def filter_tiene_contactos(self, queryset, name, value):
        """Filtrar por existencia de contactos."""
        if value is True:
            return queryset.filter(contactos__isnull=False).distinct()
        elif value is False:
            return queryset.filter(contactos__isnull=True)
        return queryset
    
    def filter_tiene_direcciones(self, queryset, name, value):
        """Filtrar por existencia de direcciones adicionales."""
        if value is True:
            return queryset.filter(direcciones__isnull=False).distinct()
        elif value is False:
            return queryset.filter(direcciones__isnull=True)
        return queryset


class ContactoCuentaFilter(django_filters.FilterSet):
    """Filtro para contactos de cuenta."""
    
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains',
        help_text="Búsqueda parcial en nombre del contacto"
    )
    
    cargo = django_filters.CharFilter(
        field_name='cargo',
        lookup_expr='icontains',
        help_text="Búsqueda parcial en cargo"
    )
    
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        help_text="Búsqueda parcial en email"
    )
    
    telefono = django_filters.CharFilter(
        field_name='telefono',
        lookup_expr='icontains',
        help_text="Búsqueda parcial en teléfono"
    )
    
    activo = django_filters.BooleanFilter(
        help_text="Filtrar por estado activo/inactivo"
    )
    
    cuenta = django_filters.ModelChoiceFilter(
        field_name='cuenta_id',
        queryset=cuenta.objects.filter(activo=True),
        help_text="Filtrar por cuenta"
    )
    
    class Meta:
        model = contacto_cuenta
        fields = []


class DireccionFilter(django_filters.FilterSet):
    """Filtro para direcciones."""
    
    etiqueta = django_filters.CharFilter(
        field_name='etiqueta',
        lookup_expr='icontains',
        help_text="Búsqueda parcial en etiqueta"
    )
    
    calle = django_filters.CharFilter(
        field_name='calle',
        lookup_expr='icontains',
        help_text="Búsqueda parcial en calle"
    )
    
    provincia = django_filters.ModelChoiceFilter(
        field_name='provincia_idprovincia',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por provincia"
    )
    
    localidad = django_filters.ModelChoiceFilter(
        field_name='localidad_idlocalidad',
        queryset=None,  # Se configura en __init__
        help_text="Filtrar por localidad"
    )
    
    es_principal = django_filters.BooleanFilter(
        help_text="Filtrar direcciones principales"
    )
    
    cuenta = django_filters.ModelChoiceFilter(
        field_name='cuenta_id',
        queryset=cuenta.objects.filter(activo=True),
        help_text="Filtrar por cuenta"
    )
    
    class Meta:
        model = direccion
        fields = []
    
    def __init__(self, *args, **kwargs):
        """Inicializar querysets dinámicos."""
        super().__init__(*args, **kwargs)
        
        from .models import provincia, localidad
        
        self.filters['provincia'].queryset = provincia.objects.all().order_by('nombre_provincia')
        self.filters['localidad'].queryset = localidad.objects.all().order_by('nombre_localidad')