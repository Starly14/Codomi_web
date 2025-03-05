from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

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


class Fondo(models.Model):
    MONEDA_CHOICES = [
        ('$', 'Dólares ($)'),
        ('bs', 'Bolivares (Bs. S)'),
    ]
    


    id_fondo = models.IntegerField(primary_key=True)
    moneda_fondo = models.CharField(max_length=10, choices=MONEDA_CHOICES)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    egresos = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    saldo_fondo = models.DecimalField(max_length=30, decimal_places=2, max_digits=30)
    fecha_fondo = models.DateTimeField()
    detalles_fondo = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'fondo'
        managed = False

class Recibo(models.Model):
    id_recibo = models.IntegerField(primary_key=True)
    fecha_recibo = models.DateTimeField()
    id_fondo = models.ForeignKey(Fondo, db_column="id_fondo", on_delete=models.CASCADE)
    monto_dl = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'recibo'
        managed = False

class Presupuesto(models.Model):
    id_pres = models.IntegerField(primary_key=True)
    id_recibo = models.ForeignKey(Recibo, db_column="id_recibo", on_delete=models.CASCADE)
    titulo_pres = models.CharField(max_length=100)
    detalle_pres = models.CharField(max_length=255)
    monto_pres_bs = models.DecimalField(decimal_places=2, max_digits=30) # REVISAR LOS DIGITOS MAXIMOS
    monto_pres_dl = models.DecimalField(decimal_places=2, max_digits=30)
    fecha_pres = models.DateTimeField()
    clasificacion_pres = models.CharField() # POSIBLE GENERACION DE CHOICES
    tipo_pres = models.CharField()

    class Meta:
        db_table = 'presupuesto'
        managed = False

class Gasto(models.Model):
    id_gasto = models.IntegerField(primary_key=True)
    id_fondo = models.ForeignKey(Fondo, db_column="id_fondo", on_delete=models.CASCADE)
    titulo_gasto = models.CharField(max_length=100)
    detalle_gasto = models.CharField(max_length=255)
    monto_gasto_bs = models.DecimalField(max_digits=30, decimal_places=2)
    monto_gasto_dl = models.DecimalField(max_digits=30, decimal_places=2)
    moneda_gasto = models.CharField(max_length=1)
    fecha_gasto = models.DateTimeField()
    clasificacion_gasto = models.CharField() # Posible choices

    class Meta:
        db_table = 'gasto'
        managed = False
