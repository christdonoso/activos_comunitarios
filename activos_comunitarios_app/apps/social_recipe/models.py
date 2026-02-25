from django.db import models
import uuid

from apps.comunity_assets.models import ComunityAsset
from apps.users.models import Usuario
# Create your models here.


class Paciente(models.Model):
    rut = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

class SocialRecipe(models.Model):
    # Relaciones
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='recetas')
    profesional = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='recetas_emitidas')
    activo = models.ForeignKey(ComunityAsset, on_delete=models.CASCADE)
    
    # Detalles de la receta
    objetivo_salud = models.TextField()
    frecuencia = models.CharField(max_length=100)
    duracion = models.CharField(max_length=100)
    notas_adicionales = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_emision = models.DateTimeField(auto_now_add=True)
    codigo_seguimiento = models.CharField(max_length=12, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.codigo_seguimiento:

            self.codigo_seguimiento = str(uuid.uuid4().hex[:8].upper())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receta {self.codigo_seguimiento} - {self.paciente.nombre}"