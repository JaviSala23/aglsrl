"""
Formularios para el módulo de agenda.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Contacto, TipoContacto, Evento, TipoEvento, Tarea
from cuentas.models import cuenta


class ContactoForm(forms.ModelForm):
    """Formulario para crear y editar contactos."""
    
    class Meta:
        model = Contacto
        fields = [
            'nombre', 'apellido', 'empresa', 'cargo',
            'telefono_principal', 'telefono_secundario',
            'email_principal', 'email_secundario',
            'direccion', 'ciudad', 'provincia', 'codigo_postal', 'pais',
            'tipo_contacto', 'cuenta_relacionada',
            'notas', 'sitio_web', 'favorito'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del contacto'
            }),
            'empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa (opcional)',
                'readonly': True,
                'style': 'background-color: #f8f9fa;'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo o posición'
            }),
            'telefono_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+54 9 XXX XXX-XXXX',
                'type': 'tel'
            }),
            'telefono_secundario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+54 9 XXX XXX-XXXX (opcional)',
                'type': 'tel'
            }),
            'email_principal': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@ejemplo.com'
            }),
            'email_secundario': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email2@ejemplo.com (opcional)'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa',
                'rows': 2
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código Postal'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'tipo_contacto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cuenta_relacionada': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_cuenta_relacionada'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales sobre el contacto',
                'rows': 3
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com'
            }),
            'favorito': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre *',
            'apellido': 'Apellido',
            'empresa': 'Empresa',
            'cargo': 'Cargo',
            'telefono_principal': 'Teléfono Principal',
            'telefono_secundario': 'Teléfono Secundario',
            'email_principal': 'Email Principal',
            'email_secundario': 'Email Secundario',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'provincia': 'Provincia',
            'codigo_postal': 'Código Postal',
            'pais': 'País',
            'tipo_contacto': 'Tipo de Contacto *',
            'cuenta_relacionada': 'Cuenta Relacionada',
            'notas': 'Notas',
            'sitio_web': 'Sitio Web',
            'favorito': 'Marcar como Favorito'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo cuentas activas para el selector
        cuentas_activas = cuenta.objects.filter(activo=True).order_by('razon_social')
        self.fields['cuenta_relacionada'].queryset = cuentas_activas
        self.fields['cuenta_relacionada'].empty_label = "Seleccione una cuenta (opcional)"
        
        # Personalizar las opciones para mostrar nombre más amigable
        choices = [(None, "Seleccione una cuenta (opcional)")]
        for cuenta_obj in cuentas_activas:
            # Mostrar nombre_fantasia si existe, sino razon_social
            nombre_display = cuenta_obj.nombre_fantasia or cuenta_obj.razon_social
            choices.append((cuenta_obj.id_cuenta, f"{nombre_display} - {cuenta_obj.numero_documento}"))
        
        self.fields['cuenta_relacionada'].choices = choices
        
        # Filtrar solo tipos de contacto activos
        self.fields['tipo_contacto'].queryset = TipoContacto.objects.filter(activo=True).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        cuenta_relacionada = cleaned_data.get('cuenta_relacionada')
        empresa = cleaned_data.get('empresa')
        
        # Si se selecciona una cuenta relacionada, actualizar el campo empresa automáticamente
        if cuenta_relacionada:
            # Usar nombre_fantasia si existe, sino razon_social
            nombre_empresa = cuenta_relacionada.nombre_fantasia or cuenta_relacionada.razon_social
            cleaned_data['empresa'] = nombre_empresa
        
        return cleaned_data


class EventoForm(forms.ModelForm):
    """Formulario para crear y editar eventos."""
    
    class Meta:
        model = Evento
        fields = [
            'titulo', 'descripcion', 'tipo_evento',
            'fecha_inicio', 'fecha_fin', 'todo_el_dia', 
            'ubicacion', 'ubicacion_virtual', 'contactos',
            'minutos_recordatorio', 'recordatorio_activo', 
            'prioridad', 'estado'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del evento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del evento',
                'rows': 3
            }),
            'tipo_evento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'todo_el_dia': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación del evento'
            }),
            'ubicacion_virtual': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/...'
            }),
            'contactos': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4'
            }),
            'minutos_recordatorio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '5'
            }),
            'recordatorio_activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar contactos activos del usuario
        if user:
            self.fields['contactos'].queryset = Contacto.objects.filter(
                activo=True, 
                creado_por=user
            ).order_by('apellido', 'nombre')
        
        # Filtrar tipos de evento activos
        self.fields['tipo_evento'].queryset = TipoEvento.objects.filter(activo=True).order_by('nombre')


class TareaForm(forms.ModelForm):
    """Formulario para crear y editar tareas."""
    
    # Campo personalizado para múltiples usuarios
    usuarios_asignados = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label='Asignar a usuarios',
        help_text='Selecciona uno o varios usuarios para trabajar en esta tarea'
    )
    
    class Meta:
        model = Tarea
        fields = [
            'titulo', 'descripcion', 'fecha_vencimiento',
            'prioridad', 'contacto_relacionado', 'estado'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la tarea',
                'rows': 3
            }),
            'fecha_vencimiento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contacto_relacionado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar contactos activos del usuario
        if user:
            self.fields['contacto_relacionado'].queryset = Contacto.objects.filter(
                activo=True, 
                creado_por=user
            ).order_by('apellido', 'nombre')
            
            # Obtener todos los usuarios excepto el actual para asignación
            self.fields['usuarios_asignados'].queryset = User.objects.filter(
                is_active=True
            ).exclude(pk=user.pk).order_by('first_name', 'last_name', 'username')
            
        self.fields['contacto_relacionado'].empty_label = "Sin contacto relacionado"
        
        # Si estamos editando, cargar usuarios asignados
        if self.instance.pk:
            self.fields['usuarios_asignados'].initial = self.instance.usuarios_asignados
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Manejar asignaciones múltiples
            usuarios_seleccionados = self.cleaned_data.get('usuarios_asignados', [])
            
            if usuarios_seleccionados:
                # Importar el modelo aquí para evitar circular imports
                from .models import AsignacionTarea
                from django.utils import timezone
                
                # Eliminar asignaciones anteriores que ya no están seleccionadas
                AsignacionTarea.objects.filter(tarea=instance).exclude(
                    usuario__in=usuarios_seleccionados
                ).delete()
                
                # Crear nuevas asignaciones
                for usuario in usuarios_seleccionados:
                    AsignacionTarea.objects.get_or_create(
                        tarea=instance,
                        usuario=usuario,
                        defaults={
                            'estado': 'asignada',
                            'fecha_asignacion': timezone.now(),
                            'comentarios': f'Tarea asignada desde el formulario el {timezone.now().strftime("%d/%m/%Y %H:%M")}'
                        }
                    )
            else:
                # Si no hay usuarios seleccionados, eliminar todas las asignaciones
                from .models import AsignacionTarea
                AsignacionTarea.objects.filter(tarea=instance).delete()
                
        return instance


class RespuestaAsignacionForm(forms.Form):
    """Formulario para aceptar o rechazar una asignación de tarea."""
    
    RESPUESTA_CHOICES = [
        ('aceptar', 'Aceptar tarea'),
        ('rechazar', 'Rechazar tarea'),
    ]
    
    respuesta = forms.ChoiceField(
        choices=RESPUESTA_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Qué deseas hacer con esta tarea?'
    )
    
    comentarios = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Comentarios sobre tu decisión (opcional)',
            'rows': 3
        }),
        required=False,
        label='Comentarios'
    )