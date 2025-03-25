from django.urls import path
from . import views

urlpatterns = [

    path('gestion_fondos/', views.gestion_fondos, name='gestion_fondos'),

    path('recibo/<int:year>/<int:month>/<int:day>/<str:nro_dpto>/', views.reciboBase, name='reciboBase'),

    path('recibo/', views.preReciboBase, name='preReciboBase'),

    path('generar_recibo/<int:year>/<int:month>/<int:day>/', views.generarRecibo, name='generar_recibo'),

    path('generar_recibo/', views.preGenerarRecibo, name='pre_generar_recibo'),

]
