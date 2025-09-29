from django import forms
from django.contrib.auth.models import User
from .models import Ubicacion, TipoUbicacion, Almacenaje, TipoAlmacenaje, EstadoAlmacenaje, Stock

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


class StockForm(forms.ModelForm):
    """Formulario para ingresar stock en almacenajes"""
    
    class Meta:
        model = Stock
        fields = ['ubicacion', 'almacenaje', 'mercaderia', 'cantidad_kg']
        widgets = {
            'ubicacion': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_ubicacion_stock'
            }),
            'almacenaje': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_almacenaje_stock'
            }),
            'mercaderia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cantidad_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cantidad en kilogramos',
                'min': '0.1',
                'step': '0.1'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar ubicaciones activas
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activo=True).order_by('nombre')
        
        # Si hay datos (POST o initial), configurar almacenajes apropiadamente
        if args and args[0]:  # hay datos POST
            ubicacion_id = args[0].get('ubicacion')
            if ubicacion_id:
                self.fields['almacenaje'].queryset = Almacenaje.objects.filter(
                    ubicacion_id=ubicacion_id, activo=True
                ).order_by('codigo')
            else:
                self.fields['almacenaje'].queryset = Almacenaje.objects.none()
        else:
            # Inicialmente no mostrar almacenajes hasta que se seleccione una ubicación
            self.fields['almacenaje'].queryset = Almacenaje.objects.none()
        
        # Importar y filtrar mercaderías disponibles
        try:
            from mercaderias.models import Mercaderia
            self.fields['mercaderia'].queryset = Mercaderia.objects.select_related('grano').order_by('grano__nombre')
        except ImportError:
            # Si no existe el modelo Mercaderia, crear un queryset vacío
            self.fields['mercaderia'].queryset = Stock.objects.none()
        
        # Hacer campos requeridos
        self.fields['ubicacion'].required = True
        self.fields['almacenaje'].required = True
        self.fields['mercaderia'].required = True
        self.fields['cantidad_kg'].required = True
        
        # Labels personalizados
        self.fields['ubicacion'].label = 'Ubicación'
        self.fields['almacenaje'].label = 'Almacenaje'
        self.fields['mercaderia'].label = 'Mercadería'
        self.fields['cantidad_kg'].label = 'Cantidad (kg)'
        
        # Help texts
        self.fields['cantidad_kg'].help_text = 'Cantidad a ingresar en kilogramos'
        self.fields['almacenaje'].help_text = 'Seleccione primero la ubicación para filtrar almacenajes'
    
    def clean(self):
        cleaned_data = super().clean()
        ubicacion = cleaned_data.get('ubicacion')
        almacenaje = cleaned_data.get('almacenaje')
        cantidad_kg = cleaned_data.get('cantidad_kg')
        
        # Validar que el almacenaje pertenezca a la ubicación seleccionada
        if ubicacion and almacenaje:
            if almacenaje.ubicacion != ubicacion:
                raise forms.ValidationError("El almacenaje seleccionado no pertenece a la ubicación elegida.")
        
        # Validar que el almacenaje esté activo y disponible
        if almacenaje:
            if not almacenaje.activo:
                raise forms.ValidationError("El almacenaje seleccionado no está activo.")
            
            # Verificar capacidad si está definida
            if almacenaje.capacidad_kg and cantidad_kg:
                from django.db.models import Sum
                stock_actual = Stock.objects.filter(almacenaje=almacenaje).aggregate(
                    total=Sum('cantidad_kg')
                )['total'] or 0
                
                if (stock_actual + cantidad_kg) > almacenaje.capacidad_kg:
                    capacidad_disponible = almacenaje.capacidad_kg - stock_actual
                    raise forms.ValidationError(
                        f"La cantidad excede la capacidad disponible del almacenaje. "
                        f"Capacidad disponible: {capacidad_disponible:.1f} kg"
                    )
        
        return cleaned_data