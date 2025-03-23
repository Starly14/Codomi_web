from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # Redirige al home
        else:
            return render(request, "iniciarSesion/login.html", {"error": "Usuario o contraseña incorrectos"})
    
    return render(request, "iniciarSesion/login.html")

##@login_required
#def home_view(request):
    #return render(request, "iniciarSesion/home.html")

def logout_view(request):
    logout(request)
    return redirect(reverse('iniciarSesion:login'))  # Usar reverse para obtener la URL