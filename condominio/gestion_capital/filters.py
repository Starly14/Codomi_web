import django_filters
from .models import Importe, Recibo, Recibo_p, Dpto

# Constante para los meses (choices)
MONTH_CHOICES = [
    ('01', 'Enero'),
    ('02', 'Febrero'),
    ('03', 'Marzo'),
    ('04', 'Abril'),
    ('05', 'Mayo'),
    ('06', 'Junio'),
    ('07', 'Julio'),
    ('08', 'Agosto'),
    ('09', 'Septiembre'),
    ('10', 'Octubre'),
    ('11', 'Noviembre'),
    ('12', 'Diciembre'),
]

class FiltroFecha(django_filters.FilterSet):
    # Se encarga de tomar los años de la BDD
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Extrae los años únicos de 'fecha_importe' de Importe y actualiza los choices
        years = Importe.objects.dates('fecha_importe', 'year', order='ASC')
        year_choices = [(str(date.year), str(date.year)) for date in years]
        self.filters['anio'].extra['choices'] = year_choices
    
    mes = django_filters.ChoiceFilter(
        choices=MONTH_CHOICES,
        method='filtro_por_mes',
        label='Mes'
    )
   
    anio = django_filters.ChoiceFilter(
        method='filtro_por_anio',
        label='Año'
    )

    # Obtenemos todos los departamentos
    id_dpto = django_filters.ModelChoiceFilter(
        queryset=Dpto.objects.all(),
        method='filtro_por_id_dpto',
        label='Departamento'
    )

    class Meta:
        model = Importe
        fields = ['mes', 'anio', 'id_dpto']

    
    def filtro_por_mes(self, queryset, name, value):
        return queryset.filter(fecha_importe__month=value) if value else queryset # __ permite ingresar al valor

    def filtro_por_anio(self, queryset, name, value):
        return queryset.filter(fecha_importe__year=value) if value else queryset

    def filtro_por_id_dpto(self, queryset, name, value):
        return queryset.filter(id_dpto=value) if value else queryset

class HistorialRecibosFilter(django_filters.FilterSet):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Extrae los años únicos de 'fecha_importe' de Importe y actualiza los choices
        years = Importe.objects.dates('fecha_importe', 'year', order='ASC')
        year_choices = [(str(date.year), str(date.year)) for date in years]
        self.filters['anio'].extra['choices'] = year_choices

    mes = django_filters.ChoiceFilter(
        choices=MONTH_CHOICES,
        method='filtro_por_mes',
        label='Mes'
    )
  
    anio = django_filters.ChoiceFilter(
        method='filtro_por_anio',
        label='Año'
    )
    id_dpto = django_filters.ModelChoiceFilter(
        queryset=Dpto.objects.all(),
        label='Departamento'
    )
    nombre_prop = django_filters.CharFilter(
        field_name='id_dpto__asignaciones__id_prop__nombre_prop',
        lookup_expr='icontains',
        label='Nombre Propietario'
    )

    class Meta:
        model = Recibo_p
        fields = ['id_dpto', 'nombre_prop', 'mes', 'anio']

    def filtro_por_mes(self, queryset, name, value):
        return queryset.filter(id_recibo__fecha_recibo__month=value) if value else queryset

    def filtro_por_anio(self, queryset, name, value):
        return queryset.filter(id_recibo__fecha_recibo__year=value) if value else queryset
