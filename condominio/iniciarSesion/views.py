from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirige al dashboard
        else:
            return render(request, "iniciarSesion/login.html", {"error": "Usuario o contraseña incorrectos"})
    
    return render(request, "iniciarSesion/login.html")

##@login_required
def dashboard_view(request):
    return render(request, "iniciarSesion/dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("login")