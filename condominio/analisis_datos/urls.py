from django.urls import path
from . import views

urlpatterns = [
    path('', views.analisis_datos, name='analisis_datos'),
    path('todas_tasas/', views.api_consultar_todas_las_tasas, name='todas_tasas'),
    path('tasa_por_fecha/', views.api_consultar_tasa_por_fecha, name='tasa_por_fecha'),
    path('subir_tasa/', views.api_subir_nueva_tasa, name='subir_tasa'),
    path('ultima_tasa/', views.api_obtener_ultima_tasa, name='ultima_tasa'),
    path('rango_tasas/', views.api_consultar_rango_tasas, name='rango_tasas'),
    path('presupuestos_vs_gastos/', views.presupuestos_vs_gastos, name='comparar_estadistica'),
]