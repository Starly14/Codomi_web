from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

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
    alicuota = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    id_edif = models.ForeignKey('Edif', models.DO_NOTHING, db_column='id_edif')

    class Meta:
        managed = False
        db_table = 'dpto'


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

class Fondo(models.Model):
    MONEDA_CHOICES = [
        ('$', 'Dólares ($)'),
        ('bs', 'Bolivares (Bs.)'),
    ]

    id_fondo = models.AutoField(primary_key=True)
    moneda_fondo = models.CharField(max_length=10, choices=MONEDA_CHOICES)
    ingresos = models.DecimalField(max_digits=30, decimal_places=2, validators=[MinValueValidator(0)])
    egresos = models.DecimalField(max_digits=30, decimal_places=2, validators=[MinValueValidator(0)])
    saldo_fondo = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    fecha_fondo = models.DateTimeField(blank=True, null=True)
    detalles_fondo = models.CharField(max_length=300, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'fondo'

    def __str__(self):
        return f"id_fondo: {self.id_fondo}. {self.fecha_fondo}   {self.moneda_fondo}"


class Recibo(models.Model):
    id_recibo = models.AutoField(primary_key=True)
    fecha_recibo = models.DateTimeField(blank=True, null=True)
    id_fondo = models.ForeignKey(Fondo, models.DO_NOTHING, db_column='id_fondo')
    monto_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recibo'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

class Edif(models.Model):
    id_edif = models.AutoField(primary_key=True)
    nombre_edif = models.CharField(max_length=255, blank=True, null=True)
    rif = models.CharField(max_length=10, blank=True, null=True)
    direccion_edif = models.CharField(max_length=255, blank=True, null=True)
    foto_edif = models.BinaryField(blank=True, null=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edif'


class Comentario(models.Model):
    id_comentario = models.ForeignKey('ComentarioFrec', models.DO_NOTHING, db_column='id_comentario')
    id_recibo = models.ForeignKey('Recibo', models.DO_NOTHING, db_column='id_recibo')
    id_com = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'comentario'


class ComentarioFrec(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    titulo_comentario = models.CharField(max_length=100, blank=True, null=True)
    desc_comentario = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comentario_frec'


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


class Gasto(models.Model):
    MONEDA_CHOICES = [
        ('$', 'Dólares ($)'),
        ('bs', 'Bolivares (Bs.)'),
    ]
    id_gasto = models.AutoField(primary_key=True)
    id_fondo = models.ForeignKey(Fondo, models.DO_NOTHING, db_column='id_fondo')
    titulo_gasto = models.CharField(max_length=100, blank=True, null=True)
    detalle_gasto = models.CharField(max_length=255, blank=True, null=True)
    monto_gasto_bs = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    monto_gasto_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    moneda_gasto = models.CharField(blank=True, null=True, choices=MONEDA_CHOICES)
    fecha_gasto = models.DateTimeField(blank=True, null=True)
    clasificacion_gasto = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gasto'


class Importe(models.Model):
    id_importe = models.AutoField(primary_key=True)
    id_dpto = models.ForeignKey(Dpto, models.DO_NOTHING, db_column='id_dpto', blank=True, null=True)
    id_fondo = models.ForeignKey(Fondo, models.DO_NOTHING, db_column='id_fondo')
    fecha_importe = models.DateTimeField()
    pago_bs = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    pago_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    moneda_importe = models.CharField(blank=True, null=True)
    detalle_importe = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'importe'

    def __str__(self):
        return f"dpto: {self.id_dpto.id_dpto}. Importe$: {self.pago_dl}. {self.fecha_importe}"


class Presupuesto(models.Model):
    MONEDA_CHOICES = [
        ('$', 'Dólares ($)'),
        ('bs', 'Bolivares (Bs.)'),
    ]
    TIPO_CHOICES = [
        ('previsto', 'Previsto'),
        ('directo', 'Directo'),
    ]
    id_pres = models.AutoField(primary_key=True)
    id_recibo = models.ForeignKey('Recibo', models.DO_NOTHING, db_column='id_recibo')
    titulo_pres = models.CharField(max_length=100, blank=True, null=True)
    detalle_pres = models.CharField(max_length=255, blank=True, null=True)
    monto_pres_bs = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    monto_pres_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    moneda_pres = models.CharField(blank=True, null=True, choices=MONEDA_CHOICES)
    fecha_pres = models.DateTimeField(blank=True, null=True)
    clasificacion_pres = models.TextField(blank=True, null=True)
    tipo_pres = models.TextField(blank=True, null=True, choices=TIPO_CHOICES)

    class Meta:
        managed = False
        db_table = 'presupuesto'


