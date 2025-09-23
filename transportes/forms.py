"""
Formularios para el módulo de transportes.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta

from .models import TipoCamion, Camion, Chofer, Viaje, TicketBalanza
from cuentas.models import cuenta


class TipoCamionForm(forms.ModelForm):
    """Formulario para tipos de camión."""
    
    class Meta:
        model = TipoCamion
        fields = ['nombre', 'descripcion', 'capacidad_maxima', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Camión Grande'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de camión'
            }),
            'capacidad_maxima': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Capacidad en toneladas'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CamionForm(forms.ModelForm):
    """Formulario simplificado para camiones."""
    
    class Meta:
        model = Camion
        fields = [
            'patente', 'acoplado_1', 'acoplado_2',
            'capacidad_carga', 'tara', 'cuenta_asociada',
            'fecha_vencimiento_vtv', 'fecha_vencimiento_seguro',
            'numero_poliza', 'observaciones', 'activo'
        ]
        widgets = {
            'patente': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'placeholder': 'ABC123'
            }),
            'acoplado_1': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'placeholder': 'Patente del primer acoplado (opcional)'
            }),
            'acoplado_2': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'placeholder': 'Patente del segundo acoplado (opcional)'
            }),
            'capacidad_carga': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Capacidad en toneladas (opcional)'
            }),
            'tara': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Tara en toneladas (opcional)'
            }),
            'cuenta_asociada': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_vencimiento_vtv': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_vencimiento_seguro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_poliza': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de póliza (opcional)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cuenta_asociada'].queryset = cuenta.objects.filter(activo=True)
        self.fields['cuenta_asociada'].empty_label = "Seleccionar cuenta/empresa"
    
    def clean_patente(self):
        patente = self.cleaned_data['patente'].upper()
        if len(patente) < 6:
            raise ValidationError('La patente debe tener al menos 6 caracteres.')
        return patente
    
    def clean_acoplado_1(self):
        acoplado = self.cleaned_data.get('acoplado_1', '')
        if acoplado:
            acoplado = acoplado.upper()
            if len(acoplado) < 6:
                raise ValidationError('La patente del acoplado debe tener al menos 6 caracteres.')
        return acoplado
    
    def clean_acoplado_2(self):
        acoplado = self.cleaned_data.get('acoplado_2', '')
        if acoplado:
            acoplado = acoplado.upper()
            if len(acoplado) < 6:
                raise ValidationError('La patente del acoplado debe tener al menos 6 caracteres.')
        return acoplado


class ChoferForm(forms.ModelForm):
    """Formulario para choferes."""
    
    class Meta:
        model = Chofer
        fields = [
            'nombre', 'apellido', 'dni', 'fecha_nacimiento',
            'telefono', 'email', 'direccion', 'legajo',
            'fecha_ingreso', 'tipo_licencia', 'numero_licencia',
            'fecha_vencimiento_licencia', 'estado', 'camion_asignado',
            'contacto_emergencia_nombre', 'contacto_emergencia_telefono',
            'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del chofer'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del chofer'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+54 9 11 1234-5678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
            'legajo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de legajo'
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tipo_licencia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_licencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de licencia'
            }),
            'fecha_vencimiento_licencia': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'camion_asignado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contacto_emergencia_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto de emergencia'
            }),
            'contacto_emergencia_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de emergencia'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['camion_asignado'].queryset = Camion.objects.filter(activo=True)
        self.fields['camion_asignado'].empty_label = "Sin camión asignado"
    
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if not dni.isdigit():
            raise ValidationError('El DNI debe contener solo números.')
        if len(dni) < 7 or len(dni) > 8:
            raise ValidationError('El DNI debe tener 7 u 8 dígitos.')
        return dni
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        edad = (date.today() - fecha_nacimiento).days // 365
        if edad < 18:
            raise ValidationError('El chofer debe ser mayor de edad.')
        if edad > 70:
            raise ValidationError('El chofer no puede tener más de 70 años.')
        return fecha_nacimiento
    
    def clean_fecha_vencimiento_licencia(self):
        fecha_vencimiento = self.cleaned_data['fecha_vencimiento_licencia']
        if fecha_vencimiento < date.today():
            raise ValidationError('La licencia no puede estar vencida.')
        return fecha_vencimiento


class ViajeForm(forms.ModelForm):
    """Formulario para viajes."""
    
    class Meta:
        model = Viaje
        fields = [
            'numero_viaje', 'fecha_programada', 'camion', 'chofer',
            'origen', 'destino', 'distancia_km', 'tipo_carga',
            'descripcion_carga', 'peso_estimado', 'cliente',
            'precio_acordado', 'observaciones'
        ]
        widgets = {
            'numero_viaje': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número único del viaje'
            }),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'camion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chofer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'origen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Punto de origen'
            }),
            'destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Punto de destino'
            }),
            'distancia_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Distancia en kilómetros'
            }),
            'tipo_carga': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion_carga': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la carga'
            }),
            'peso_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Peso estimado en toneladas'
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio_acordado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Precio acordado'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del viaje'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['camion'].queryset = Camion.objects.filter(
            estado='disponible', 
            activo=True
        )
        self.fields['chofer'].queryset = Chofer.objects.filter(
            estado='disponible', 
            activo=True
        )
        self.fields['cliente'].queryset = cuenta.objects.filter(activo=True)
    
    def clean_fecha_programada(self):
        fecha_programada = self.cleaned_data['fecha_programada']
        if fecha_programada < timezone.now():
            raise ValidationError('La fecha programada no puede ser en el pasado.')
        return fecha_programada


class TicketBalanzaForm(forms.ModelForm):
    """Formulario para tickets de balanza."""
    
    class Meta:
        model = TicketBalanza
        fields = [
            'numero_ticket', 'fecha_pesaje', 'tipo_pesaje',
            'camion', 'chofer', 'viaje', 'peso_bruto', 'peso_tara',
            'producto', 'cliente_carga', 'destino_carga',
            'balanza_operador', 'observaciones'
        ]
        widgets = {
            'numero_ticket': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número único del ticket'
            }),
            'fecha_pesaje': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo_pesaje': forms.Select(attrs={
                'class': 'form-select'
            }),
            'camion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chofer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'viaje': forms.Select(attrs={
                'class': 'form-select'
            }),
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
            'producto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de producto'
            }),
            'cliente_carga': forms.Select(attrs={
                'class': 'form-select'
            }),
            'destino_carga': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Destino de la carga'
            }),
            'balanza_operador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del operador de balanza'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del pesaje'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['camion'].queryset = Camion.objects.filter(activo=True)
        self.fields['chofer'].queryset = Chofer.objects.filter(activo=True)
        self.fields['viaje'].queryset = Viaje.objects.filter(
            estado__in=['planificado', 'en_curso']
        )
        self.fields['viaje'].empty_label = "Sin viaje asociado"
        self.fields['cliente_carga'].queryset = cuenta.objects.filter(activo=True)
    
    def clean_peso_bruto(self):
        peso_bruto = self.cleaned_data['peso_bruto']
        if peso_bruto <= 0:
            raise ValidationError('El peso bruto debe ser mayor a cero.')
        return peso_bruto
    
    def clean_peso_tara(self):
        peso_tara = self.cleaned_data['peso_tara']
        if peso_tara < 0:
            raise ValidationError('El peso tara no puede ser negativo.')
        return peso_tara
    
    def clean(self):
        cleaned_data = super().clean()
        peso_bruto = cleaned_data.get('peso_bruto')
        peso_tara = cleaned_data.get('peso_tara')
        
        if peso_bruto and peso_tara and peso_tara >= peso_bruto:
            raise ValidationError('El peso tara debe ser menor al peso bruto.')
        
        return cleaned_data


# === FORMULARIOS DE BÚSQUEDA ===

class BusquedaCamionForm(forms.Form):
    """Formulario de búsqueda simplificado para camiones."""
    
    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por patente, chasis o acoplados...'
        })
    )
    
    cuenta_asociada = forms.ModelChoiceField(
        queryset=cuenta.objects.filter(activo=True),
        required=False,
        empty_label="Todas las cuentas",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class BusquedaChoferForm(forms.Form):
    """Formulario de búsqueda para choferes."""
    
    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido, DNI o legajo...'
        })
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Chofer.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tipo_licencia = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Chofer.TIPO_LICENCIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )