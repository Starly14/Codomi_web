from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.db import connection
from django.urls import reverse
from .forms import FondoForm, FechaFiltroForm, PresupuestoForm, GastoDirectoForm, GastoAplicadoForm, FondoImprevistoForm, ComentarioForm, DptoForm
from .models import Fondo, Gasto, Presupuesto, Dpto, Asignacion, Recibo, Deuda, Comentario, Importe, ComentarioFrec
from datetime import datetime, date
import base64


# Para ser guardado en la BD se genera la prox PK disponible en la tabla
def obtener_nuevo_id_fondo():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(id_fondo), 0) + 1 FROM fondo")
        return cursor.fetchone()[0]

def gestion_fondos(request):
    fecha_actual = date.today()
    year = fecha_actual.year
    month = fecha_actual.month

    # Procesar formulario de REGISTRO (POST)
    if request.method == 'POST':
        form_registro = FondoForm(request.POST, allowed_month=month, allowed_year=year)  # Corregido
        if form_registro.is_valid():
            fondo = form_registro.save(commit=False)
            fondo.id_fondo = obtener_nuevo_id_fondo()
            fondo.save()
            return redirect('gestion-fondos')  # Recargamos la misma vista
    else:
        form_registro = FondoForm(allowed_month=month, allowed_year=year)  # Corregido

    # Procesar formulario de FILTRADO (GET)
    form_filtro = FechaFiltroForm(request.GET or None)
    fondos = Fondo.objects.exclude(ingresos=0, egresos=0)  # Inicializa con fondos válidos

    if form_filtro.is_valid():
        fecha_inicio = form_filtro.cleaned_data.get('fecha_inicio')
        fecha_fin = form_filtro.cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            fondos = fondos.filter(fecha_fondo__range=[fecha_inicio, fecha_fin])

    return render(request, 'gestion-fondos.html', {
        'form_registro': form_registro,
        'form_filtro': form_filtro,
        'fondos': fondos
    })

def obtener_nuevo_id_fondo():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(id_fondo), 0) + 1 FROM fondo")
        return cursor.fetchone()[0]

def obtener_saldo_actual(mes, anio, moneda):
    fondo_mas_reciente = Fondo.objects.filter(
        fecha_fondo__year=anio,
        fecha_fondo__month=mes,
        moneda_fondo=moneda
    ).order_by('-fecha_fondo').first()  # Orden descendente por fecha

    return fondo_mas_reciente.saldo_fondo if fondo_mas_reciente else 0


def gestion_fondos(request):
    if request.method == 'POST':
        form_registro = FondoForm(request.POST)
        if form_registro.is_valid():
            fondo_nuevo = form_registro.save(commit=False)
            mes = fondo_nuevo.fecha_fondo.month
            anio = fondo_nuevo.fecha_fondo.year
            moneda = fondo_nuevo.moneda_fondo  

            fondo_existente = Fondo.objects.filter(
                fecha_fondo__year=anio,
                fecha_fondo__month=mes,
                moneda_fondo=moneda
            ).first()

            if fondo_existente:
                # Si existe, actualizar ingresos, egresos y saldo
                fondo_existente.ingresos += fondo_nuevo.ingresos
                fondo_existente.egresos += fondo_nuevo.egresos
                fondo_existente.saldo_fondo = (fondo_existente.saldo_fondo + 
                                               fondo_nuevo.ingresos - fondo_nuevo.egresos)
                fondo_existente.save()
            else:
                fondo_nuevo.id_fondo = obtener_nuevo_id_fondo()
                saldo_actual = obtener_saldo_actual(mes, anio, moneda)
                fondo_nuevo.saldo_fondo = saldo_actual + fondo_nuevo.ingresos - fondo_nuevo.egresos
                fondo_nuevo.save()

            return redirect('gestion_fondos')  # Recargar la vista
    else:
        form_registro = FondoForm()

    # Procesar formulario de FILTRADO (GET)
    form_filtro = FechaFiltroForm(request.GET or None)
    fondos = Fondo.objects.exclude(ingresos=0, egresos=0)  # Excluir fondos sin movimiento

    if form_filtro.is_valid():
        fecha_inicio = form_filtro.cleaned_data.get('fecha_inicio')
        fecha_fin = form_filtro.cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            fondos = fondos.filter(fecha_fondo__range=[fecha_inicio, fecha_fin]).order_by('fecha_fondo')

    return render(request, 'gestion-fondos.html', {
        'form_registro': form_registro,
        'form_filtro': form_filtro,
        'fondos': fondos
    })

