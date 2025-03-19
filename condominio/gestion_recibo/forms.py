# forms.py
from django import forms
from django.forms import inlineformset_factory # Formularios en relacion a un modelo padre Presupuesto y Recibo
from .models import Recibo, Presupuesto, Fondo, Gasto
from django.utils.dates import MONTHS
from django.db.models.functions import ExtractYear


# UPDATE: he borrado detalles_fondo de los campos a llenar por el administrador
class FondoForm(forms.ModelForm):
    ingresos = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01'})
    )
    
    egresos = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01'})
    )

    class Meta:
        model = Fondo
        fields = ['moneda_fondo', 'ingresos', 'egresos', 'fecha_fondo'] 
        widgets = {
            'fecha_fondo': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'fecha-input'
            }),
        }

class FechaFiltroForm(forms.Form):
    fecha_inicio = forms.DateField(
        label='Desde',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'fecha-filter'})
    )
    fecha_fin = forms.DateField(
        label='Hasta',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'fecha-filter'})
    )

class MesAnioFiltroForm(forms.Form):

    mes = forms.ChoiceField(
        choices=[(i, MONTHS[i].title()) for i in range(1, 13)],
        label="Mes"
    )

    anio = forms.ChoiceField(
        label="Año",
        choices=[]  # Se llenará dinámicamente
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtenemos años únicos de todas las tablas relevantes
        years_fondo = Fondo.objects.dates('fecha_fondo', 'year').annotate(year=ExtractYear('fecha_fondo')).values_list('year', flat=True).distinct()
        years_gasto = Gasto.objects.dates('fecha_gasto', 'year').annotate(year=ExtractYear('fecha_gasto')).values_list('year', flat=True).distinct()
        years_presupuesto = Presupuesto.objects.dates('fecha_pres', 'year').annotate(year=ExtractYear('fecha_pres')).values_list('year', flat=True).distinct()

        all_years = sorted(set(
            list(years_fondo) + 
            list(years_gasto) + 
            list(years_presupuesto)
        ), reverse=True)

        if not all_years:
            from datetime import datetime
            current_year = datetime.now().year
            all_years = [current_year]
        
        # Actualizamos las opciones del campo año
        self.fields['anio'].choices = [(str(year), str(year)) for year in all_years]

class PresupuestoForm(forms.ModelForm):
    monto_pres_bs = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01'})
    )
    
    monto_pres_dl = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01'})
    )

    class Meta:
        model = Presupuesto
        fields = ['titulo_pres', 'detalle_pres', 'monto_pres_bs', 'monto_pres_dl', 'moneda_pres', 'fecha_pres', 'clasificacion_pres', 'tipo_pres']
        widgets = {
            'fecha_pres': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'fecha-input'
            }),
            'moneda_pres': forms.TextInput(attrs={
                'placeholder': 'Ingrese la moneda (ejemplo: USD, EUR, VES)',
                'class': 'moneda-input'
            }),
            'clasificacion_pres': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ingrese la clasificación del presupuesto',
                'class': 'clasificacion-textarea'
            }),
            'tipo_pres': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ingrese el tipo de presupuesto',
                'class': 'tipo-textarea'
            }),
        }