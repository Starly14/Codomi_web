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

from django.shortcuts import render
from .models import Gasto
from collections import Counter
import pandas as pd

# Vista para renderizar el HTML principal
def analisis_datos(request):
    return render(request, 'analisis_datos.html')

# Vista: Consultar todas las tasas
def api_consultar_todas_las_tasas(request):
    tasas = consultar_todas_las_tasas()
    return JsonResponse(tasas, safe=False)

# Vista: Consultar tasa por fecha
def api_consultar_tasa_por_fecha(request):
    fecha = request.GET.get('fecha')
    if not fecha:
        return JsonResponse({'error': 'La fecha es requerida.'}, status=400)
    tasa = consultar_tasa_por_fecha(fecha)
    return JsonResponse({'tasa': tasa})

# Vista: Subir nueva tasa
def api_subir_nueva_tasa(request):
    if request.method == "POST":
        fecha = request.POST.get('fecha')
        tasa = request.POST.get('tasa')
        if not fecha or not tasa:
            return JsonResponse({'error': 'Fecha y tasa son requeridas.'}, status=400)
        mensaje = subir_nueva_tasa(fecha, tasa)
        return JsonResponse({'mensaje': mensaje})
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

# Vista: Obtener última tasa
def api_obtener_ultima_tasa(request):
    tasa = obtener_ultima_tasa()
    return JsonResponse({'tasa': tasa})

# Vista: Consultar rango de tasas
def api_consultar_rango_tasas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    if not fecha_inicio or not fecha_fin:
        return JsonResponse({'error': 'Ambas fechas son requeridas.'}, status=400)
    tasas = consultar_rango_tasas(fecha_inicio, fecha_fin)
    return JsonResponse(tasas, safe=False)
#################################################################

def obtener_rango_fechas_FONDO():
    
    fecha_min_fondo = Fondo.objects.aggregate(min_fecha=Min('fecha_fondo'))['min_fecha']
    fecha_max_fondo = Fondo.objects.aggregate(max_fecha=Max('fecha_fondo'))['max_fecha']
    
    return fecha_min_fondo, fecha_max_fondo

def obtener_promedios_rango2():
    fecha_min, fecha_max = obtener_rango_fechas_FONDO()
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
        # print("TODAS LAS TASAS POR MES")
        # print(promedios_por_mes)
        
        # Calcular el promedio para cada mes
        promedios_finales = {}
        for clave, valores in promedios_por_mes.items():
            promedios_finales[clave] = round((sum(valores) / len(valores)), 4)
        print("PROMEDIOS FINALES")
        print(promedios_finales)
        return promedios_finales

    return {}


def ingresos_vs_egresos(request): # COMPARANDO EL FONDO
    promedios_tasas = obtener_promedios_rango2()
    
  
    





def obtener_rango_fechas_PG():
    # Obtener la fecha más antigua y la más reciente de ambas tablas
    fecha_min_pres = Presupuesto.objects.aggregate(min_fecha=Min('fecha_pres'))['min_fecha']
    fecha_max_pres = Presupuesto.objects.aggregate(max_fecha=Max('fecha_pres'))['max_fecha']
    
    fecha_min_gasto = Gasto.objects.aggregate(min_fecha=Min('fecha_gasto'))['min_fecha']
    
    fecha_max_gasto = Gasto.objects.aggregate(max_fecha=Max('fecha_gasto'))['max_fecha']
    
    # Calcular el rango global
    fecha_min = min(fecha_min_pres, fecha_min_gasto)
    fecha_max = max(fecha_max_pres, fecha_max_gasto)

    return fecha_min, fecha_max

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
    # OBTENEMOS LOS PROMEDIOS FINALES
    promedios_tasas = obtener_promedios_rango()

    promedioDiciembreAdicional = float (promedio_tasa_mes(2024, 12))
    print("PROMEDIO DICIEMBRE ADICIONAL")  
    print(promedioDiciembreAdicional)

    promedios_tasas.update({(2024, 12): promedioDiciembreAdicional})

    print("PROMEDIOS TASAS PRESUPUESTOS VS GASTOS")
    print(promedios_tasas)
    presupuestos = (Presupuesto.objects
                    .annotate(mes=ExtractMonth('fecha_pres'), anio=ExtractYear('fecha_pres'))
                    .values('mes', 'anio') # AGRUPAMOS POR MES Y ANIO
                    .annotate(total_pres=Sum('monto_pres_dl')) # SE AÑADE EL TOTAL DE PRESUPUESTOS 
                    .order_by('anio', 'mes'))
    
    print("PRESUPUESTOS") 
    print(presupuestos)
    
    gastos = (
    Gasto.objects
        .annotate(mes=ExtractMonth('fecha_gasto'), anio=ExtractYear('fecha_gasto'))
        .values('mes', 'anio', 'monto_gasto_bs', 'monto_gasto_dl')
        .order_by('anio', 'mes')
    )

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
        'plot_div': plot_div
    }

    return render(request, 'presupuestos_vs_gastos.html', contexto)





