from django.db import models

class dpto(models.Model):
    id_dpto = models.CharField(primary_key=True)
    alicuota = models.DecimalField(max_digits=4, decimal_places=2)
    id_edif = models.IntegerField()

    def __str__(self):
        return f"Dpto: {self.id_dpto}"

    class Meta:
        db_table = 'dpto'
        managed = False
    

class importe(models.Model):

    class IdDptoChoices(models.TextChoices):
        DPTO_11 = "11"
        DPTO_12 = "12"
        DPTO_13 = "13"
        DPTO_21 = "21"
        DPTO_22 = "22"
        DPTO_23 = "23"
        DPTO_31 = "31"
        DPTO_32 = "32"

    # revisar si esta bien el null
    id_importe = models.IntegerField(primary_key=True, null=False)
    id_dpto = models.ForeignKey(dpto, choices=IdDptoChoices.choices, db_column='id_dpto', on_delete=models.CASCADE)
    id_fondo = models.IntegerField()
    fecha_importe = models.DateTimeField()
    pago_bs = models.DecimalField(max_digits=10, decimal_places=2)
    pago_dl = models.DecimalField(max_digits=10, decimal_places=2)

    
    class Meta:
        db_table = 'importe'
        managed = False
    

    def __str__(self):
        return f"Dpto: {self.nro_dpto.nro_dpto} - Fecha: {self.fecha}"

