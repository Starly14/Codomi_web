from django.urls import path
from . import views

urlpatterns = [
    path("gestion_capital/", views.gestion_capital),
]