from django import forms
from .models import Edif

class EdifForm(forms.ModelForm):
    class Meta:
        model = Edif
        fields = ['nombre_edif', 'rif', 'direccion_edif', 'foto_edif']