from django.db import models

class dpto(models.Model):
    id_dpto = models.CharField(primary_key=True)
    alicuota = models.DecimalField(max_digits=4, decimal_places=2)
    id_edif = models.IntegerField()

    def __str__(self):
        return f"Dpto: {self.nro_dpto}"

    class Meta:
        db_table = 'dpto'
        managed = False

class importe(models.Model):
    # revisar si esta bien el null
    id_importe = models.IntegerField(primary_key=True, null=False)
    id_dpto = models.ForeignKey(dpto, db_column='id_dpto', on_delete=models.CASCADE)
    id_fondo = models.IntegerField()
    fecha_importe = models.DateTimeField()
    pago_bs = models.DecimalField(max_digits=10, decimal_places=2)
    pago_dl = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'importe'
        managed = False

    def __str__(self):
        return f"Dpto: {self.nro_dpto.nro_dpto} - Fecha: {self.fecha}"

