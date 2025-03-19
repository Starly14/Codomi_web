from django.http import JsonResponse
from django.shortcuts import render
from .LogicaAPI import (consultar_todas_las_tasas, consultar_tasa_por_fecha,
                        subir_nueva_tasa, obtener_ultima_tasa, consultar_rango_tasas)

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