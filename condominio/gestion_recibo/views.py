from django.shortcuts import render, redirect
from django.db import connection

from .forms import FondoForm, MesAnioFiltroForm, FechaFiltroForm
from .models import Fondo, Gasto, Presupuesto
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

