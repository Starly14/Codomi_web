from django.urls import path
from . import views

urlpatterns = [
    path('<int:id_recibo>/presupuestos/', views.crear_presupuestos, name='crear_presupuestos'),
]
