# forms.py
from django import forms
from django.forms import inlineformset_factory # Formularios en relacion a un modelo padre Presupuesto y Recibo
from .models import Recibo, Presupuesto, Fondo, Gasto
from django.utils.dates import MONTHS
from django.db.models.functions import ExtractYear
from django.core.exceptions import ValidationError



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

class GastoDirectoForm(forms.ModelForm):
    titulo_pres = forms.CharField(
        required=True,  
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el título',
            'oninvalid': "this.setCustomValidity('Este campo es obligatorio.')",
            'oninput': "this.setCustomValidity('')"
        }),
        error_messages={'required': "El título del presupuesto es obligatorio."}
    )

    detalle_pres = forms.CharField(
        required=False,  
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese un detalle (opcional)'})
    )

    clasificacion_gasto = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: limpieza,jardin,...'
        }),
        help_text="Ingresa las clasificaciones separadas por comas."
    )

    fecha_pres = forms.DateTimeField(
        required=True,  # Cambiado a True para que sea obligatorio
        widget=forms.DateTimeInput(attrs={'type': 'date'}),
        error_messages={'required': "La fecha del presupuesto es obligatoria."},  # Mensaje de error personalizado
        help_text="Selecciona una fecha que pertenezca al mes y año indicado."
    )

    monto_pres_dl = forms.DecimalField(
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 
            'oninvalid': "this.setCustomValidity('Si el monto es 0, deja el campo vacío.')",
            'oninput': "this.setCustomValidity('')",
            'placeholder': 'Ej: 3.14'
        }),
        error_messages={
            'invalid': "Ingresa un número válido.",
            'min_value': "Si el monto es 0, deja el campo vacío."
        }
    )
    
    class Meta:
        model = Presupuesto
        fields = '__all__'
        exclude = ['id_pres', 'id_recibo', 'tipo_pres', 'moneda_pres', 'monto_pres_bs']

    def clean(self):
        cleaned_data = super().clean()
        monto_dl = cleaned_data.get("monto_pres_dl")
        fecha = cleaned_data.get("fecha_pres")

        # Validación de campos obligatorios
        if not cleaned_data.get('titulo_pres'):
            self.add_error('titulo_pres', "El título del presupuesto es obligatorio.")

        if not fecha:  # Validar que la fecha no esté vacía
            self.add_error('fecha_pres', "La fecha del presupuesto es obligatoria.")

        if not monto_dl:
            self.add_error('monto_pres_dl', "Debe ingresar al menos un monto en Dólares.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.allowed_month = kwargs.pop('allowed_month', None)
        self.allowed_year = kwargs.pop('allowed_year', None)
        super(GastoDirectoForm, self).__init__(*args, **kwargs)
        self.fields['fecha_pres'].label = 'Fecha del Presupuesto'
        self.fields['titulo_pres'].label = 'Título del Presupuesto'
        self.fields['detalle_pres'].label = 'Descripción'
        self.fields['clasificacion_pres'].label = 'Clasificaciones'
        self.fields['monto_pres_dl'].label = 'Monto en Dólares'

    def clean_fecha_pres(self):
        fecha = self.cleaned_data.get('fecha_pres')
        if fecha and self.allowed_month and self.allowed_year:
            if fecha.month != self.allowed_month or fecha.year != self.allowed_year:
                raise forms.ValidationError(
                    f'La fecha debe pertenecer al mes {self.allowed_month} y al año {self.allowed_year}.'
                )
        return fecha

    def clean_clasificacion_pres(self):
        clasificacion = self.cleaned_data.get('clasificacion_pres')
        if clasificacion:
            clasificaciones = [c.strip() for c in clasificacion.split(',') if c.strip()]
            return ','.join(clasificaciones)
        return clasificacion
    
class PresupuestoForm(forms.ModelForm):
    titulo_pres = forms.CharField(
        required=True,  
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el título',
            'oninvalid': "this.setCustomValidity('Este campo es obligatorio.')",
            'oninput': "this.setCustomValidity('')"
        }),
        error_messages={'required': "El título del presupuesto es obligatorio."}
    )

    detalle_pres = forms.CharField(
        required=False,  
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese un detalle (opcional)'})
    )

    clasificacion_pres = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: limpieza,jardin,...'
        }),
        help_text="Ingresa las clasificaciones separadas por comas."
    )

    fecha_pres = forms.DateTimeField(
        required=True,  # Cambiado a True para que sea obligatorio
        widget=forms.DateTimeInput(attrs={'type': 'date'}),
        error_messages={'required': "La fecha del presupuesto es obligatoria."},  # Mensaje de error personalizado
        help_text="Selecciona una fecha que pertenezca al mes y año indicado."
    )

    monto_pres_dl = forms.DecimalField(
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 
            'oninvalid': "this.setCustomValidity('Si el monto es 0, deja el campo vacío.')",
            'oninput': "this.setCustomValidity('')",
            'placeholder': 'Ej: 3.14'
        }),
        error_messages={
            'invalid': "Ingresa un número válido.",
            'min_value': "Si el monto es 0, deja el campo vacío."
        }
    )
    
    class Meta:
        model = Presupuesto
        fields = '__all__'
        exclude = ['id_pres', 'id_recibo', 'tipo_pres', 'moneda_pres', 'monto_pres_bs']

    def clean(self):
        cleaned_data = super().clean()
        monto_dl = cleaned_data.get("monto_pres_dl")
        fecha = cleaned_data.get("fecha_pres")

        # Validación de campos obligatorios
        if not cleaned_data.get('titulo_pres'):
            self.add_error('titulo_pres', "El título del presupuesto es obligatorio.")

        if not fecha:  # Validar que la fecha no esté vacía
            self.add_error('fecha_pres', "La fecha del presupuesto es obligatoria.")

        if not monto_dl:
            self.add_error('monto_pres_dl', "Debe ingresar al menos un monto en en Dólares.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.allowed_month = kwargs.pop('allowed_month', None)
        self.allowed_year = kwargs.pop('allowed_year', None)
        super(PresupuestoForm, self).__init__(*args, **kwargs)
        self.fields['fecha_pres'].label = 'Fecha del Presupuesto'
        self.fields['titulo_pres'].label = 'Título del Presupuesto'
        self.fields['detalle_pres'].label = 'Descripción'
        self.fields['clasificacion_pres'].label = 'Clasificaciones'
        self.fields['monto_pres_dl'].label = 'Monto en Dólares'

    def clean_fecha_pres(self):
        fecha = self.cleaned_data.get('fecha_pres')
        if fecha and self.allowed_month and self.allowed_year:
            if fecha.month != self.allowed_month or fecha.year != self.allowed_year:
                raise forms.ValidationError(
                    f'La fecha debe pertenecer al mes {self.allowed_month} y al año {self.allowed_year}.'
                )
        return fecha

    def clean_clasificacion_pres(self):
        clasificacion = self.cleaned_data.get('clasificacion_pres')
        if clasificacion:
            clasificaciones = [c.strip() for c in clasificacion.split(',') if c.strip()]
            return ','.join(clasificaciones)
        return clasificacion

class GastoAplicadoForm(forms.ModelForm):
    titulo_gasto = forms.CharField(
        required=True,  
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el título',
            'oninvalid': "this.setCustomValidity('Este campo es obligatorio.')",
            'oninput': "this.setCustomValidity('')"
        }),
        error_messages={'required': "El título del presupuesto es obligatorio."}
    )

    detalle_gasto = forms.CharField(
        required=False,  
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese un detalle (opcional)'})
    )

    moneda_gasto = forms.ChoiceField(
        required=True,  
        choices=[('bs', 'Bolívares'), ('$', 'Dólares')],
        widget=forms.Select(attrs={
            'oninvalid': "this.setCustomValidity('Seleccione una moneda.')",
            'oninput': "this.setCustomValidity('')"
        }),
        help_text="Seleccione la moneda en la que se hará el gasto originalmente.",
        error_messages={'required': "La selección de la moneda es obligatoria."}
    )

    clasificacion_gasto = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: limpieza,jardin,...'
        }),
        help_text="Ingresa las clasificaciones separadas por comas."
    )

    fecha_gasto = forms.DateTimeField(
        required=True,  # Cambiado a True para que sea obligatorio
        widget=forms.DateTimeInput(attrs={'type': 'date'}),
        error_messages={'required': "La fecha del gasto es obligatoria."},  # Mensaje de error personalizado
        help_text="Selecciona una fecha que pertenezca al mes y año indicado."
    )

    monto_gasto_dl = forms.DecimalField(
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 
            'oninvalid': "this.setCustomValidity('Si el monto es 0, deja el campo vacío.')",
            'oninput': "this.setCustomValidity('')",
            'placeholder': 'Ej: 3.14'
        }),
        error_messages={
            'invalid': "Ingresa un número válido.",
            'min_value': "Si el monto es 0, deja el campo vacío."
        }
    )
    
    monto_gasto_bs = forms.DecimalField(
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'oninvalid': "this.setCustomValidity('Si el monto es 0, deja el campo vacío.')",
            'oninput': "this.setCustomValidity('')",
            'placeholder': 'Ej: 10.11'
        }),
        error_messages={
            'invalid': "Ingresa un número válido.",
            'min_value': "Si el monto es 0, deja el campo vacío."
        }
    )
    
    class Meta:
        model = Gasto
        fields = '__all__'
        exclude = ['id_gasto', 'id_fondo']

    def clean(self):
        cleaned_data = super().clean()
        monto_bs = cleaned_data.get("monto_gasto_bs")
        monto_dl = cleaned_data.get("monto_gasto_dl")
        moneda = cleaned_data.get("moneda_gasto")
        fecha = cleaned_data.get("fecha_gasto")

        # Validación de campos obligatorios
        if not cleaned_data.get('titulo_gasto'):
            self.add_error('titulo_gasto', "El título del gasto es obligatorio.")

        if not cleaned_data.get('moneda_gasto'):
            self.add_error('moneda_gasto', "La selección de la moneda es obligatoria.")

        if not fecha:  # Validar que la fecha no esté vacía
            self.add_error('fecha_gasto', "La fecha del presupuesto es obligatoria.")

        if not monto_bs and not monto_dl:
            self.add_error('monto_gasto_bs', "Debe ingresar al menos un monto en Bolívares o en Dólares.")
            self.add_error('monto_gasto_dl', "Debe ingresar al menos un monto en Bolívares o en Dólares.")

        if monto_bs and not monto_dl and moneda != 'bs':
            self.add_error('moneda_gasto', "La moneda debe ser 'bs' si solo hay monto en Bolívares.")

        if monto_dl and not monto_bs and moneda != '$':
            self.add_error('moneda_gasto', "La moneda debe ser '$' si solo hay monto en Dólares.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.allowed_month = kwargs.pop('allowed_month', None)
        self.allowed_year = kwargs.pop('allowed_year', None)
        super(GastoAplicadoForm, self).__init__(*args, **kwargs)
        self.fields['fecha_gasto'].label = 'Fecha del Gasto'
        self.fields['titulo_gasto'].label = 'Título del Gasto'
        self.fields['detalle_gasto'].label = 'Descripción'
        self.fields['clasificacion_gasto'].label = 'Clasificaciones'
        self.fields['monto_gasto_bs'].label = 'Monto en Bolívares'
        self.fields['monto_gasto_dl'].label = 'Monto en Dólares'
        self.fields['moneda_gasto'].label = 'Tipo de Moneda'

    def clean_fecha_gasto(self):
        fecha = self.cleaned_data.get('fecha_gasto')
        if fecha and self.allowed_month and self.allowed_year:
            if fecha.month != self.allowed_month or fecha.year != self.allowed_year:
                raise forms.ValidationError(
                    f'La fecha debe pertenecer al mes {self.allowed_month} y al año {self.allowed_year}.'
                )
        return fecha

    def clean_clasificacion_gasto(self):
        clasificacion = self.cleaned_data.get('clasificacion_gasto')
        if clasificacion:
            clasificaciones = [c.strip() for c in clasificacion.split(',') if c.strip()]
            return ','.join(clasificaciones)
        return clasificacion
    




class FondoImprevistoForm(forms.ModelForm):
    monto_pres_dl = forms.DecimalField(
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 
            'oninvalid': "this.setCustomValidity('Si el monto es 0, deja el campo vacío.')",
            'oninput': "this.setCustomValidity('')",
            'placeholder': 'Ej: 3.14'
        }),
        error_messages={
            'invalid': "Ingresa un número válido.",
            'min_value': "Si el monto es 0, deja el campo vacío."
        }
    )
    
    class Meta:
        model = Presupuesto
        fields = '__all__'
        exclude = ['clasificacion_pres', 'id_pres', 'titulo_pres', 'detalle_pres', 'id_recibo', 'tipo_pres', 'moneda_pres', 'monto_pres_bs', 'fecha_pres']

    def clean(self):
        cleaned_data = super().clean()
        monto_dl = cleaned_data.get("monto_pres_dl")

        if not monto_dl:
            self.add_error('monto_pres_dl', "Debe ingresar un monto en Dólares para el fondo de imprevistos.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(FondoImprevistoForm, self).__init__(*args, **kwargs)  # Corregido
        self.fields['monto_pres_dl'].label = 'Monto para fondo de imprevistos en Dólares'