def reciboBase(request, year, month, day, nro_dpto):

    dpto = get_object_or_404(Dpto, id_dpto=nro_dpto)

    fechas = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    fecha_escrita = f'{fechas[month-1]}, {year}'

    if month < 12:
        mes_siguiente = fechas[month]
        mes_siguiente_nro = 1
        mes_siguiente_nro += month
        ano_siguiente = year
    else:
        mes_siguiente = fechas[0]
        mes_siguiente_nro = 1
        ano_siguiente = year+1

    asignacionPropietario = Asignacion.objects.filter(
        id_dpto=dpto,
        fecha_inicio__lt=f"{ano_siguiente}-{mes_siguiente_nro}-{day}"  # Fecha menor al año dado
    ).order_by('-fecha_inicio').first()  # Ordenar por fecha descendente y tomar el más reciente

    propietario = asignacionPropietario.id_prop # al hacer esto, obtienes el objeto dpto como tal
    edif = dpto.id_edif  # igual aca

    recibo = get_object_or_404(Recibo, fecha_recibo__year=year, fecha_recibo__month=month)


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
        gastoFinaldl = f'{sum(sumaGastosdl)}$'

    apartamentos = Dpto.objects.all()
    dptosDeudores = []
    deudasTotales = []

    for apto in apartamentos:
        importesApto = Importe.objects.filter(id_dpto=apto.id_dpto, fecha_importe__lt=recibo.fecha_recibo)
        deudasApto = Deuda.objects.filter(id_dpto=apto.id_dpto, fecha_cta__lt=recibo.fecha_recibo)
        sumaImportesApto = []
        sumaDeudasApto = []
        for i in importesApto:
            sumaImportesApto.append(i.pago_dl)
        for i in deudasApto:
            sumaDeudasApto.append(i.deuda)
        aptosPagos = sum(sumaDeudasApto) - sum(sumaImportesApto)
        if aptosPagos != 0:
            dptosDeudores.append(apto)
            deudasTotales.append(aptosPagos)
        else:
            continue

    montoDeudasTotales = sum(deudasTotales)

    fondoActualdl = Fondo.objects.get(fecha_fondo__year=year, fecha_fondo__month=month, moneda_fondo='$')
    fondoActualbs = Fondo.objects.get(fecha_fondo__year=year, fecha_fondo__month=month, moneda_fondo='bs')
    sumaHipotetica = fondoActualdl.saldo_fondo + montoDeudasTotales
    
    if month > 1:
        mes_pasado_nro = month-1
        ano_pasado_nro = year
    else:
        mes_pasado_nro = 12
        ano_pasado_nro = year-1

    try:
        fondoAnteriordl = Fondo.objects.get(fecha_fondo__year=ano_pasado_nro, fecha_fondo__month=mes_pasado_nro, moneda_fondo='$')
        fondoAnteriorbs = Fondo.objects.get(fecha_fondo__year=ano_pasado_nro, fecha_fondo__month=mes_pasado_nro, moneda_fondo='bs')
        montoAnteriordl = f'{fondoAnteriordl.saldo_fondo}$'
        montoAnteriorbs = f'{fondoAnteriorbs.saldo_fondo} Bs.'
    except Fondo.DoesNotExist:
        montoAnteriordl = '-'
        montoAnteriorbs = '-'
    #aqui empieza lo de fondos
    fechaPasada = datetime.strptime(f'{year-1}-{month}-{day} 00:00:00', "%Y-%m-%d %H:%M:%S")


    ultimasDeudas = Deuda.objects.filter(id_dpto=nro_dpto, fecha_cta__lt=recibo.fecha_recibo).order_by('fecha_cta')
    ultimosImportes = Importe.objects.filter(id_dpto=nro_dpto, fecha_importe__lt=recibo.fecha_recibo).order_by('fecha_importe')
    ultimosImportesSeleccionados = Importe.objects.filter(id_dpto=nro_dpto, fecha_importe__lt=recibo.fecha_recibo, fecha_importe__gt=fechaPasada).order_by('fecha_importe')


    sumaSaldo = 0

    listaAdeudado = []

    iteradorGeneral = len(ultimasDeudas)
    iteradorDeudas = 0
    iteradorImportes = 0
    iteradorImportesViejo = 0

    while iteradorGeneral > 0:

        deuda_actual = ultimasDeudas[iteradorDeudas]
        
        # Procesar solo las deudas que no tengan detalle_deuda y sean mayores que fechaPasada
        if deuda_actual.detalle_deuda is None:
            if deuda_actual.fecha_cta > fechaPasada:
                if iteradorImportes < len(ultimosImportesSeleccionados):
                # Verificamos que la fecha de deuda coincida con la de los importes
                    if deuda_actual.fecha_cta.year == ultimosImportesSeleccionados[iteradorImportes].fecha_importe.year and deuda_actual.fecha_cta.month == ultimosImportesSeleccionados[iteradorImportes].fecha_importe.month:
                        # si hay mas de un importe en el mismo mes:
                        pago_actual = ultimosImportesSeleccionados[iteradorImportes].pago_dl
                        if iteradorImportes < len(ultimosImportesSeleccionados)-1:
                            while ultimosImportesSeleccionados[iteradorImportes].fecha_importe.year == ultimosImportesSeleccionados[iteradorImportes+1].fecha_importe.year and ultimosImportesSeleccionados[iteradorImportes].fecha_importe.month == ultimosImportesSeleccionados[iteradorImportes+1].fecha_importe.month:
                                iteradorImportes += 1
                                pago_actual += ultimosImportesSeleccionados[iteradorImportes].pago_dl

                        sumaSaldo += deuda_actual.deuda
                        sumaSaldo -= pago_actual
                        iteradorImportes += 1  # Solo se incrementa si hay coincidencia de fechas
                    else:
                        pago_actual = 0.00  # No hay pago correspondiente a esa deuda
                        sumaSaldo += deuda_actual.deuda
                else:
                    pago_actual = 0.00  # No hay pago correspondiente a esa deuda
                    sumaSaldo += deuda_actual.deuda

                listaAdeudado.append({
                    'fechaAdeudado': f'{fechas[deuda_actual.fecha_cta.month-1]} {deuda_actual.fecha_cta.year}',
                    'importeAdeudado': f'{pago_actual}$',
                    'deudaAdeudado': f'{deuda_actual.deuda}$',
                    'sumaAdeudado': f'{sumaSaldo}$'
                })
                iteradorDeudas += 1
            else: # si los importes son de antes de los 12 meses de interes por mostrar
                if deuda_actual.fecha_cta.year == ultimosImportes[iteradorImportesViejo].fecha_importe.year and deuda_actual.fecha_cta.month == ultimosImportes[iteradorImportesViejo].fecha_importe.month:
                    pago_actual = ultimosImportes[iteradorImportesViejo].pago_dl
                    # si hay mas de un importe en el mismo mes:
                    if iteradorImportesViejo < len(ultimosImportes)-1:
                        while ultimosImportes[iteradorImportesViejo].fecha_importe.year == ultimosImportes[iteradorImportesViejo+1].fecha_importe.year and ultimosImportes[iteradorImportesViejo].fecha_importe.month == ultimosImportes[iteradorImportesViejo+1].fecha_importe.month:
                            iteradorImportesViejo += 1
                            pago_actual += ultimosImportes[iteradorImportesViejo].pago_dl
                    sumaSaldo += deuda_actual.deuda
                    sumaSaldo -= pago_actual
                    iteradorImportesViejo += 1
                else:
                    sumaSaldo += deuda_actual.deuda
                iteradorDeudas += 1

        else:
            sumaSaldo += deuda_actual.deuda
            iteradorDeudas += 1

        iteradorGeneral -= 1

    if edif.foto_edif:
        foto_bytes = bytes(edif.foto_edif)
        foto_base64 = base64.b64encode(foto_bytes).decode('utf-8')
        from imghdr import what
        image_type = what(None, foto_bytes)
        foto_url = f"data:image/{image_type};base64,{foto_base64}" if image_type else None
    else:
        foto_url = None




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
        'dptosDeudores': dptosDeudores,
        'montoDeudasTotales': montoDeudasTotales,
        'fondoActualdl': fondoActualdl,
        'fondoActualbs': fondoActualbs,
        'sumaHipotetica': sumaHipotetica,
        'montoAnteriordl': montoAnteriordl,
        'montoAnteriorbs': montoAnteriorbs,
        'listaAdeudado': listaAdeudado,
        'foto_url': foto_url,
    })

