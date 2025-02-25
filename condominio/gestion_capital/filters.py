import django_filters
from .models import importe
from django.db.models import Q

class FiltroFecha(django_filters.FilterSet):
    # Creacion de las opciones a mostrar
    mes = django_filters.ChoiceFilter(
        choices=[
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
        ], 
        method='filtro_por_mes', 
        label='Mes'
    )

    agno = django_filters.ChoiceFilter(
        choices=[
            ('2022', '2022'),
            ('2023', '2023'),
            ('2024', '2024'),
        ],
        method='filtro_por_agno',
        label='Año'
    )
    
    id_dpto = django_filters.ChoiceFilter(
        choices=importe.IdDptoChoices.choices,
        method='filtro_por_id_dpto',
        label='Departamento'
    )

    class Meta:
        model = importe
        # Campos sobre los que se va a filtrar
        fields = ['mes', 'agno', 'id_dpto']

    def filtro_por_mes(self, queryset, name, value):
        if value:
            return queryset.filter(fecha_importe__month=value) #Filtra por la string del mes que django toma como el numero del mes. __month es una propiedad de django
        return queryset

    def filtro_por_agno(self, queryset, name, value):

        if value:
            return queryset.filter(fecha_importe__year=value)
        return queryset

    def filtro_por_id_dpto(self, queryset, name, value):
        if value:
            return queryset.filter(id_dpto=value)
        return queryset