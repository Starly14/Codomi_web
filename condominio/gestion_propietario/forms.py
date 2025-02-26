from django import forms
from .models import Propietario, Correo

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['nombre_prop']

        labels = {  # Eliminar el label "Correo"
            'nombre_prop': '',
        }

        widgets = { # 
            'nombre_prop': forms.TextInput(attrs={
                'placeholder': 'Nuevo nombre',  # Placeholder
            }),
        }

class CorreoForm(forms.ModelForm):
    class Meta:
        model = Correo
        fields = ['correo']
        widgets = {
            'correo': forms.EmailInput(attrs={
                'placeholder': 'Introduzca el correo',  # Placeholder
                'required': 'required',
                'oninvalid': "this.setCustomValidity('Por favor, introduce un correo electrónico válido.')",
                'oninput': "this.setCustomValidity('')",
            }),
        }
        labels = {  # Eliminar el label "Correo"
            'correo': '',
        }
        error_messages = {
            'correo': {
                'unique': 'Este correo ya está registrado.',
                'invalid': 'Por favor, introduce un correo electrónico válido.',
            },
        }