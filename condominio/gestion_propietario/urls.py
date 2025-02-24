from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.propietario_detail, name='propietario-detail'),
]
