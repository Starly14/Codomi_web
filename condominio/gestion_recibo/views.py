from django.shortcuts import render, redirect, get_object_or_404
from .models import Recibo
from .forms import PresupuestoFormSet

def crear_presupuestos(request, id_recibo):
    recibo = get_object_or_404(Recibo, id_recibo=id_recibo)
    
    if request.method == 'POST':
        formset = PresupuestoFormSet(request.POST, instance=recibo)
        if formset.is_valid():
            formset.save()
            return # Por crear 
    else:
        formset = PresupuestoFormSet(instance=recibo)
    
    return render(request, 'templates/crear_presupuestos.html', {'formset': formset, 'recibo': recibo})
