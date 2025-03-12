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
    })

