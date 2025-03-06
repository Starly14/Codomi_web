from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# Use static() to add URL mapping to serve static files during development (only)
from django.conf.urls.static import static

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
    path('', include("homepage.urls")),
    path("iniciarSesion/", include("iniciarSesion.urls")),
    path('gestion_propietario/', include('gestion_propietario.urls')),
    path('gestion_capital/', include('gestion_capital.urls')),
    path('editar_edificio/', include('editar_edificio.urls')),
    
    ] + static(settings.STATIC_URL)

#Para el manejo de imágenes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)