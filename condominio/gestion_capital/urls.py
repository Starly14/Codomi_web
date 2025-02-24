from django.urls import path
from . import views
from .views import ImporteListView 

urlpatterns = [
    path("gestion_capital/", views.gestion_capital),
   path('importes/', ImporteListView.as_view(), name='importe_list')
  ]
