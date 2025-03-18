from django.shortcuts import render

# Vista para renderizar analisis_datos.html
def analisis_datos(request):
    return render(request, 'analisis_datos.html')