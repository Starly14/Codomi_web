from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/editarPropietario', views.propietario_detail, name='propietario-detail'),
    path('registrarPropietario/', views.registrarPropietarioView, name='registrarPropietario'),
    path('plantilla/', views.plantillaBase, name='plantillaBase'),
]
