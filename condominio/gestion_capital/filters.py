import django_filters
from .models import importe

class ImporteFilter(django_filters.FilterSet):
    # revisar si existe CharFilter()
    id_dpto = django_filters.CharFilter(field_name='id_dpto__id_dpto', lookup_expr='exact')

    # revisar si existe DateTimeFilter()
    fecha_importe = django_filters.CharFilter(method='filter_by_month_and_year')

    class Meta:
        model = importe
        fields = ['id_dpto', 'fecha_importe']
    
    def filter_by_month_and_year(self, queryset, name, value):
        try:
            
            year, month = value.split('-')
            return queryset.filter(
                fecha_importe__year=year,
                fecha_importe__month=month
            )
        except (ValueError, IndexError):
            return queryset