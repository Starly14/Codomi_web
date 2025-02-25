from django import forms
from .models import Propietario, Correo

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['nombre_prop']

class CorreoForm(forms.ModelForm):
    class Meta:
        model = Correo
        fields = ['correo']
        widgets = {
            'correo': forms.EmailInput(attrs={
                'required': 'required',
                'oninvalid': "this.setCustomValidity('Por favor, introduce un correo electrónico válido.')",
                'oninput': "this.setCustomValidity('')",
            }),
        }
        #mensaje de error cuando el correo
        error_messages = {
            'correo': {
                'unique': 'Este correo ya está registrado.',
                'invalid': 'Por favor, introduce un correo electrónico válido.',
            },
        }
