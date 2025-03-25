from django.shortcuts import render
from django.db.models import Sum, Max, F
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import EstadoCuentaFiltroForm, FondoFiltroForm

from .models import Deuda, Dpto, Importe, Fondo
 # permite mostrar una lista de objetos del modelo
from .models import Importe
from .filters import FiltroFecha

def vista_con_filtro(request):
    filtro = FiltroFecha(request.GET)
    # Queryset inicial (todos los query)
    queryset = Importe.objects.all()

    if filtro.is_valid(): # Verifica que la informacion proporcionada en el form es correcta
        queryset = filtro.qs
        contexto = {'filtro': filtro, 'queryset': queryset}

    return render(request, 'gestion_capital/importe_list.html', contexto)

def consultar_fondo(request):

    print("DATOS FORMULARIO")
    
    form = FondoFiltroForm(request.GET)
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1)
    inicio_mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)

    # Inicializar variables para mes y año
    mes = anio = None
    datos_mostrados = False  # Variable para controlar si mostrar datos

    # Validar el formulario
    if form.is_valid():
        mes = form.cleaned_data.get('mes')
        anio = form.cleaned_data.get('anio')

        # Validar que los campos no sean "----"
        if mes != "----" and anio != "----":
            datos_mostrados = True  

    # Calcular fechas de filtrado solo si mes y año son válidos
    if datos_mostrados:
        inicio_mes = timezone.make_aware(datetime(int(anio), int(mes), 1), timezone.get_current_timezone())
        if int(mes) == 12:
            fin_mes = timezone.make_aware(datetime(int(anio) + 1, 1, 1), timezone.get_current_timezone())
        else:
            fin_mes = timezone.make_aware(datetime(int(anio), int(mes) + 1, 1), timezone.get_current_timezone())
        
        # Establecer las fechas para el mes anterior
        inicio_mes_anterior = inicio_mes - timedelta(days=1)
        inicio_mes_anterior = inicio_mes_anterior.replace(day=1)  # Primer día del mes anterior
        fin_mes_anterior = inicio_mes  # Último día del mes anterior

    else:
        # Si no se han seleccionado mes y año, se muestra el mes actual
        inicio_mes = hoy.replace(day=1)
        fin_mes = hoy
        inicio_mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
        fin_mes_anterior = inicio_mes

    # Consultas para el mes seleccionado o actual
    fondos_actuales = Fondo.objects.filter(fecha_fondo__range=(inicio_mes, fin_mes))
    fondos_anteriores = Fondo.objects.filter(fecha_fondo__range=(inicio_mes_anterior, fin_mes_anterior))

    # Calcular saldos e ingresos/egresos para ambas monedas
    def calcular_totales(fondos):
        saldo_bs = fondos.filter(moneda_fondo='bs').aggregate(total=Sum('saldo_fondo'))['total'] or 0
        saldo_dl = fondos.filter(moneda_fondo='$').aggregate(total=Sum('saldo_fondo'))['total'] or 0
        ingresos_bs = fondos.filter(moneda_fondo='bs').aggregate(total=Sum('ingresos'))['total'] or 0
        ingresos_dl = fondos.filter(moneda_fondo='$').aggregate(total=Sum('ingresos'))['total'] or 0
        egresos_bs = fondos.filter(moneda_fondo='bs').aggregate(total=Sum('egresos'))['total'] or 0
        egresos_dl = fondos.filter(moneda_fondo='$').aggregate(total=Sum('egresos'))['total'] or 0
        return saldo_bs, saldo_dl, ingresos_bs, ingresos_dl, egresos_bs, egresos_dl



    if datos_mostrados:
        saldo_actual_bs, saldo_actual_dl, ingresos_actual_bs, ingresos_actual_dl, egresos_actual_bs, egresos_actual_dl = calcular_totales(fondos_actuales)
        saldo_anterior_bs, saldo_anterior_dl, ingresos_anterior_bs, ingresos_anterior_dl, egresos_anterior_bs, egresos_anterior_dl = calcular_totales(fondos_anteriores)

        print("DATOS FORMULARIO")
        print("formulario vaildo", form.is_valid())
        print("mes", mes)
        print("anio", anio) 

        contexto = {
            'form': form,
            'meses': form.fields['mes'].choices,
            'anios': form.fields['anio'].choices,
            'saldo_actual_bs': saldo_actual_bs,
            'saldo_actual_dl': saldo_actual_dl,
            'ingresos_actual_bs': ingresos_actual_bs,
            'ingresos_actual_dl': ingresos_actual_dl,
            'egresos_actual_bs': egresos_actual_bs,
            'egresos_actual_dl': egresos_actual_dl,
            'saldo_anterior_bs': saldo_anterior_bs,
            'saldo_anterior_dl': saldo_anterior_dl,
            'ingresos_anterior_bs': ingresos_anterior_bs,
            'ingresos_anterior_dl': ingresos_anterior_dl,
            'egresos_anterior_bs': egresos_anterior_bs,
            'egresos_anterior_dl': egresos_anterior_dl,
        }
    else:
        contexto = {
            'form': form,
            'meses': form.fields['mes'].choices,
            'anios': form.fields['anio'].choices,
        }

    return render(request, 'gestion_capital/consultar_fondo.html', contexto)


