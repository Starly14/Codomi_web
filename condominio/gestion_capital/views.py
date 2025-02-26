from django.shortcuts import render
 # permite mostrar una lista de objetos del modelo
from .models import importe
from .filters import FiltroFecha

def gestion_capital(request):
    return render(request, "gestion_capital/gestionCapital.html")

def vista_con_filtro(request):
    filtro = FiltroFecha(request.GET)
    # Queryset inicial (todos los query)
    queryset = importe.objects.all()

    if filtro.is_valid(): # Verifica que la informacion proporcionada en el form es correcta
        queryset = filtro.qs
        contexto = {'filtro': filtro, 'queryset': queryset}

    return render(request, 'gestion_capital/importe_list.html', contexto)