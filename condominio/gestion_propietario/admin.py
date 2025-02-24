from django.contrib import admin

# Register your models here.

from .models import Propietario, Dpto, Asignacion, Correo

admin.site.register(Propietario)
admin.site.register(Dpto)
admin.site.register(Asignacion)
admin.site.register(Correo)
