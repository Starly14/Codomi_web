from django.shortcuts import render
from django.views.generic import ListView # permite mostrar una lista de objetos del modelo
from .models import importe
from .filters import ImporteFilter

def gestion_capital(request):
    return render(request, "gestion_capital/gestionCapital.html")

class ImporteListView(ListView):
    model = importe # modelo que se va a listar
    template_name = 'importe_list.html'
    context_object_name = 'importes'

    # metodo que se ejecuta antes de mostrar los datos
    def get_queryset(self):
        queryset = super().get_queryset() # obtiene todos los querysets del modelo
        self.filterset = ImporteFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs # retorna el queryset filtrado

    # datos que se van a enviar al template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

