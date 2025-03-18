from django.urls import path
from . import views

urlpatterns = [
    path('', views.analisis_datos, name='analisis_datos')
]