def generarRecibo(request, year, month, day):
    fechas = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    fecha_recibida = date(year, month, day)
    fechaRecibidaLetra = f'{fechas[month]} de {year}'

    if month == 12:
        mes_siguiente = 1
        ano_siguiente = year + 1
    else:
        mes_siguiente = month + 1
        ano_siguiente = year

    fechaSiguienteLetra = f'{fechas[mes_siguiente]} de {ano_siguiente}'


    fecha_actual = date.today()
    form_presupuesto = PresupuestoForm(allowed_year=year, allowed_month=month)
    form_GastoDirecto = GastoDirectoForm(allowed_year=year, allowed_month=month)
    form_GastoAplicado = GastoAplicadoForm(allowed_year=year, allowed_month=month)
    form_fondo = FondoImprevistoForm()
    form_comentario = ComentarioForm()

    presupuestos = Presupuesto.objects.filter(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='previsto')
    monto_presupuestos = []
    for presupuesto in presupuestos:
        monto_presupuestos.append({'titulo': presupuesto.titulo_pres, 'monto': f'{presupuesto.monto_pres_dl}$'})
    
    gastosDirectos = Presupuesto.objects.filter(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='directo')
    monto_gastosDirectos = []
    for gastoDirecto in gastosDirectos:
        monto_gastosDirectos.append({'titulo': gastoDirecto.titulo_pres, 'monto': f'{gastoDirecto.monto_pres_dl}$'})

    gastos = Gasto.objects.filter(fecha_gasto__year=year, fecha_gasto__month=month)

    monto_gastos = []

    for gasto in gastos:
        if gasto.monto_gasto_bs == None and gasto.moneda_gasto == '$':
            monto_gastos.append({'titulo': gasto.titulo_gasto, 'monto': f'{gasto.monto_gasto_dl}$'})
        elif gasto.monto_gasto_dl == None and gasto.moneda_gasto == 'bs':
            monto_gastos.append({'titulo': gasto.titulo_gasto, 'monto': f'{gasto.monto_gasto_bs} Bs.'})
        else:
            monto_gastos.append({'titulo': gasto.titulo_gasto, 'monto': f'{gasto.monto_gasto_bs} Bs. ({gasto.monto_gasto_dl}$)'})

    fondosImprevistos = Presupuesto.objects.filter(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='fondo')
    monto_fondo = []
    for fondo in fondosImprevistos:
        monto_fondo.append(f'{fondo.monto_pres_dl}$')



    try:
        fondoImprevisto = Presupuesto.objects.get(fecha_pres__year=year, fecha_pres__month=month, tipo_pres='fondo')
    except Presupuesto.DoesNotExist:
        fondoImprevisto = None

    if month > 1:
        mes_pasado_nro = month-1
        ano_pasado_nro = year
    else:
        mes_pasado_nro = 12
        ano_pasado_nro = year-1

