from django.urls import path
from . import views

urlpatterns = [
    path('presupuestos/<int:id_recibo>/', views.crear_presupuestos, name='crear_presupuestos'),
]
