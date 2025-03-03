from django.shortcuts import render

from .models import Recibo_p
from .filters import HistorialRecibosFilter
 # permite mostrar una lista de objetos del modelo
from .models import Importe
from .filters import FiltroFecha

def gestion_capital(request):
    return render(request, "gestion_capital/gestionCapital.html")

def vista_con_filtro(request):
    filtro = FiltroFecha(request.GET)
    # Queryset inicial (todos los query)
    queryset = Importe.objects.all()

    if filtro.is_valid(): # Verifica que la informacion proporcionada en el form es correcta
        queryset = filtro.qs
        contexto = {'filtro': filtro, 'queryset': queryset}

    return render(request, 'gestion_capital/importe_list.html', contexto)

def historial_recibos(request):
    filtro = HistorialRecibosFilter(request.GET, queryset=Recibo_p.objects.all())
    return render(request, 'gestion_capital/historial_recibos.html', {
        'filtro': filtro,
        'queryset': filtro.qs  # los resultados filtrados
    })