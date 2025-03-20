from django.urls import path
from . import views

urlpatterns = [

    path('reporte_mensual/', views.reporte_mensual, name='reporte_mensual'),

    path('gestion_fondos/', views.gestion_fondos, name='gestion_fondos'),

    path('recibo/<int:year>/<int:month>/<int:day>/<str:nro_dpto>/', views.reciboBase, name='reciboBase'),

    path('generar_recibo/<int:year>/<int:month>/<int:day>/', views.generarRecibo, name='generar_recibo'),

]
