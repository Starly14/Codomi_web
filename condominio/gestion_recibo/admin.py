from django.contrib import admin

# Register your models here.

from .models import Propietario, Dpto, Asignacion, Correo, Deuda, Importe, Fondo

admin.site.register(Propietario)
admin.site.register(Dpto)
admin.site.register(Asignacion)
admin.site.register(Correo)
admin.site.register(Deuda)
admin.site.register(Importe)
admin.site.register(Fondo)