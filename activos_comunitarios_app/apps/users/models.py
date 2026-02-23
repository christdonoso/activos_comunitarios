from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Usuario(models.Model):

    USER_TYPE = [
        ('COLAB','Colaborador'),
        ('ADMIN', 'Administrador'),
        ('PROF','Profesional')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=50)
    rut = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=[('F', 'Femenino'), ('M', 'Masculino'), ('O', 'Otro')], null=True, blank=True)
    phone = models.CharField(max_length=50)
    #profile_image = models.ImageField(null=True, blank=True, upload_to='images/')
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=150)
    region = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
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