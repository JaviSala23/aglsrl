"""
Formularios para el sistema de tickets de transporte.
"""
from django import forms
from django.forms import inlineformset_factory
from .models import Ticket, DetalleMercaderia, AnalisisMercaderia, TipoMovimiento, EstadoTicket
from transportes.models import Chofer
from cuentas.models import cuenta
from mercaderias.models import Mercaderia, ClasificacionCalidad
from almacenamiento.models import Almacenaje


class TicketForm(forms.ModelForm):
    """Formulario principal para crear/editar tickets."""
    
    # Campo explícito para tipo de movimiento
    tipo_movimiento = forms.ModelChoiceField(
        queryset=TipoMovimiento.objects.filter(activo=True),
        empty_label="-- Seleccionar Tipo de Movimiento --",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        required=True
    )
    
    class Meta:
        model = Ticket
        fields = [
            'tipo_movimiento', 'patente_camion', 'chofer', 'cuenta_transporte',
            'origen', 'destinatario', 'fecha_llegada', 'peso_bruto', 'peso_tara',
            'observaciones'
        ]
        widgets = {
            'patente_camion': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'placeholder': 'ABC123 (Obligatorio)',
                'required': True,
                'style': 'text-transform: uppercase;'
            }),
            'chofer': forms.Select(attrs={'class': 'form-select'}),
            'cuenta_transporte': forms.Select(attrs={'class': 'form-select'}),
            'origen': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.Select(attrs={'class': 'form-select'}),
            'fecha_llegada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'peso_bruto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 kg'
            }),
            'peso_tara': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 kg'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales del ticket...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el formato de fecha para HTML5 datetime-local
        self.fields['fecha_llegada'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
        
        # El campo tipo_movimiento ya está configurado como ModelChoiceField explícito
        # pero lo reforzamos aquí por seguridad
        self.fields['tipo_movimiento'].queryset = TipoMovimiento.objects.filter(activo=True)
        self.fields['tipo_movimiento'].empty_label = "-- Seleccionar Tipo de Movimiento --"
        
        # Configurar querysets para los campos relacionados
        try:
            self.fields['chofer'].queryset = Chofer.objects.filter(activo=True)
        except:
            self.fields['chofer'].queryset = Chofer.objects.all()
        self.fields['chofer'].empty_label = "-- Seleccionar Chofer (Opcional) --"
        
        # Filtrar cuentas por tipo si es necesario
        try:
            cuentas_activas = cuenta.objects.filter(activo=True)
        except:
            cuentas_activas = cuenta.objects.all()
            
        self.fields['cuenta_transporte'].queryset = cuentas_activas
        self.fields['cuenta_transporte'].empty_label = "-- Seleccionar Empresa Transporte (Opcional) --"
        self.fields['origen'].queryset = cuentas_activas
        self.fields['origen'].empty_label = "-- Seleccionar Origen --"
        self.fields['destinatario'].queryset = cuentas_activas
        self.fields['destinatario'].empty_label = "-- Seleccionar Destinatario --"
        
        # Configurar campos obligatorios
        self.fields['patente_camion'].required = True
        self.fields['tipo_movimiento'].required = True
        
        # Hacer campos condicionales según el tipo de movimiento
        self.fields['origen'].required = False
        self.fields['destinatario'].required = False
    
    def clean_patente_camion(self):
        """Validar y formatear patente."""
        patente = self.cleaned_data['patente_camion'].upper().replace(' ', '')
        return patente
    
    def clean(self):
        """Validación cruzada del formulario."""
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        origen = cleaned_data.get('origen')
        destinatario = cleaned_data.get('destinatario')
        peso_bruto = cleaned_data.get('peso_bruto')
        peso_tara = cleaned_data.get('peso_tara')
        
        # Validar origen/destinatario según tipo de movimiento
        if tipo_movimiento:
            if tipo_movimiento.requiere_origen and not origen:
                raise forms.ValidationError('Este tipo de movimiento requiere especificar un origen.')
            
            if tipo_movimiento.requiere_destinatario and not destinatario:
                raise forms.ValidationError('Este tipo de movimiento requiere especificar un destinatario.')
        
        # Validar pesos si ambos están presentes
        if peso_bruto and peso_tara:
            if peso_bruto <= peso_tara:
                raise forms.ValidationError('El peso bruto debe ser mayor al peso tara.')
        
        return cleaned_data


class DetalleMercaderiaForm(forms.ModelForm):
    """Formulario para detalle de mercaderías en un ticket."""
    
    class Meta:
        model = DetalleMercaderia
        fields = [
            'mercaderia', 'cantidad_kg', 'calidad_clasificacion', 
            'ubicacion_almacenaje', 'observaciones'
        ]
        widgets = {
            'mercaderia': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'calidad_clasificacion': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion_almacenaje': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones específicas...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar querysets
        try:
            self.fields['mercaderia'].queryset = Mercaderia.objects.filter(activo=True)
        except:
            self.fields['mercaderia'].queryset = Mercaderia.objects.all()
        self.fields['mercaderia'].empty_label = "-- Seleccionar Mercadería --"
        
        try:
            self.fields['calidad_clasificacion'].queryset = ClasificacionCalidad.objects.filter(activo=True)
        except:
            self.fields['calidad_clasificacion'].queryset = ClasificacionCalidad.objects.all()
        self.fields['calidad_clasificacion'].empty_label = "-- Sin Clasificar (Se hará en análisis) --"
        
        try:
            self.fields['ubicacion_almacenaje'].queryset = Almacenaje.objects.filter(activo=True)
        except:
            self.fields['ubicacion_almacenaje'].queryset = Almacenaje.objects.all()
        self.fields['ubicacion_almacenaje'].empty_label = "-- Seleccionar Ubicación --"
        
        # Campos obligatorios
        self.fields['mercaderia'].required = True
        self.fields['cantidad_kg'].required = True


# FormSet para manejar múltiples mercaderías por ticket
DetalleMercaderiaFormSet = inlineformset_factory(
    Ticket,
    DetalleMercaderia,
    form=DetalleMercaderiaForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    max_num=10,  # Máximo 10 mercaderías por ticket
)


class AnalisisForm(forms.ModelForm):
    """Formulario para registrar análisis de mercadería."""
    
    class Meta:
        model = AnalisisMercaderia
        fields = [
            'humedad', 'proteina', 'grasa', 'parametros_adicionales',
            'observaciones_analisis', 'aprobado'
        ]
        widgets = {
            'humedad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'proteina': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'grasa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'parametros_adicionales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Otros parámetros en formato JSON...'
            }),
            'observaciones_analisis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones del análisis...'
            }),
            'aprobado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PesosForm(forms.ModelForm):
    """Formulario simple para actualizar pesos."""
    
    class Meta:
        model = Ticket
        fields = ['peso_bruto', 'peso_tara']
        widgets = {
            'peso_bruto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Peso bruto en kg'
            }),
            'peso_tara': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Peso tara en kg'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        peso_bruto = cleaned_data.get('peso_bruto')
        peso_tara = cleaned_data.get('peso_tara')
        
        if peso_bruto and peso_tara and peso_bruto <= peso_tara:
            raise forms.ValidationError('El peso bruto debe ser mayor al peso tara.')
        
        return cleaned_data


class FiltroTicketsForm(forms.Form):
    """Formulario para filtrar tickets en la lista."""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número, patente, chofer...'
        })
    )
    
    tipo = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todos los estados",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import TipoMovimiento, EstadoTicket
        
        try:
            self.fields['tipo'].queryset = TipoMovimiento.objects.filter(activo=True)
        except:
            self.fields['tipo'].queryset = TipoMovimiento.objects.all()
            
        try:
            self.fields['estado'].queryset = EstadoTicket.objects.filter(activo=True)
        except:
            self.fields['estado'].queryset = EstadoTicket.objects.all()