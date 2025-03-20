from django.urls import path
from . import views

urlpatterns = [
    path("gestion_capital/", views.gestion_capital),
    path('importes/', views.vista_con_filtro, name='importe_list'),
    path('recibos/', views.historial_recibos, name="recibos"),
    path('estado_cuenta/', views.estado_cuenta, name='estado_cuenta'),
    path('consultar_fondo/', views.consultar_fondo, name='consultar_fondo'),
  ]
