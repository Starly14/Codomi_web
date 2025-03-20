from django.db import models

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