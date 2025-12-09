from django.http import JsonResponse
from django.shortcuts import render
from .LogicaAPI import (consultar_todas_las_tasas, consultar_tasa_por_fecha,
                        subir_nueva_tasa, obtener_ultima_tasa, consultar_rango_tasas, promedio_tasa_mes)

from .models import Gasto, Presupuesto, Fondo
import plotly.express as px
from django.db.models.functions import ExtractMonth, ExtractYear
import plotly.graph_objects as go
from plotly.offline import plot
from django.db.models import Sum
from decimal import Decimal
from django.db.models import Min, Max
from datetime import datetime
from .forms import FechaFiltroForm

from django.shortcuts import render
from .models import Gasto
from collections import Counter
import pandas as pd

from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime

from django.utils.timezone import make_aware

# Vista para renderizar el HTML principal
def analisis_datos(request):
    return render(request, 'analisis_datos.html')
#################################################################

def obtener_rango_fechas_fondo():
    fecha_min = Fondo.objects.aggregate(min_fecha=Min('fecha_fondo'))['min_fecha']
    fecha_max = Fondo.objects.aggregate(max_fecha=Max('fecha_fondo'))['max_fecha']
    return fecha_min, fecha_max


def ingresos_egresos_saldo(request):

    fecha_min, fecha_max = obtener_rango_fechas_fondo()

    if request.method == 'GET' and 'fecha_inicio' in request.GET and 'fecha_fin' in request.GET:
        form = FechaFiltroForm(request.GET)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
        else:
            fecha_inicio, fecha_fin = fecha_min, fecha_max
    else:
        form = FechaFiltroForm(initial={'fecha_inicio': fecha_min, 'fecha_fin': fecha_max})
        fecha_inicio, fecha_fin = fecha_min, fecha_max

    if fecha_fin.month == 12:
        next_month_year = fecha_fin.year + 1
        next_month = 1
    else:
        next_month_year = fecha_fin.year
        next_month = fecha_fin.month + 1

    fecha_fin_siguiente = fecha_fin.replace(year=next_month_year, month=next_month, day=1)

    print("FECHA FIN PARA CONSULTAR TASAS:")
    print(fecha_fin_siguiente)
    tasas = consultar_rango_tasas(fecha_inicio.strftime("%Y-%m-%d"), fecha_fin_siguiente.strftime("%Y-%m-%d"))
    
    promedios_tasas = {}
    if tasas:
        for tasa in tasas:
            fecha = datetime.strptime(tasa['fecha'], "%Y-%m-%d")
            anio, mes = fecha.year, fecha.month
            if (anio, mes) not in promedios_tasas:
                promedios_tasas[(anio, mes)] = []
            promedios_tasas[(anio, mes)].append(float(tasa['tasa']))
        
        for key, value in promedios_tasas.items():
            promedios_tasas[key] = round(sum(value) / len(value), 4)

    fondos = (Fondo.objects
              .filter(fecha_fondo__range=[fecha_inicio, fecha_fin])
              .annotate(mes=ExtractMonth('fecha_fondo'), anio=ExtractYear('fecha_fondo'))
              .exclude(ingresos=0, egresos=0)
              .values('mes', 'anio', 'moneda_fondo', 'ingresos', 'egresos', 'saldo_fondo')
              .order_by('anio', 'mes'))

    print("FONDOS 2024")
    for fondo in fondos:
        if fondo['anio'] == 2024:
            print(fondo)

    data_fondo = {}

    for fondo in fondos:
        anio, mes = fondo['anio'], fondo['mes']
        moneda = fondo['moneda_fondo']

        ingreso_dolarizado = float(fondo['ingresos'])
        egreso_dolarizado = float(fondo['egresos'])
        saldo_dolarizado = float(fondo['saldo_fondo'])

        if moneda == 'bs':
            tasa_promedio = promedios_tasas.get((anio, mes), 1)
            if tasa_promedio != 0:
                ingreso_dolarizado = round(float(fondo['ingresos']) / tasa_promedio, 2)
                egreso_dolarizado = round(float(fondo['egresos']) / tasa_promedio, 2)
                saldo_dolarizado = round(float(fondo['saldo_fondo']) / tasa_promedio, 2)
        else:
            ingreso_dolarizado = round(float(fondo['ingresos']), 2)
            egreso_dolarizado = round(float(fondo['egresos']), 2)
            saldo_dolarizado = round(float(fondo['saldo_fondo']), 2)

        if (anio, mes) not in data_fondo:
            data_fondo[(anio, mes)] = {'ingresos': 0, 'egresos': 0, 'saldo': 0}
        data_fondo[(anio, mes)]['ingresos'] += ingreso_dolarizado
        data_fondo[(anio, mes)]['egresos'] += egreso_dolarizado
        data_fondo[(anio, mes)]['saldo'] += saldo_dolarizado

    meses = []
    ingresos_values = []
    egresos_values = []
    saldo_values = []

    for (anio, mes), valores in sorted(data_fondo.items()):
        label = f"{mes:02d}/{anio}"
        meses.append(label)
        ingresos_values.append(valores['ingresos'])
        egresos_values.append(valores['egresos'])
        saldo_values.append(valores['saldo'])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=meses, y=ingresos_values, name='Ingresos (USD)', marker_color='green'))
    fig.add_trace(go.Bar(x=meses, y=egresos_values, name='Egresos (USD)', marker_color='red'))
    fig.add_trace(go.Scatter(x=meses, y=saldo_values, name='Saldo (USD)', mode='lines+markers', line=dict(color='blue')))

    fig.update_layout(
        title='Relación entre Ingresos, Egresos y Saldo del Edificio (USD)',
        xaxis_title='Mes/Año',
        yaxis_title='Monto en USD',
        barmode='group'
    )

    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    contexto = {'plot_div': plot_div, 'form': form}
    return render(request, 'ingresos_egresos_saldo.html', contexto)

