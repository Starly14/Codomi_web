
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# Use static() to add URL mapping to serve static files during development (only)
from django.conf.urls.static import static

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
    path("iniciarSesion/", include("iniciarSesion.urls")),
    path('gestion_propietario/', include('gestion_propietario.urls')),
    path('gestion_capital/', include('gestion_capital.urls'))
    ] + static(settings.STATIC_URL)

