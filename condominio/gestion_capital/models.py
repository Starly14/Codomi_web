from django.db import models
from django.core.validators import MinValueValidator

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
    # id_fondo = models.IntegerField()
    fecha_importe = models.DateTimeField()
    pago_bs = models.DecimalField(max_digits=10, decimal_places=2)
    pago_dl = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'importe'
        managed = False
    
    def __str__(self):
        return f"Dpto: {self.nro_dpto.nro_dpto} - Fecha: {self.fecha}"
    
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
    
class Deuda(models.Model):
    id_deuda = models.AutoField(primary_key=True)
    id_dpto = models.ForeignKey('Dpto', models.DO_NOTHING, db_column='id_dpto', blank=True, null=True)
    fecha_cta = models.DateTimeField()
    deuda = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    detalle_deuda = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deuda'

    def __str__(self):
        return f"dpto: {self.id_dpto.id_dpto}. Deuda: {self.deuda}. {self.fecha_cta}"
    

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