# FALTA A LAS FECHAS MENORES


    if fecha_recibida > fecha_actual:
        raise Http404("La fecha ingresada es mayor a la fecha actual")
    try:
        fondodl = Fondo.objects.get(fecha_fondo__year=year, fecha_fondo__month=month, moneda_fondo='$')
        fondobs = Fondo.objects.get(fecha_fondo__year=year, fecha_fondo__month=month, moneda_fondo='bs')
    except Fondo.DoesNotExist:
        fondodl = fondobs = None
    comentarios = []
    try:
        recibo = Recibo.objects.get(fecha_recibo__year=year, fecha_recibo__month=month)
        comentariosFeos = Comentario.objects.filter(id_recibo=recibo)
        comentarios = ComentarioFrec.objects.filter(comentario__in=comentariosFeos)

    except Recibo.DoesNotExist:
        recibo = None
    try:
        fondoPasadodl = Fondo.objects.get(fecha_fondo__year=ano_pasado_nro, fecha_fondo__month=mes_pasado_nro, moneda_fondo='$')
        fondoPasadobs = Fondo.objects.get(fecha_fondo__year=ano_pasado_nro, fecha_fondo__month=mes_pasado_nro, moneda_fondo='bs')
    except Fondo.DoesNotExist:
        fondoPasadodl = fondoPasadobs = None
    
    if recibo == None:
        if request.method == 'POST':
            if 'CrearReciboYFondo' or 'CrearReciboYFondo0' in request.POST:
                print('peperoni mozarella')
                if 'CrearReciboYFondo' in request.POST:
                    montodl = fondoPasadodl.saldo_fondo
                    montobs = fondoPasadobs.saldo_fondo
                else:
                    montodl = 0
                    montobs = 0
                nuevoFondodl = Fondo(
                    moneda_fondo='$',
                    ingresos=0.00,
                    egresos=0.00,
                    saldo_fondo=montodl,
                    fecha_fondo=date(year, month, 1),
                    detalles_fondo=None  # Se guardará como NULL en la base de datos
                )
                nuevoFondobs = Fondo(
                    moneda_fondo='bs',
                    ingresos=0.00,
                    egresos=0.00,
                    saldo_fondo=montobs,
                    fecha_fondo=date(year, month, 1),
                    detalles_fondo=None  # Se guardará como NULL en la base de datos
                )
                nuevoFondodl.save()
                nuevoFondobs.save()
                nuevo_recibo = Recibo(
                    fecha_recibo=date(year, month, 1),  
                    id_fondo=nuevoFondodl,
                    monto_dl=0  
                )
                nuevo_recibo.save()
                url = reverse('generar_recibo', args=[year, month, 1])
                return redirect(url)

            elif 'CrearRecibo' in request.POST:
                nuevo_recibo = Recibo(
                    fecha_recibo=date(year, month, 1),  
                    id_fondo=fondodl,
                    monto_dl=0  
                )
                nuevo_recibo.save()
                url = reverse('generar_recibo', args=[year, month, 1])
                return redirect(url)

    if fondodl != None and recibo != None:
        # Procesar formulario de REGISTRO (POST)
        if request.method == 'POST':
            if 'agregarPresupuesto' in request.POST:
                form_presupuesto = PresupuestoForm(request.POST, allowed_year=year, allowed_month=month)
                if form_presupuesto.is_valid():
                    presupuestoFinal = form_presupuesto.save(commit=False)
                    presupuestoFinal.id_recibo = recibo
                    presupuestoFinal.tipo_pres = 'previsto'
                    presupuestoFinal.moneda_pres = '$'

                    presupuestoFinal.save()

                    #
                    #SE DEBERIA PODER AGREGAR DEUDAS, ESTO PARA SPRINT4
                    #
                    url = reverse('generar_recibo', args=[year, month, 1])
                    return redirect(url)
                
            elif 'agregarGastoDirecto' in request.POST:
                form_GastoDirecto = GastoDirectoForm(request.POST, allowed_year=year, allowed_month=month)
                if form_GastoDirecto.is_valid():
                    gastoDirectoFinal = form_GastoDirecto.save(commit=False)
                    gastoDirectoFinal.id_recibo = recibo
                    gastoDirectoFinal.tipo_pres = 'directo'
                    gastoDirectoFinal.moneda_pres = '$'

                    gastoDirectoFinal.save()

                    url = reverse('generar_recibo', args=[year, month, 1])
                    return redirect(url)
                
            elif 'agregarGastoAplicado' in request.POST:
                form_GastoAplicado = GastoAplicadoForm(request.POST, allowed_year=year, allowed_month=month)
                if form_GastoAplicado.is_valid():
                    gastoAplicadoFinal = form_GastoAplicado.save(commit=False)
                    if gastoAplicadoFinal.moneda_gasto == '$':
                        gastoAplicadoFinal.id_fondo = fondodl
                    else:
                        gastoAplicadoFinal.id_fondo = fondobs

                    gastoAplicadoFinal.save()

                    url = reverse('generar_recibo', args=[year, month, 1])
                    return redirect(url)

            elif 'agregarFondoImprevisto' in request.POST:  # Validar el formulario correcto
                if fondoImprevisto != None:
                    fondoImprevisto.delete()
                form_fondo = FondoImprevistoForm(request.POST)  # Crear instancia del formulario
                fondoFinal = form_fondo.save(commit=False)
                fondoFinal.id_recibo = recibo  # Asegúrate de que 'recibo' esté definido
                fondoFinal.titulo_pres = 'FONDO PARA GASTOS IMPREVISTOS'
                fondoFinal.moneda_pres = '$'

                fecha = date(year, month, 1)
                fecha_con_hora = datetime.combine(fecha, datetime.min.time())
                fondoFinal.fecha_pres = fecha_con_hora  # Usar datetime, no timestamp
                fondoFinal.clasificacion_pres = 'fondo_imprevisto'
                fondoFinal.tipo_pres = 'fondo'
                fondoFinal.save()

                fondoImprevisto = fondoFinal
                url = reverse('generar_recibo', args=[year, month, day])
                return redirect(url)
                # Si no es POST, crear formulario vacío

            elif 'agregarComentario' in request.POST:
                form_comentario = ComentarioForm(request.POST)
                if form_comentario.is_valid():  # Corregido: Validar form_comentario
                    # Guardar el comentario en ComentarioFrec
                    comentarioFinal = form_comentario.save(commit=False)
                    comentarioFinal.titulo_comentario = 'Titulo, por definir luego'
                    comentarioFinal.save()  # Guardar el comentario en la base de datos

                    # Crear el conector en Comentario
                    comentarioConector = Comentario(
                        id_comentario=comentarioFinal,  # Asignar el objeto ComentarioFrec
                        id_recibo=recibo  # Asegúrate de que 'recibo' esté definido
                    )
                    comentarioConector.save()  # Guardar el conector en la base de datos

                    # Redireccionar dinámicamente
                    url = reverse('generar_recibo', args=[year, month, day])  # Usar variables dinámicas
                    return redirect(url)
            elif 'redirectVerRecibo' in request.POST:
                # Usar el nombre correcto de la URL y pasar los argumentos en el orden correcto
                url = reverse('reciboBase', args=[year, month, day, 11])  # 'reciboBase' es el nombre de la URL
                return redirect(url)
                
    return render(request, "generarRecibo.html", {
        'recibo': recibo,
        'fondodl': fondodl,
        'form_presupuesto': form_presupuesto,
        'monto_presupuestos': monto_presupuestos,
        'form_GastoDirecto': form_GastoDirecto,
        'monto_gastosDirectos': monto_gastosDirectos,
        'form_GastoAplicado': form_GastoAplicado,
        'monto_gastos': monto_gastos,
        'form_fondo': form_fondo,
        'monto_fondo': monto_fondo,
        'fondoImprevisto': fondoImprevisto,
        'form_comentario': form_comentario,
        'comentarios': comentarios,
        'fechaSiguienteLetra': fechaSiguienteLetra,
        'fechaRecibidaLetra': fechaRecibidaLetra,
    })
    
    
