from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Propietario, Correo, Dpto, Asignacion, Recibo, Deuda, Presupuesto, Comentario, Importe, Gasto
from .forms import PropietarioForm, CorreoForm, DptoForm, FechaForm

def propietario_detail(request, id):
    # se definen las variables iniciales
    propietario = get_object_or_404(Propietario, id_prop=id)
    correos = Correo.objects.filter(id_prop=propietario)
    propietarios = Propietario.objects.all()
    propietario_form = PropietarioForm(instance=propietario)
    correo_form = CorreoForm()

    if request.method == 'POST':
        if 'edit_nombre' in request.POST: # guarda un form con el nombre insertado
            propietario_form = PropietarioForm(request.POST, instance=propietario)
            if propietario_form.is_valid():
                propietario_form.save()
                return redirect('propietario-detail', id=id)

        elif 'add_correo' in request.POST: # guarda un form con el correo insertado, agregandolo a la lista de correos
            correo_form = CorreoForm(request.POST)
            if correo_form.is_valid():
                nuevo_correo = correo_form.save(commit=False)
                nuevo_correo.id_prop = propietario
                nuevo_correo.save()
                return redirect('propietario-detail', id=id)

        elif 'delete_correo' in request.POST: # envia un post con el id del correo a eliminar
            correo_id = request.POST.get('correo_id')
            Correo.objects.filter(correo=correo_id).delete()
            return redirect('propietario-detail', id=id)
        
        elif 'delete_propietario' in request.POST: # NO ESTA SIENDO USADO, UTIL EN OTRA CIRCUNSTANCIA
            propietario_id = request.POST.get('propietario_id')
            Propietario.objects.filter(id_prop=propietario_id).delete()
            return redirect('propietario-detail', id=id)
        
        elif 'redirect_propietario' in request.POST: #redirige al editar propietario del propietario seleccionado
            propietario_id = request.POST.get('propietario_id')
            return redirect('propietario-detail', id=propietario_id) 

    else:
        propietario_form = PropietarioForm(instance=propietario)
        correo_form = CorreoForm()

    return render(request, 'editarPropietario.html', {
        'propietario': propietario,
        'correos': correos,
        'propietario_form': propietario_form,
        'correo_form': correo_form,
        'propietarios': propietarios,
    })

def registrarPropietarioView(request):
    correos = Correo.objects.all()
    propietarios = Propietario.objects.all()
    dptos = Dpto.objects.all()
    
    propietario_form = PropietarioForm()
    correo_form = CorreoForm()
    dpto_form = DptoForm()
    fecha_form = FechaForm()

    if request.method == 'POST':
        propietario_form = PropietarioForm(request.POST)
        correo_form = CorreoForm(request.POST)
        fecha_form = FechaForm(request.POST)

        # Extraer ID del departamento manualmente antes de validar el formulario
        id_dpto = request.POST.get('id_dpto')

        try:
            nuevo_dpto = Dpto.objects.get(id_dpto=id_dpto)  # Buscar el departamento existente
        except Dpto.DoesNotExist:
            dpto_form = DptoForm(request.POST)
            return render(request, 'registrarPropietario.html', {
                'error': 'Error en el departamento',
                'correos': correos,
                'propietarios': propietarios,
                'dptos': dptos,
                'propietario_form': propietario_form,
                'correo_form': correo_form,
                'dpto_form': dpto_form,
                'fecha_form': fecha_form,
            })

        if propietario_form.is_valid() and correo_form.is_valid() and fecha_form.is_valid():
            nuevo_propietario = propietario_form.save(commit=True)

            # Guardar o reutilizar el correo
            correo_valor = correo_form.cleaned_data['correo']
            correo_existente = Correo.objects.filter(correo=correo_valor).first()
            if not correo_existente:
                nuevo_correo = correo_form.save(commit=False)
                nuevo_correo.id_prop = nuevo_propietario
                nuevo_correo.save()
            else:
                #aqui, chatgpt por favor, haz que se borre 
                Propietario.objects.filter(id_prop=nuevo_propietario.id_prop).delete
                return render(request, 'registrarPropietario.html', {
                    'error': 'Error en el departamento',
                    'correos': correos,
                    'propietarios': propietarios,
                    'dptos': dptos,
                    'propietario_form': propietario_form,
                    'correo_form': correo_form,
                    'dpto_form': dpto_form,
                    'fecha_form': fecha_form,
                })

            # Guardar la asignación del departamento
            fecha_inicio = fecha_form.cleaned_data['fecha_inicio']

            # Si ya hay una asignación activa, cerrarla antes de crear una nueva
            try:
                asignacion_existente = Asignacion.objects.get(id_dpto=nuevo_dpto, fecha_fin__isnull=True)
                asignacion_existente.fecha_fin = fecha_inicio
                asignacion_existente.save()
            except Asignacion.DoesNotExist:
                pass

            nueva_asignacion = Asignacion(
                id_prop=nuevo_propietario,
                id_dpto=nuevo_dpto,
                fecha_inicio=fecha_inicio,
                fecha_fin=None
            )
            nueva_asignacion.save()
            print('a ver deberia hacerlo todo hasta aca')
            return redirect('propietario-detail', id=nuevo_propietario.id_prop)

    return render(request, 'registrarPropietario.html', {
        'correos': correos,
        'propietarios': propietarios,
        'dptos': dptos,
        'propietario_form': propietario_form,
        'correo_form': correo_form,
        'dpto_form': dpto_form,
        'fecha_form': fecha_form,
    })



def plantillaBase(request):
    return render(request, "Plantilla.html")