def obtener_rango_fechas_PG():
    # Obtener la fecha más antigua y la más reciente de ambas tablas
    fecha_min_pres = Presupuesto.objects.aggregate(min_fecha=Min('fecha_pres'))['min_fecha']
    fecha_max_pres = Presupuesto.objects.aggregate(max_fecha=Max('fecha_pres'))['max_fecha']
    
    fecha_min_gasto = Gasto.objects.aggregate(min_fecha=Min('fecha_gasto'))['min_fecha']
    
    fecha_max_gasto = Gasto.objects.aggregate(max_fecha=Max('fecha_gasto'))['max_fecha']
    
    # Calcular el rango global
    fecha_min = min(fecha_min_pres, fecha_min_gasto)
    fecha_max = max(fecha_max_pres, fecha_max_gasto)

    if fecha_max.month == 12:
        next_month_year = fecha_max.year + 1
        next_month = 1
    else:
        next_month_year = fecha_max.year
        next_month = fecha_max.month + 1

    fecha_max_siguiente = fecha_max.replace(year=next_month_year, month=next_month, day=1)

    print("FECHA FIN PARA CONSULTAR TASAS:")
    print(fecha_max_siguiente)

    return fecha_min, fecha_max_siguiente

def obtener_promedios_rango():
    fecha_min, fecha_max = obtener_rango_fechas_PG()
    print("FECHA MIN OBTENER PROMEDIOS")
    print(fecha_min)

    print("FECHA MAX OBTENER PROMEDIOS")
    print(fecha_max)

    print("FECHAS CORRECTAS")

    # Convertir a cadenas para la consulta API
    fecha_inicio = fecha_min.strftime("%Y-%m-%d") # CONVERTIR A STRING
    fecha_fin = fecha_max.strftime("%Y-%m-%d") # CONVERTIR A STRING STRINGFROMTIME

    # CONSULTAMOS EL RANGO COMPLETO DE TASAS
    tasas = consultar_rango_tasas(fecha_inicio, fecha_fin)
    print("TASAS")
    print(tasas) # INVOCO LA API

    promedios_por_mes = {}
    if tasas: # SE VERIFICA QUE EXISTAN TASAS
        for tasa in tasas:
            fecha = datetime.strptime(tasa['fecha'], "%Y-%m-%d") # CONVERTIR A DATETIME
            # print(fecha)
            anio, mes = fecha.year, fecha.month
            if (anio, mes) not in promedios_por_mes:
                promedios_por_mes[(anio, mes)] = []
            promedios_por_mes[(anio, mes)].append(float(tasa['tasa'])) # PARA CADA MES Y AGNO ESPECIFICO SE AGREGAN LAS TASAS DE TODOS LOS DIAS DE ESE MES
        print("TODAS LAS TASAS POR MES")
        print(promedios_por_mes)
        
        # Calcular el promedio para cada mes
        promedios_finales = {}
        for clave, valores in promedios_por_mes.items():
            promedios_finales[clave] = round((sum(valores) / len(valores)), 4)
        print("PROMEDIOS FINALES")
        print(promedios_finales)
        return promedios_finales

    return {}