def preReciboBase(request):
    # se definen las variables iniciales
    recibosCrudos = Recibo.objects.all()
    recibos = []
    meses = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
    for i in recibosCrudos:
        recibos.append({'recibo': i, 'mes': meses[i.fecha_recibo.month]})
    dptoForm = DptoForm()
    if request.method == 'POST':
        dptoForm = DptoForm(request.POST)
        if 'redirect_recibo' in request.POST: #redirige al ver recibo de la fecha seleccionada
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            print(request.POST)
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            recibo_id = request.POST.get('recibo_id')
            recibo = Recibo.objects.get(id_recibo=recibo_id)
            year = recibo.fecha_recibo.year
            month = recibo.fecha_recibo.month
            day = recibo.fecha_recibo.day
            id_dpto = dptoForm['id_dpto'].value()
            return redirect('reciboBase', year, month, day, id_dpto) 

    return render(request, 'preRecibo.html', {
        'recibos': recibos,
        'meses': meses,
        'dptoForm': dptoForm,
    })


def preGenerarRecibo(request):
    fondos = Fondo.objects.filter(moneda_fondo='bs', ingresos=0.00, egresos=0.00)
    recibosCrudos = []
    for fondo in fondos:
        recibos = Recibo.objects.filter(
            fecha_recibo__year=fondo.fecha_fondo.year,
            fecha_recibo__month=fondo.fecha_fondo.month
        )
        if recibos.exists():  # Verificar si hay resultados
            recibosCrudos.append(recibos.first())  # Agregar el primer recibo encontrado
    recibos = []
    meses = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
    for i in recibosCrudos:
        recibos.append({'recibo': i, 'mes': meses[i.fecha_recibo.month]})
    if len(recibos) == 0:
        fecha_actual = date.today()
        return redirect('generar_recibo', fecha_actual.year, fecha_actual.month, fecha_actual.day)
    if request.method == 'POST':
        if 'redirect_recibo' in request.POST: #redirige al ver recibo de la fecha seleccionada
            recibo_id = request.POST.get('recibo_id')
            recibo = Recibo.objects.get(id_recibo=recibo_id)
            year = recibo.fecha_recibo.year
            month = recibo.fecha_recibo.month
            day = recibo.fecha_recibo.day
            return redirect('generar_recibo', year, month, day) 

    return render(request, 'preGenerarRecibo.html', {
        'recibos': recibos,
        'meses': meses,
    })