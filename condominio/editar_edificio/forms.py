from django import forms
from .models import Edif

class EdifForm(forms.ModelForm):
    archivo = forms.FileField(required=False)

    class Meta:
        model = Edif
        fields = ['nombre_edif', 'rif', 'direccion_edif']