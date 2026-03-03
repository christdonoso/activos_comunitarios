from django.db import models

# Create your models here.
    

class Cesfam(models.Model):
    nombre = models.CharField(max_length=200)
    codigo_deis = models.CharField(max_length=50, unique=True, blank=True,help_text="Código único del centro")
    direccion = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.nombre


class SectorTerritorial(models.Model):
    cesfam = models.ForeignKey(Cesfam, on_delete=models.CASCADE, related_name='sectores')
    nombre = models.CharField(max_length=200)
    poblacion = models.IntegerField(default=0)
    color = models.CharField(max_length=7, default='#3b82f6')
    # Guardamos las coordenadas como JSON si no usas GeoDjango
    geojson = models.JSONField() 
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre