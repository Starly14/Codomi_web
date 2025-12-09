from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
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


class Gasto(models.Model):
    id_gasto = models.AutoField(primary_key=True)
    id_fondo = models.ForeignKey(Fondo, models.DO_NOTHING, db_column='id_fondo')
    titulo_gasto = models.CharField(max_length=100, blank=True, null=True)
    detalle_gasto = models.CharField(max_length=255, blank=True, null=True)
    monto_gasto_bs = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    monto_gasto_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    moneda_gasto = models.CharField(blank=True, null=True)
    fecha_gasto = models.DateTimeField(blank=True, null=True)
    clasificacion_gasto = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gasto'

class Recibo(models.Model):
    id_recibo = models.IntegerField(primary_key=True)
    fecha_recibo = models.DateTimeField()
    id_fondo = models.ForeignKey(Fondo, on_delete=models.CASCADE, db_column='id_fondo')
    monto_dl = models.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        db_table = 'recibo'
        managed = False

class Presupuesto(models.Model):
    id_pres = models.AutoField(primary_key=True)
    id_recibo = models.ForeignKey('Recibo', models.DO_NOTHING, db_column='id_recibo')
    titulo_pres = models.CharField(max_length=100, blank=True, null=True)
    detalle_pres = models.CharField(max_length=255, blank=True, null=True)
    monto_pres_bs = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    monto_pres_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    moneda_pres = models.CharField(blank=True, null=True)
    fecha_pres = models.DateTimeField(blank=True, null=True)
    clasificacion_pres = models.TextField(blank=True, null=True)
    tipo_pres = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'presupuesto'