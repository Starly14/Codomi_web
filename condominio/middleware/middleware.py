from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs que no requieren autenticación (usando reverse con namespace)
        excluded_urls = [
            reverse('iniciarSesion:login'),  # URL de la vista de login
        ]

        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated and request.path not in excluded_urls:
            return redirect('iniciarSesion:login')  # Redirigir a la página de login
            print(reverse('iniciarSesion:login'))  # Debería imprimir '/iniciarSesion/login/'

        response = self.get_response(request)
        return response