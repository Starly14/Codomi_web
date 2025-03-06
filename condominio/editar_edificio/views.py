from django.shortcuts import render, get_object_or_404, redirect
from .models import Edif
from .forms import EdifForm
import base64

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

    if edificio.foto_edif:
        foto_bytes = bytes(edificio.foto_edif)  # Convertir memoryview a bytes
        foto_base64 = base64.b64encode(foto_bytes).decode('utf-8')
        from imghdr import what
        image_type = what(None, foto_bytes)
        foto_url = f"data:image/{image_type};base64,{foto_base64}" if image_type else None
    else:
        foto_url = None

    return render(request, 'editar_edificio.html', {'form': form, 'edificio': edificio, 'foto_url': foto_url})