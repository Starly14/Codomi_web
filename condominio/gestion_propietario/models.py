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
    id_dpto = models.CharField(primary_key=True, max_length=5)
    alicuota = models.DecimalField(max_digits=4, decimal_places=2)
    id_edif = models.IntegerField()

    def __str__(self):
        return f"Dpto: {self.id_dpto}"

    class Meta:
        db_table = 'dpto'
        managed = False

class Asignacion(models.Model):
    id_prop = models.ForeignKey('Propietario', models.DO_NOTHING, db_column='id_prop')
    id_dpto = models.ForeignKey('Dpto', models.DO_NOTHING, db_column='id_dpto')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    id_asignacion = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'asignacion'
        managed = False

    def __str__(self):
        fecha_fin_str = f" Fecha fin: {self.fecha_fin}" if self.fecha_fin else ""
        return f"Propietario: {self.id_prop.nombre_prop} - Dpto: {self.id_dpto.id_dpto} Fecha inicio:{self.fecha_inicio}{fecha_fin_str}."
    
class Correo(models.Model):
    correo = models.EmailField(primary_key=True, unique=True)
    id_prop = models.ForeignKey('Propietario', on_delete=models.CASCADE, db_column='id_prop', related_name='correos')

    class Meta:
        managed = False
        db_table = 'correo'

    def __str__(self):
        return f"Propietario: {self.id_prop.nombre_prop} - correo: {self.correo}."