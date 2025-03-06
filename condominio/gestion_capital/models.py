from django.db import models

class Dpto(models.Model):
    
    class IdDptoChoices(models.TextChoices):
        DPTO_11 = "11"
        DPTO_12 = "12"
        DPTO_13 = "13"
        DPTO_21 = "21"
        DPTO_22 = "22"
        DPTO_23 = "23"
        DPTO_31 = "31"
        DPTO_32 = "32"

    id_dpto = models.CharField(primary_key=True, choices=IdDptoChoices.choices)
    alicuota = models.DecimalField(max_digits=4, decimal_places=2)
    id_edif = models.IntegerField()

    def __str__(self):
        return f"Dpto: {self.id_dpto}"

    class Meta:
        db_table = 'dpto'
        managed = False


class Importe(models.Model):

    # revisar si esta bien el null
    id_importe = models.IntegerField(primary_key=True, null=False)
    id_dpto = models.ForeignKey(Dpto, db_column='id_dpto', on_delete=models.CASCADE)
    id_fondo = models.IntegerField()
    fecha_importe = models.DateTimeField()
    pago_bs = models.DecimalField(max_digits=10, decimal_places=2)
    pago_dl = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'importe'
        managed = False
    
    def __str__(self):
        return f"Dpto: {self.nro_dpto.nro_dpto} - Fecha: {self.fecha}"

class Recibo(models.Model):
    id_recibo = models.IntegerField(primary_key=True)
    fecha_recibo = models.DateTimeField()
    # id_fondo = models.ForeignKey()
    # monto_dl = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'recibo'
        managed = False

class Recibo_p(models.Model):
    id_recibo_p = models.IntegerField(primary_key=True)
    id_recibo = models.ForeignKey(Recibo, db_column='id_recibo', on_delete=models.CASCADE)
    id_dpto = models.ForeignKey(Dpto, db_column='id_dpto', on_delete=models.CASCADE)
    monto_dl = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'recibo_p'
        managed = False

class Propietario(models.Model):
    id_prop = models.AutoField(primary_key=True)
    nombre_prop = models.CharField(max_length=80)

    def __str__(self):
        return f"Propietario: {self.nombre_prop}"

    class Meta:
        db_table = 'propietario'
        managed = False

class Asignacion(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_prop = models.ForeignKey(Propietario, on_delete=models.CASCADE, db_column='id_prop', related_name='asignaciones')
    nro_dpto = models.ForeignKey(Dpto, on_delete=models.CASCADE, db_column='id_dpto', related_name='asignaciones')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'asignacion'
        managed = False

    def __str__(self):
        fecha_fin_str = f" Fecha fin: {self.fecha_fin}" if self.fecha_fin else ""
        return f"Propietario: {self.id_prop.nombre_prop} - Dpto: {self.nro_dpto.nro_dpto} Fecha inicio:{self.fecha_inicio}{fecha_fin_str}."
    