def presupuestos_vs_gastos(request):

    fecha_min, fecha_max = obtener_rango_fechas_PG()  

    if request.method == 'GET' and 'fecha_inicio' in request.GET and 'fecha_fin' in request.GET:
        form = FechaFiltroForm(request.GET)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_max = form.cleaned_data['fecha_fin']
            # En este caso, actualizamos los valores de fecha_min y fecha_max con los enviados por el usuario
            fecha_min = fecha_inicio
            fecha_max = fecha_max
        else:
            fecha_inicio, fecha_max = fecha_min, fecha_max
    else:
        form = FechaFiltroForm(initial={'fecha_inicio': fecha_min, 'fecha_fin': fecha_max})
        fecha_inicio, fecha_max = fecha_min, fecha_max
    promedios_tasas = obtener_promedios_rango()

    print("PROMEDIOS TASAS PRESUPUESTOS VS GASTOS")
    print(promedios_tasas)
    presupuestos = (Presupuesto.objects
                .filter(fecha_pres__range=[fecha_min, fecha_max])
                .annotate(mes=ExtractMonth('fecha_pres'), anio=ExtractYear('fecha_pres'))
                .values('mes', 'anio')
                .annotate(total_pres=Sum('monto_pres_dl'))
                .order_by('anio', 'mes'))
    
    print("PRESUPUESTOS") 
    print(presupuestos)
    
    gastos = (Gasto.objects
          .filter(fecha_gasto__range=[fecha_min, fecha_max])
          .annotate(mes=ExtractMonth('fecha_gasto'), anio=ExtractYear('fecha_gasto'))
          .values('mes', 'anio', 'monto_gasto_bs', 'monto_gasto_dl')
          .order_by('anio', 'mes'))

    print("GASTOS")
    print(gastos)

    data_gastos = {}

    for gasto in gastos:
        anio, mes = gasto['anio'], gasto['mes']

        if gasto['monto_gasto_dl'] != None:
            monto_dolarizado = float(gasto['monto_gasto_dl'])
        elif gasto['monto_gasto_bs'] != None and gasto['monto_gasto_dl'] == None:
            # LOGICA DE CONVERSION
            tasa_promedio = promedios_tasas.get((anio, mes), 1)  # SE TOMA EL PROMEDIO DE LA TASA PARA ESE AGNO Y MES
            #print("TASA PROMEDIO")
            #print(tasa_promedio)

            #print("MONTOS UN POCO RAROS EN BS")
            #print(gasto['monto_gasto_bs'])
            if tasa_promedio != 0:
                monto_dolarizado = round(float(gasto['monto_gasto_bs']) / tasa_promedio, 2)                   
                #print(monto_dolarizado)
          

        # Acumular el gasto dolarizado por mes/año
        if (anio, mes) not in data_gastos:
            data_gastos[(anio, mes)] = 0
        data_gastos[(anio, mes)] += monto_dolarizado

    # Convertir resultados de presupuestos a diccionario
    data_pres = {}

    for item in presupuestos:
        clave = (item['anio'], item['mes'])
        total_pres = item.get('total_pres', 0) or 0
        if total_pres > 0:
            data_pres[clave] = total_pres
            # No hay problema que sean decimales

    print("DATA PRESUPUESTO")
    print(data_pres)

    # Unir las claves (mes, anio) de ambos conjuntos y ordenarlas
    keys = sorted(set(data_pres.keys()).union(data_gastos.keys()))

    # Preparar listas para el gráfico
    meses = []
    presupuestos_values = []
    gastos_values = []

    for key in keys:
        anio, mes = key
        label = f"{mes:02d}/{anio}"
        meses.append(label)
        presupuestos_values.append(data_pres.get(key, 0))
        gastos_values.append(data_gastos.get(key, 0))

    # Crear el gráfico con Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=meses,
        y=presupuestos_values,
        name='Presupuestos (USD)',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=meses,
        y=gastos_values,
        name='Gastos (USD)',
        marker_color='red'
    ))
    fig.update_layout(
        title='Relación entre Presupuestos y Gastos en USD a lo largo de los meses',
        xaxis_title='Mes/Año',
        yaxis_title='Monto en USD',
        barmode='group'
    )

    # Obtener el código HTML del gráfico
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    contexto = {
        'plot_div': plot_div,
        'form': form
    }

    return render(request, 'presupuestos_vs_gastos.html', contexto)