def estado_cuenta(request):
    # LLAMAMOS AL FORMULARIO PARA PREPARARLO PARA LA ENTRADA DEL USUARIO, SI LO DESEA
    form = EstadoCuentaFiltroForm(request.GET or None)
    # LISTA DE REPORTES PARA CADA DEPARTAMENTO
    reportes = []
    # LISTA DE DEPARTAMENTOS
    departamentos = []

    # DADO QUE NINGÚN CAMPO ES REQUERIDO, AL PRINCIPIO SE MOSTRARÁN TODOS LOS RESULTADOS
    if form.is_valid():
        # SE OBTIENEN MES, AÑO O DEPARTAMENTO SI SE DESEA
        filter_departamento = form.cleaned_data.get('departamento')
        filter_mes = form.cleaned_data.get('mes')
        filter_anio = form.cleaned_data.get('anio')

        # Si no se selecciona un departamento, usamos todos
        if filter_departamento:
            departamentos = [filter_departamento]
        else:
            departamentos = list(Dpto.objects.all())

        if filter_mes:
            filter_mes = int(filter_mes)
        if filter_anio:
            filter_anio = int(filter_anio)

        # CREACIÓN DE CADA REPORTE POR DEPARTAMENTO
        for dpto in departamentos:
            # Obtener pagos agrupados por mes y año
            importes_qs = (
                Importe.objects.filter(id_dpto=dpto)
                .annotate(mes=ExtractMonth('fecha_importe'), anio=ExtractYear('fecha_importe'))
                .values('mes', 'anio')
                .annotate(total_pago=Sum('pago_dl'), fecha_pago=Max('fecha_importe'))
                .order_by('anio', 'mes')
            )

            pago_dict = {
                (item['anio'], item['mes']): (item['total_pago'], item['fecha_pago'])
                for item in importes_qs
            }

            # Obtener deudas (excluyendo ajustes) agrupadas por mes y año
            deudas_qs = (
                Deuda.objects.filter(id_dpto=dpto)
                .exclude(detalle_deuda='ajuste')
                .annotate(mes=ExtractMonth('fecha_cta'), anio=ExtractYear('fecha_cta'))
                .values('mes', 'anio')
                .annotate(total_deuda=Sum('deuda'))
                .order_by('anio', 'mes')
            )

            deuda_dict = {
                (item['anio'], item['mes']): item['total_deuda']
                for item in deudas_qs
            }

            # Unir llaves de deuda y pago
            keys = set(deuda_dict.keys()) | set(pago_dict.keys())
            if filter_mes:
                keys = {(anio, mes) for (anio, mes) in keys if mes == filter_mes}
            if filter_anio:
                keys = {(anio, mes) for (anio, mes) in keys if anio == filter_anio}

            deuda_acumulada = 0
            reporte_dpto = []

            for anio, mes in sorted(keys):
                deuda = deuda_dict.get((anio, mes), 0)
                pago, fecha_pago = pago_dict.get((anio, mes), (0, None))

                saldo = deuda + deuda_acumulada - pago

                if saldo < 0:  # Pago mayor que la deuda total (actual + acumulada)
                    overpayment = abs(saldo)
                    deuda_acumulada = 0
                    saldo = 0

                    if fecha_pago:
                        # PARA QUE NO LLORE POR EL NAIVE
                        if timezone.is_naive(fecha_pago):
                            fecha_pago = timezone.make_aware(fecha_pago, timezone.get_current_timezone())

                        deuda_existente = Deuda.objects.filter(
                            id_dpto=dpto,
                            fecha_cta=fecha_pago,
                            deuda=overpayment,
                            detalle_deuda='ajuste'
                        ).exists()

                        if not deuda_existente:

                            print("CREANDO DEUDA")
                            Deuda.objects.create(
                                id_dpto=dpto,
                                fecha_cta=fecha_pago,
                                deuda=overpayment,
                                detalle_deuda='ajuste'
                            )
                else:
                    print("SALDO POSITIVO, QUEDO PELANDO")
                    deuda_acumulada = saldo

                reporte_dpto.append({
                    'anio': anio,
                    'mes': mes,
                    'alicuota': dpto.alicuota,
                    'deuda': deuda,
                    'pago': pago,
                    'saldo': saldo,
                    'deuda_acumulada': deuda_acumulada,
                })

            if len(reporte_dpto) > 0:
                reportes.append({
                    'departamento': dpto,
                    'reporte': reporte_dpto
                })
    if len(reportes) == 0:
        reportes = None
    return render(request, 'gestion_capital/estado_cuenta.html', {
        'form': form,
        'reportes': reportes
    })
