from django.shortcuts import render, get_object_or_404, redirect
from .models import Propietario, Correo
from .forms import PropietarioForm, CorreoForm
from django.db import IntegrityError

def propietario_detail(request, id):
    propietario = get_object_or_404(Propietario, id_prop=id)
    correos = Correo.objects.filter(id_prop=propietario)

    propietario_form = PropietarioForm(instance=propietario)
    correo_form = CorreoForm()
    if request.method == 'POST':
        if 'edit_nombre' in request.POST:
            propietario_form = PropietarioForm(request.POST, instance=propietario)
            if propietario_form.is_valid():
                propietario_form.save()
                return redirect('propietario-detail', id=id)

        elif 'add_correo' in request.POST:
            correo_form = CorreoForm(request.POST)
            if correo_form.is_valid():
                nuevo_correo = correo_form.save(commit=False)
                nuevo_correo.id_prop = propietario
                nuevo_correo.save()
                return redirect('propietario-detail', id=id)

        elif 'delete_correo' in request.POST:
            correo_id = request.POST.get('correo_id')
            Correo.objects.filter(correo=correo_id).delete()
            return redirect('propietario-detail', id=id)

    else:
        propietario_form = PropietarioForm(instance=propietario)
        correo_form = CorreoForm()

    return render(request, 'Registrar_usuario.html', {
        'propietario': propietario,
        'correos': correos,
        'propietario_form': propietario_form,
        'correo_form': correo_form,
    })