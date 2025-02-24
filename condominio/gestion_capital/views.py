from django.shortcuts import render

# Create your views here.
def gestion_capital(request):
    return render(request, "gestion_capital/gestionCapital.html")