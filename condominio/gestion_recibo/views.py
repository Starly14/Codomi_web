from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection

from .forms import FondoForm, MesAnioFiltroForm, FechaFiltroForm
from .models import Fondo, Gasto, Presupuesto, Dpto, Asignacion, Recibo, Deuda, Comentario, Importe
from django.db.models import Sum
from datetime import datetime


# Para ser guardado en la BD se genera la prox PK disponible en la tabla
def obtener_nuevo_id_fondo():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(id_fondo), 0) + 1 FROM fondo")
        return cursor.fetchone()[0]

def gestion_fondos(request):
    # Procesar formulario de REGISTRO (POST)
    if request.method == 'POST':
        form_registro = FondoForm(request.POST)
        if form_registro.is_valid():
            fondo = form_registro.save(commit=False)
            fondo.id_fondo = obtener_nuevo_id_fondo()
            fondo.save()
            return redirect('gestion-fondos')  # Recargamos la misma vista

    # Si no es POST, crear formulario vacío
    else:
        form_registro = FondoForm()

    # Procesar formulario de FILTRADO (GET)
    form_filtro = FechaFiltroForm(request.GET or None)
    fondos = Fondo.objects.all()

    if form_filtro.is_valid():
        fecha_inicio = form_filtro.cleaned_data.get('fecha_inicio')
        fecha_fin = form_filtro.cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            fondos = fondos.filter(fecha_fondo__range=[fecha_inicio, fecha_fin])
    
    fondos = Fondo.objects.exclude(ingresos=0, egresos=0)

    return render(request, 'gestion-fondos.html', {
        'form_registro': form_registro,
        'form_filtro': form_filtro,
        'fondos': fondos
    })

def reporte_mensual(request):
    form = MesAnioFiltroForm(request.GET)
    gastos = Gasto.objects.none()
    presupuestos = Presupuesto.objects.none()
    ingresos = Fondo.objects.none()
    egresos = Fondo.objects.none()
    total_ingresos = 0
    total_egresos = 0

    if form.is_valid():
        mes = form.cleaned_data['mes']
        anio = form.cleaned_data['anio']
        gastos = Gasto.objects.filter(fecha_gasto__year=anio, fecha_gasto__month=mes)
        presupuestos = Presupuesto.objects.filter(fecha_pres__year=anio, fecha_pres__month=mes)
        ingresos = Fondo.objects.filter(fecha_fondo__year=anio, fecha_fondo__month=mes, ingresos__gt=0)
        egresos = Fondo.objects.filter(fecha_fondo__year=anio, fecha_fondo__month=mes, egresos__gt=0)
        total_ingresos = ingresos.aggregate(Sum('ingresos'))['ingresos__sum'] or 0
        total_egresos = egresos.aggregate(Sum('egresos'))['egresos__sum'] or 0

    return render(request, 'reporte_mensual.html', {
        'form': form,
        'gastos': gastos,
        'presupuestos': presupuestos,
        'ingresos': ingresos,
        'egresos': egresos,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos
    })

def reciboBase(request, year, month, day, nro_dpto):

    dpto = get_object_or_404(Dpto, id_dpto=nro_dpto)

    # Filtrar asignaciones por el departamento y con fecha menor a `year`
    asignacion = Asignacion.objects.filter(
        id_dpto=dpto,
        fecha_inicio__lt=f"{year}-{month}-{day}"  # Fecha menor al año dado
    ).order_by('-fecha_inicio').first()  # Ordenar por fecha descendente y tomar el más reciente

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
    fondoAnteriordl = Fondo.objects.get(fecha_fondo__year=ano_pasado_nro, fecha_fondo__month=mes_pasado_nro, moneda_fondo='$')
    fondoAnteriorbs = Fondo.objects.get(fecha_fondo__year=ano_pasado_nro, fecha_fondo__month=mes_pasado_nro, moneda_fondo='bs')

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
        'fondoAnteriordl': fondoAnteriordl,
        'fondoAnteriorbs': fondoAnteriorbs,
        'listaAdeudado': listaAdeudado,
    })

def generarRecibo(request):
    return render(request, "generarRecibo.html")
