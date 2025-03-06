from django.urls import path
from . import views

urlpatterns = [
    path('presupuestos/<int:id_recibo>/', views.crear_presupuestos, name='crear_presupuestos'),

    path('reporte-mensual/', views.reporte_mensual, name='reporte_mensual'),

    path('gestion-fondos/', views.gestion_fondos, name='gestion-fondos'),
]
