from django.db import models
from django.contrib.auth.models import User
from ..sectorization.models import Cesfam, SectorTerritorial
# Create your models here.



class Usuario(models.Model):

    USER_TYPE = [
        ('ADMIN', 'Administrador'),
        ('PROF','Profesional')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cesfam = models.ForeignKey(Cesfam, on_delete=models.SET_NULL, related_name='funcionarios', blank=True, null=True)
    sector = models.ForeignKey(SectorTerritorial, on_delete=models.SET_NULL, blank=True, null=True)
    fullname = models.CharField(max_length=50)
    rut = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=[('F', 'Femenino'), ('M', 'Masculino'), ('O', 'Otro')], null=True, blank=True)
    #profile_image = models.ImageField(null=True, blank=True, upload_to='images/')
    email = models.EmailField(max_length=50)
    city = models.CharField(max_length=150)
    user_type = models.CharField(max_length=15,choices = USER_TYPE)
    creater_at = models.DateField(auto_now_add=True, blank=True,null=True)
 
    def __str__(self):
        return self.fullname
    
    @staticmethod
    def get_usuario(request):
        user = request.user
        usuario = Usuario.objects.get(user = user)
        return usuario

    @staticmethod
    def filter_usuario(request):
        user = request.user
        usuario = Usuario.objects.filter(user = user)
        return usuario