def clasificacion(request):
    # Obtener parámetros de fechas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Consulta base
    gastos = Gasto.objects.all()
    
    # Aplicar filtros de fecha si existen
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            gastos = gastos.filter(fecha_gasto__range=[fecha_inicio, fecha_fin])
        except ValueError:
            # Si hay error en el formato de fecha, ignorar los filtros
            pass
    
    # Procesar clasificaciones
    clasificaciones = []
    for gasto in gastos:
        if gasto.clasificacion_gasto:
            clasificaciones.extend(gasto.clasificacion_gasto.split(','))
    
    frecuencia = Counter(clasificaciones)
    df = pd.DataFrame(frecuencia.items(), columns=['Clasificacion', 'Frecuencia'])
    
    context = {
        'clasificaciones': df['Clasificacion'].tolist(),
        'frecuencias': df['Frecuencia'].tolist(),
    }
    return render(request, 'clasificacion_torta.html', context)

def datos_grafica_gastos(request):
    # Obtener parámetros de fechas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Consulta base
    gastos = Gasto.objects.all()
    
    # Aplicar filtros de fecha si existen
    if fecha_inicio and fecha_fin:
        try:
            # Convertir a datetime con timezone
            fecha_inicio = make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            fecha_fin = make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            
            gastos = gastos.filter(fecha_gasto__range=[fecha_inicio, fecha_fin])
        except ValueError as e:
            print(f"Error al convertir fechas: {e}")
            return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    
    # Procesar clasificaciones
    clasificaciones = []
    for gasto in gastos:
        if gasto.clasificacion_gasto:
            # Limpiar espacios en blanco alrededor de las clasificaciones
            clasificaciones.extend([c.strip() for c in gasto.clasificacion_gasto.split(',')])
    
    # Contar frecuencias ignorando espacios
    frecuencia = Counter(clasificaciones)
    
    # Eliminar duplicados de espacios diferentes
    clasificaciones_limpias = list(frecuencia.keys())
    frecuencias_limpias = list(frecuencia.values())
    
    return JsonResponse({
        'clasificaciones': clasificaciones_limpias,
        'frecuencias': frecuencias_limpias,
    })


def intentoComparacion(request):
    Gastos = Gasto.objects.all()


    
    
    return render(request, 'intentoComparacion.html')