def clasificacion(request):
    # Obtener todos los gastos
    gastos = Gasto.objects.all()

    # Procesar las clasificaciones
    clasificaciones = []
    for gasto in gastos:
        if gasto.clasificacion_gasto:
            # Dividir las clasificaciones por comas y agregarlas a la lista
            clasificaciones.extend(gasto.clasificacion_gasto.split(','))

    # Contar la frecuencia de cada clasificación
    frecuencia = Counter(clasificaciones)

    # Convertir a un DataFrame de Pandas para facilitar el manejo
    df = pd.DataFrame(frecuencia.items(), columns=['Clasificacion', 'Frecuencia'])

    # Pasar los datos a la plantilla
    context = {
        'clasificaciones': df['Clasificacion'].tolist(),
        'frecuencias': df['Frecuencia'].tolist(),
        }
    return render(request, 'clasificacion_torta.html', context)








'''
def conversion_dl(anio, mes, monto_bs, monto_dl):
    if monto_dl is not None:
        return monto_dl
    elif monto_bs is not None:
        promedio_tasa = promedio_tasa_mes(anio, mes)
        if promedio_tasa:
            promedio_tasa = Decimal(promedio_tasa)
            resultado = round(Decimal(monto_bs / promedio_tasa), 2)
            return resultado
    return 0

def presupuestos_vs_gastos(request):

    presupuestos = (Presupuesto.objects
                    .annotate(mes=ExtractMonth('fecha_pres'), anio=ExtractYear('fecha_pres'))
                    .values('mes', 'anio')
                    .annotate(total_pres=Sum('monto_pres_dl'))
                    .order_by('anio', 'mes'))
    
    print("PRESUPUESTOS")
    print(presupuestos)
    
    # Obtener totales agrupados por mes y año en Gasto (convertidos a dólares)
    gastos = (Gasto.objects
              .annotate(mes=ExtractMonth('fecha_gasto'), anio=ExtractYear('fecha_gasto'))
              .values('mes', 'anio', 'monto_gasto_bs', 'monto_gasto_dl'))
    
    print("GASTOS")
    print(gastos)

    # Convertir resultados en diccionarios para fácil acceso
    data_pres = {}
    for item in presupuestos:
        clave = (item['anio'], item['mes'])
        total_pres = item.get('total_pres', 0) or 0  # Maneja None o valores falsy
        if total_pres > 0:
            data_pres[clave] = total_pres
    
    print("DATA PRESUPUESTOS DICCIONARIO")
    print(data_pres)

    data_gastos = {}

    for item in gastos:
        anio = item['anio']
        mes = item['mes']
        monto_bs = item['monto_gasto_bs']
        monto_dl = item['monto_gasto_dl']
        monto_dolarizado = conversion_dl(anio, mes, monto_bs, monto_dl)
        print("MONTO DOLARIZADO")
        print(monto_dolarizado)

        if (anio, mes) not in data_gastos:
            data_gastos[(anio, mes)] = 0
        data_gastos[(anio, mes)] += monto_dolarizado

    # Unir las claves (mes, anio) de ambos conjuntos y ordenarlas
    keys = sorted(set(list(data_pres.keys()) + list(data_gastos.keys())))

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
        'plot_div': plot_div
    }
    
    return render(request, 'presupuestos_vs_gastos.html', contexto)
'''


    