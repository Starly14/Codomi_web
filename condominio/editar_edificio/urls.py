from django.urls import path
from . import views

urlpatterns = [
    path('<int:id_edif>/', views.editar_edificio, name='editar_edificio')
]