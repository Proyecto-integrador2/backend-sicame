from django.db import models
from django.contrib.postgres.fields import ArrayField
import pickle

# Create your models here.

class Empleado(models.Model):
    empleado_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    cargo = models.CharField(max_length=100)
    caracteristicas_faciales = models.BinaryField()

    def set_caracteristicas_faciales(self, encoding):
        """Guarda el encoding serializado."""
        self.caracteristicas_faciales = pickle.dumps(encoding)

    def get_caracteristicas_faciales(self):
        """Recupera el encoding deserializado."""
        return pickle.loads(self.caracteristicas_faciales)

    def __str__(self):
        return f"{self.nombre} ({self.cargo})"


class Asistencia(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField(auto_now_add=True)
    hora_entrada = models.TimeField(blank=True, null=True)
    hora_salida = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"Asistencia de {self.empleado.nombre} - {self.fecha}"


class Emocion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='emociones')
    asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE, related_name='emociones')
    emocion_registrada = models.CharField(max_length=50)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(default="Sin observaciones")

    def __str__(self):
        return f"{self.emocion_registrada} - {self.empleado.nombre} ({self.fecha_hora})"
