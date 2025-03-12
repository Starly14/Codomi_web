from django.urls import path
from . import views

urlpatterns = [
    path('editarPropietario/<int:id>/', views.propietario_detail, name='propietario-detail'),
    path('registrarPropietario/', views.registrarPropietarioView, name='registrarPropietario'),
    path('plantilla/', views.plantillaBase, name='plantillaBase'),
]
