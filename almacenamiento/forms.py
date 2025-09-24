from django import forms
from django.contrib.auth.models import User
from .models import Ubicacion, TipoUbicacion, Almacenaje, TipoAlmacenaje, EstadoAlmacenaje

class UbicacionForm(forms.ModelForm):
    """Formulario para crear y editar ubicaciones"""
    
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'tipo', 'encargado', 'direccion', 'latitud', 'longitud', 'observaciones', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Planta Central, Campo Norte',
                'maxlength': 100
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'encargado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa de la ubicación...'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -34.6037',
                'step': '0.0000001'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -58.3816',
                'step': '0.0000001'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos requeridos
        self.fields['nombre'].required = True
        self.fields['tipo'].required = True
        
        # Configurar queryset para usuarios
        self.fields['encargado'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
        self.fields['encargado'].empty_label = "Seleccionar encargado (opcional)"
        
        # Establecer valores por defecto
        if not self.instance.pk:  # Solo para nuevas ubicaciones
            self.fields['activo'].initial = True
    
    def clean_nombre(self):
        """Validar que el nombre sea único"""
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Verificar unicidad
            if self.instance.pk:
                # Editando ubicación existente
                if Ubicacion.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Ya existe una ubicación con este nombre.")
            else:
                # Creando nueva ubicación
                if Ubicacion.objects.filter(nombre__iexact=nombre).exists():
                    raise forms.ValidationError("Ya existe una ubicación con este nombre.")
        
        return nombre
    
    def clean_latitud(self):
        """Validar rango de latitud"""
        latitud = self.cleaned_data.get('latitud')
        if latitud is not None:
            if not (-90 <= latitud <= 90):
                raise forms.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return latitud
    
    def clean_longitud(self):
        """Validar rango de longitud"""
        longitud = self.cleaned_data.get('longitud')
        if longitud is not None:
            if not (-180 <= longitud <= 180):
                raise forms.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return longitud
    
    def clean(self):
        """Validaciones cruzadas"""
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')
        
        # Si se proporciona una coordenada, se debe proporcionar la otra
        if (latitud is not None and longitud is None) or (latitud is None and longitud is not None):
            raise forms.ValidationError("Si proporciona coordenadas GPS, debe incluir tanto latitud como longitud.")
        
        return cleaned_data


class AlmacenajeForm(forms.ModelForm):
    """Formulario para crear y editar almacenajes"""
    
    class Meta:
        model = Almacenaje
        fields = ['ubicacion', 'tipo', 'codigo', 'capacidad_kg', 'estado', 'latitud', 'longitud', 
                 'longitud_metros', 'sentido', 'observaciones', 'activo']
        widgets = {
            'ubicacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: S-01, GB-A12, SB-001',
                'maxlength': 50
            }),
            'capacidad_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Capacidad en kilogramos',
                'step': '0.01',
                'min': '0.01'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -34.6037',
                'step': '0.0000001'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -58.3816',
                'step': '0.0000001'
            }),
            'longitud_metros': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitud en metros (para silo bolsa)',
                'step': '0.01',
                'min': '0'
            }),
            'sentido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Norte-Sur, Este-Oeste',
                'maxlength': 50
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos requeridos
        self.fields['ubicacion'].required = True
        self.fields['tipo'].required = True
        self.fields['codigo'].required = True
        
        # Configurar queryset para ubicaciones activas
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activo=True).order_by('nombre')
        self.fields['ubicacion'].empty_label = "Seleccionar ubicación"
        
        # Establecer valores por defecto
        if not self.instance.pk:  # Solo para nuevos almacenajes
            self.fields['activo'].initial = True
            self.fields['estado'].initial = EstadoAlmacenaje.DISPONIBLE
    
    def clean_codigo(self):
        """Validar que el código sea único dentro de la ubicación"""
        codigo = self.cleaned_data.get('codigo')
        ubicacion = self.cleaned_data.get('ubicacion')
        
        if codigo and ubicacion:
            # Verificar unicidad dentro de la ubicación
            if self.instance.pk:
                # Editando almacenaje existente
                if Almacenaje.objects.filter(
                    ubicacion=ubicacion, 
                    codigo__iexact=codigo
                ).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError(f"Ya existe un almacenaje con código '{codigo}' en esta ubicación.")
            else:
                # Creando nuevo almacenaje
                if Almacenaje.objects.filter(ubicacion=ubicacion, codigo__iexact=codigo).exists():
                    raise forms.ValidationError(f"Ya existe un almacenaje con código '{codigo}' en esta ubicación.")
        
        return codigo
    
    def clean_capacidad_kg(self):
        """Validar capacidad"""
        capacidad = self.cleaned_data.get('capacidad_kg')
        if capacidad is not None and capacidad <= 0:
            raise forms.ValidationError("La capacidad debe ser mayor a 0.")
        return capacidad
    
    def clean_longitud_metros(self):
        """Validar longitud en metros"""
        longitud_metros = self.cleaned_data.get('longitud_metros')
        if longitud_metros is not None and longitud_metros <= 0:
            raise forms.ValidationError("La longitud debe ser mayor a 0.")
        return longitud_metros
    
    def clean_latitud(self):
        """Validar rango de latitud"""
        latitud = self.cleaned_data.get('latitud')
        if latitud is not None:
            if not (-90 <= latitud <= 90):
                raise forms.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return latitud
    
    def clean_longitud(self):
        """Validar rango de longitud"""
        longitud = self.cleaned_data.get('longitud')
        if longitud is not None:
            if not (-180 <= longitud <= 180):
                raise forms.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return longitud
    
    def clean(self):
        """Validaciones cruzadas"""
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')
        tipo = cleaned_data.get('tipo')
        longitud_metros = cleaned_data.get('longitud_metros')
        sentido = cleaned_data.get('sentido')
        
        # Si se proporciona una coordenada GPS, se debe proporcionar la otra
        if (latitud is not None and longitud is None) or (latitud is None and longitud is not None):
            raise forms.ValidationError("Si proporciona coordenadas GPS, debe incluir tanto latitud como longitud.")
        
        # Validaciones específicas para silo bolsa
        if tipo == TipoAlmacenaje.SILO_BOLSA:
            if not longitud_metros:
                raise forms.ValidationError("La longitud en metros es requerida para silo bolsa.")
            if not sentido:
                raise forms.ValidationError("El sentido de orientación es requerido para silo bolsa.")
        
        return cleaned_data