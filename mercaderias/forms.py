from django import forms
from .models import Grano

class GranoForm(forms.ModelForm):
    """Formulario para crear y editar granos"""
    
    class Meta:
        model = Grano
        fields = ['nombre', 'codigo', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Trigo Pan',
                'maxlength': 100
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: TRIG',
                'maxlength': 10,
                'style': 'text-transform: uppercase;'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional del grano...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos requeridos
        self.fields['nombre'].required = True
        self.fields['codigo'].required = True
        
        # Establecer valores por defecto
        if not self.instance.pk:  # Solo para nuevos granos
            self.fields['activo'].initial = True
    
    def clean_codigo(self):
        """Validar que el código sea único y esté en mayúsculas"""
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            codigo = codigo.upper()
            
            # Verificar unicidad
            if self.instance.pk:
                # Editando grano existente
                if Grano.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Ya existe un grano con este código.")
            else:
                # Creando nuevo grano
                if Grano.objects.filter(codigo=codigo).exists():
                    raise forms.ValidationError("Ya existe un grano con este código.")
        
        return codigo
    
    def clean_nombre(self):
        """Validar que el nombre sea único"""
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Verificar unicidad
            if self.instance.pk:
                # Editando grano existente
                if Grano.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Ya existe un grano con este nombre.")
            else:
                # Creando nuevo grano
                if Grano.objects.filter(nombre__iexact=nombre).exists():
                    raise forms.ValidationError("Ya existe un grano con este nombre.")
        
        return nombre