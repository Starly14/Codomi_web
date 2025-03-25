from django import forms
from .models import Asignacion
from datetime import date
from .models import Propietario, Correo, Dpto, Asignacion

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
                'class': 'rounded-lg py-1 pl-5' ,
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
                'oninput': "this.setCustomValidity('')",
                'class': 'rounded-lg py-1 pl-5' ,
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

class DptoForm(forms.ModelForm):
    class Meta:
        model = Dpto
        fields = ['id_dpto']
        labels = {
            'id_dpto': '',
        }
        widgets = {
            'id_dpto': forms.TextInput(attrs={'placeholder': 'Departamento',
                                              'class': 'rounded-lg' ,}),
        }

    def clean_id_dpto(self):
        id_dpto = self.cleaned_data.get('id_dpto')
        if not Dpto.objects.filter(id_dpto=id_dpto).exists():
            raise forms.ValidationError("El departamento ingresado no existe.")
        return id_dpto

class FechaForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['fecha_inicio']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'value': date.today().strftime('%Y-%m-%d'),
                                                    'class': 'rounded-lg' ,
            }),
           
        }
        labels = {
            'fecha_inicio': '',
        }

    def clean_fecha_inicio(self):
        fecha_ingresada = self.cleaned_data['fecha_inicio']

        if fecha_ingresada is not None:
            fecha_ingresada = fecha_ingresada.date()  # Convertir a date para la comparación
        
        fecha_actual = date.today()

        if fecha_ingresada > fecha_actual:
            raise forms.ValidationError("No puedes seleccionar una fecha futura.")

        return fecha_ingresada
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_inicio'].input_formats = ['%d/%m/%Y']