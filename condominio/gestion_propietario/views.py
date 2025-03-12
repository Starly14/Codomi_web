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




def reciboBase(request, year, month, day, nro_dpto):

    dpto = get_object_or_404(Dpto, id_dpto=nro_dpto)

    # Filtrar asignaciones por el departamento y con fecha menor a `year`
    asignacion = Asignacion.objects.filter(
        id_dpto=dpto,
        fecha_inicio__lt=f"{year}-{month}-{day}"  # Fecha menor al año dado
    ).order_by('-fecha_inicio').first()  # Ordenar por fecha descendente y tomar el más reciente

    if asignacion:
        print(f"Asignación encontrada: {asignacion}")
    else:
        print("No se encontró ninguna asignación.")
        
    propietario = asignacion.id_prop # al hacer esto, obtienes el objeto dpto como tal
    edif = dpto.id_edif  # igual aca

    recibo = get_object_or_404(Recibo, fecha_recibo__year=year, fecha_recibo__month=month)
    
    fechas = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    fecha_escrita = f'{day} de {fechas[month-1]}, {year}'

    if month < 12:
        mes_siguiente = fechas[month]
        ano_siguiente = year
    else:
        mes_siguiente = fechas[0]
        ano_siguiente = year+1

    presupuestos = Presupuesto.objects.filter(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='previsto')
    directos = Presupuesto.objects.filter(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='directo')
    fondo = Presupuesto.objects.get(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='fondo')

    monto_presupuestos = []
    monto_directos = []
    monto_fondo = fondo.monto_pres_dl

    for presupuesto in presupuestos:
        if presupuesto.monto_pres_bs == None:
            monto_presupuestos.append({'titulo': presupuesto.titulo_pres, 'monto': f'{presupuesto.monto_pres_dl}$'})
        if presupuesto.monto_pres_dl == None:
            monto_presupuestos.append({'titulo': presupuesto.titulo_pres, 'monto': f'{presupuesto.monto_pres_bs}Bs.'})

    for directo in directos:
        if directo.monto_pres_bs == None:
            monto_directos.append({'titulo': directo.titulo_pres, 'monto': f'{directo.monto_pres_dl}$'})
        if directo.monto_pres_dl == None:
            monto_directos.append({'titulo': directo.titulo_pres, 'monto': f'{directo.monto_pres_bs}Bs.'})

    #a futuro, por cuestiones de otros condominios, esto debe ser cambiado a como esta con gastos
        
    subtotal = 0
    for i,v in enumerate(presupuestos):
        subtotal += v.monto_pres_dl
    
    reserva = subtotal
    reserva /= 2

    total = sum([subtotal, reserva, monto_fondo])

    total_alicuotaC = dpto.alicuota * total / 100

    total_alicuota = round(total_alicuotaC,2) #total multiplicado por la alicuota redondeado

    suma_directos = 0
    for i,v in enumerate(directos):
        suma_directos += v.monto_pres_dl
    
    totales = suma_directos
    totales += total_alicuota

    comentarios_ids = Comentario.objects.filter(id_recibo=recibo.id_recibo)

    comentarios = []

    for comentario in comentarios_ids:
        com = comentario.id_comentario
        comentarios.append(com)

    importesObjects = Importe.objects.filter(id_dpto=nro_dpto, fecha_importe__lt=recibo.fecha_recibo)
    importes = []
    for i in importesObjects:
        importes.append(i.pago_dl)
    
    deudasObjects = Deuda.objects.filter(id_dpto=nro_dpto, fecha_cta__lt=recibo.fecha_recibo)
    deudas = []
    for i in deudasObjects:
        deudaPersonal = i.deuda
        deudas.append(deudaPersonal)
    
    totalImportes = sum(importes)
    totalDeudas = sum(deudas)

    print(totalImportes)
    print(totalDeudas)
    for i in importes:
        print(i)

    print('\n\n\nespacio\n\n\n')

    for i in deudas:
        print(i)

    print('\n\n\nespacio\n\n\n')

    print(totalImportes-totalDeudas)

    deudaFinal = totalDeudas-totalImportes
    totalPagar = totales + deudaFinal

    gastos = Gasto.objects.filter(fecha_gasto__year=year, fecha_gasto__month=month)

    monto_gastos = []

    sumaGastosdl = []
    sumaGastosbs = []
    for gasto in gastos:
        if gasto.monto_gasto_bs == None and gasto.moneda_gasto == '$':
            monto_gastos.append({'titulo': gasto.titulo_gasto, 'monto': f'{gasto.monto_gasto_dl}$'})
            sumaGastosdl.append(gasto.monto_gasto_dl)
        elif gasto.monto_gasto_dl == None and gasto.moneda_gasto == 'bs':
            monto_gastos.append({'titulo': gasto.titulo_gasto, 'monto': f'{gasto.monto_gasto_bs} Bs.'})
            sumaGastosbs.append(gasto.monto_gasto_bs)
        else:
            monto_gastos.append({'titulo': gasto.titulo_gasto, 'monto': f'{gasto.monto_gasto_bs} Bs. ({gasto.monto_gasto_dl}$)'})
            sumaGastosbs.append(gasto.monto_gasto_bs)

    gastoFinalbs = f'{sum(sumaGastosbs)}Bs.'

    if len(sumaGastosdl) == 0:
        gastoFinaldl = ''
    else:
        gastoFinaldl = f'   ({sum(sumaGastosdl)}$)'



    return render(request, 'recibo.html', {
        'edif': edif,
        'prop': propietario,
        'recibo': recibo,
        'fecha_escrita': fecha_escrita,
        'dpto': dpto,
        'mes_siguiente': mes_siguiente,
        'ano_siguiente': ano_siguiente,
        'monto_presupuestos': monto_presupuestos,
        'monto_directos': monto_directos,
        'monto_fondo': monto_fondo,
        'subtotal': subtotal,
        'reserva': reserva,
        'fondo': monto_fondo,
        'total': total,
        'total_alicuota': total_alicuota,
        'suma_directos': suma_directos,
        'totales': totales,
        'comentarios': comentarios,
        'deudaFinal': deudaFinal,
        'totalPagar': totalPagar,
        'monto_gastos': monto_gastos,
        'gastoFinaldl': gastoFinaldl,
        'gastoFinalbs': gastoFinalbs,
    })
