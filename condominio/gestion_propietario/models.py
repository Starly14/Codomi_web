from django.db import models

class Propietario(models.Model):
    id_prop = models.AutoField(primary_key=True)
    nombre_prop = models.CharField(max_length=80)

    def __str__(self):
        return f"Propietario: {self.nombre_prop}"

    class Meta:
        db_table = 'propietario'
        managed = False

class Dpto(models.Model):
    nro_dpto = models.IntegerField(primary_key=True)
    alicuota = models.DecimalField(max_digits=4, decimal_places=2)
    id_edif = models.IntegerField()

    def __str__(self):
        return f"Dpto: {self.nro_dpto}"

    class Meta:
        db_table = 'dpto'
        managed = False

class Asignacion(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_prop = models.ForeignKey(Propietario, on_delete=models.CASCADE, db_column='id_prop', related_name='asignaciones')
    nro_dpto = models.ForeignKey(Dpto, on_delete=models.CASCADE, db_column='nro_dpto', related_name='asignaciones')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'asignacion'
        managed = False

    def __str__(self):
        fecha_fin_str = f" Fecha fin: {self.fecha_fin}" if self.fecha_fin else ""
        return f"Propietario: {self.id_prop.nombre_prop} - Dpto: {self.nro_dpto.nro_dpto} Fecha inicio:{self.fecha_inicio}{fecha_fin_str}."
    
class Correo(models.Model):
    correo = models.EmailField(primary_key=True, unique=True)
    id_prop = models.ForeignKey('Propietario', on_delete=models.CASCADE, db_column='id_prop', related_name='correos')

    class Meta:
        managed = False
        db_table = 'correo'

    def __str__(self):
        return f"Propietario: {self.id_prop.nombre_prop} - correo: {self.correo}."