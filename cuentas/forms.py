from django import forms
from .models import provincia, localidad

class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = provincia
        fields = ['nombre_provincia', 'codigo_provincia', 'pais_idpais']

class LocalidadForm(forms.ModelForm):
    class Meta:
        model = localidad
        fields = ['nombre_localidad', 'cp_localidad', 'provincia_id_provincia']
