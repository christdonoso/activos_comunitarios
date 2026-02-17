from django.shortcuts import render
from apps.users.models import Usuario

# Create your views here.

def index(request):
    return render(request, 'registration/login.html')


def profile(request):
    if request.method == 'GET':
        usuario = Usuario.get_usuario(request)
        return render(request, 'profile.html', context={'usuario':usuario})
    else:
        usuario = Usuario.filter_usuario(request)
        
        return render(request, 'profile.html', context={'usuario':usuario})
    
