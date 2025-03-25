from django import forms

class FechaFiltroForm(forms.Form):
    fecha_inicio = forms.DateField(
        label='Desde',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'fecha-filter'})
    )
    fecha_fin = forms.DateField(
        label='Hasta',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'fecha-filter'})
    )