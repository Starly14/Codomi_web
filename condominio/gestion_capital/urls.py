from django.urls import path
from . import views

urlpatterns = [
    path("gestion_capital/", views.gestion_capital),
   path('importes/', views.vista_con_filtro, name='importe_list')
  ]
