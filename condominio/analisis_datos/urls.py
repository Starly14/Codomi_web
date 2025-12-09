from django.urls import path
from . import views

urlpatterns = [
    path('', views.analisis_datos, name='analisis_datos'),
    path('presupuestos_vs_gastos/', views.presupuestos_vs_gastos, name='comparar_estadistica'),
    path('ingresos_egresos_saldo/', views.ingresos_egresos_saldo, name='ingresos_egresos_saldo'),
    path('clasificacion/', views.clasificacion, name='clasificacion_torta'),
    path('datos-grafica-gastos/', views.datos_grafica_gastos, name='datos_grafica_gastos'),
]