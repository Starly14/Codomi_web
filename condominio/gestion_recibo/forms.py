# forms.py
from django import forms
from django.forms import inlineformset_factory # Formularios en relacion a un modelo padre Presupuesto y Recibo
from .models import Recibo, Presupuesto

class PresupuestoForm(forms.ModelForm): # Creacion del formulario basada en el modelo
    class Meta:
        model = Presupuesto
        fields = [
            'titulo_pres',
            'detalle_pres',
            'monto_pres_bs',
            'monto_pres_dl',
            'fecha_pres',
            'clasificacion_pres',
            'tipo_pres',
        ]
        widgets = {
            'fecha_pres': forms.DateTimeInput(attrs={'type': 'datetime-local'}), # Para mostrar con mejor interactividad
        }

# Vinculacion de los modelos padre e hijo para que cada presupuesto se vincule a un solo recibo
PresupuestoFormSet = inlineformset_factory(
    Recibo, 
    Presupuesto, 
    form=PresupuestoForm, 
    extra=1,  # Número de formularios vacíos que se muestran inicialmente
    can_delete=True  # Permite eliminar formularios si es necesario
)
