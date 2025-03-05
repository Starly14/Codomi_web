from django.shortcuts import render, get_object_or_404, redirect
from .models import Edif
from .forms import EdifForm

def editar_edificio(request, id_edif):

    """if not request.user.is_authenticated:
        return redirect('login')"""    # Esto se debe ajustar para que redirija a login si no se ha iniciado sesión
    
    edificio = get_object_or_404(Edif, id_edif=id_edif)

    if request.method == 'POST':
        form = EdifForm(request.POST, request.FILES, instance=edificio)
        if form.is_valid():
            form.save()
            return redirect('editar_edificio', id_edif=edificio.id_edif)
    else:
        form = EdifForm(instance=edificio)

    return render(request, 'editar_edificio.html', {'form': form, 'edificio': edificio})