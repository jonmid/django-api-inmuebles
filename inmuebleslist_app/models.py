from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from user_app.models import Account


class Empresa(models.Model):
  nombre = models.CharField(max_length=250)
  website = models.URLField(max_length=250)
  activo = models.BooleanField(default=True)
  
  def __str__(self):
    return self.nombre


class Inmueble(models.Model):
  direccion = models.CharField(max_length=250)
  pais = models.CharField(max_length=150)
  descripcion = models.CharField(max_length=500)
  imagen = models.CharField(max_length=900)
  avg_calificacion = models.FloatField(default=0)
  numero_calificacion = models.IntegerField(default=0)
  activo = models.BooleanField(default=True)
  created = models.DateTimeField(auto_now_add=True)
  # Relacion One to Many (Uno a muchos)
  empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='inmueblelist')
  
  def __str__(self):
    return self.direccion


class Comentario(models.Model):
  calificacion = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
  text = models.CharField(max_length=200, null=True)
  activo = models.BooleanField(default=True)
  created = models.DateTimeField(auto_now_add=True)
  update = models.DateTimeField(auto_now=True)
  # Relacion One to Many (Uno a muchos)
  inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name='comentarios')
  # comentario_user = models.ForeignKey(User, on_delete=models.CASCADE)
  comentario_user = models.ForeignKey(Account, on_delete=models.CASCADE)
  
  def __str__(self):
    return str(self.calificacion) + ' - ' + self.inmueble.direccion