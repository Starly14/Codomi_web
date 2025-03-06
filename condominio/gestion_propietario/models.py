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
    



#models para recibo:
#TAMBIEN ESTA PROPIETARIO
#TAMBIEN ESTA DPTO
#TAMBIEN ESTA ASIGNACION

class Fondo(models.Model):
    id_fondo = models.AutoField(primary_key=True)
    moneda_fondo = models.CharField(blank=True, null=True)
    egresos = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    ingresos = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    saldo_fondo = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    fecha_fondo = models.DateTimeField(blank=True, null=True)
    detalles_fondo = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fondo'


class Recibo(models.Model):
    id_recibo = models.AutoField(primary_key=True)
    fecha_recibo = models.DateTimeField(blank=True, null=True)
    id_fondo = models.ForeignKey(Fondo, models.DO_NOTHING, db_column='id_fondo')
    monto_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recibo'


class ReciboP(models.Model):
    id_recibo_p = models.AutoField(primary_key=True)
    id_recibo = models.ForeignKey(Recibo, models.DO_NOTHING, db_column='id_recibo')
    id_dpto = models.ForeignKey(Dpto, models.DO_NOTHING, db_column='id_dpto', blank=True, null=True)
    monto_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recibo_p'


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


class Importe(models.Model):
    id_importe = models.AutoField(primary_key=True)
    id_dpto = models.ForeignKey(Dpto, models.DO_NOTHING, db_column='id_dpto', blank=True, null=True)
    id_fondo = models.ForeignKey(Fondo, models.DO_NOTHING, db_column='id_fondo')
    fecha_importe = models.DateTimeField()
    pago_bs = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    pago_dl = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    moneda_gasto = models.CharField(blank=True, null=True)
    detalle_importe = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'importe'


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


