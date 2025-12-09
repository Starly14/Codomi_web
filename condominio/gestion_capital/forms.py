import calendar
from django import forms
from datetime import datetime, timedelta

from .models import Dpto, Fondo, Gasto, Presupuesto

class FondoFiltroForm(forms.Form):
    mes = forms.ChoiceField(
        choices=[
            ("1", "Enero"), ("2", "Febrero"), ("3", "Marzo"),
            ("4", "Abril"), ("5", "Mayo"), ("6", "Junio"),
            ("7", "Julio"), ("8", "Agosto"), ("9", "Septiembre"),
            ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre")
        ],
        label="Mes",
        required=True  # Hacerlo requerido
    )
    anio = forms.ChoiceField(
        label="Año",
        choices=[],  # Se llenará dinámicamente
        required=True  # Hacerlo requerido
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener los años únicos de los fondos
        years_fondo = Fondo.objects.dates('fecha_fondo', 'year')
        all_years = sorted({dt.year for dt in years_fondo}, reverse=True)
        if not all_years:
            from datetime import datetime
            all_years = [datetime.now().year]
        # Asignar los años al campo de elección
        self.fields['anio'].choices = [(str(year), str(year)) for year in all_years]


class EstadoCuentaFiltroForm(forms.Form):
    
    departamento = forms.ModelChoiceField(queryset=Dpto.objects.all(), label="Departamento", required=False)
    mes = forms.ChoiceField(
    choices=[("", "Todos")] + [
        ("1", "Enero"), ("2", "Febrero"), ("3", "Marzo"),
        ("4", "Abril"), ("5", "Mayo"), ("6", "Junio"),
        ("7", "Julio"), ("8", "Agosto"), ("9", "Septiembre"),
        ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre")
    ],
    label="Mes",
    required=False
)
    anio = forms.ChoiceField(
        label="Año",
        choices=[],  # Se llenará dinámicamente
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtenemos los años únicos de las fechas en las tablas relevantes
        years_fondo = Fondo.objects.dates('fecha_fondo', 'year')
        years_gasto = Gasto.objects.dates('fecha_gasto', 'year')
        years_presupuesto = Presupuesto.objects.dates('fecha_pres', 'year')
        # Extraemos el año (entero) y unimos en un set
        all_years = sorted(
            {dt.year for dt in list(years_fondo) + list(years_gasto) + list(years_presupuesto)},
            reverse=True
        )
        if not all_years:
            from datetime import datetime
            all_years = [datetime.now().year]
        # Agregamos opción "Todos" como valor por defecto
        self.fields['anio'].choices = [("", "Todos")] + [(str(year), str(year)) for year in all_years]