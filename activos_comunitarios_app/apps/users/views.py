from django.shortcuts import render, redirect
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.contrib import messages

from apps.users.models import Usuario

from utilities import tools

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
    

def create_user(request):
    
    if request.method == 'POST':

            data = request.POST
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            rut = data.get('rut')

            try:
                with transaction.atomic():
                    # --- VALIDACIONES DE SERVIDOR ---
                    
                    # 1. Validar RUT (Algoritmo)
                    if not tools.validar_rut_chileno(rut):
                        raise ValueError("El RUT ingresado no es válido.")

                    # 2. Validar Unicidad de RUT (En el modelo Usuario)
                    if Usuario.objects.filter(rut=rut).exists():
                        raise ValueError("Este RUT ya se encuentra registrado.")

                    # 3. Validar Unicidad de Username
                    if User.objects.filter(username=username).exists():
                        raise ValueError("El nombre de usuario ya está en uso.")

                    # 4. Validar Unicidad de Email
                    if User.objects.filter(email=email).exists():
                        raise ValueError("Este correo electrónico ya está registrado.")

                    # --- INSERCIÓN DE DATOS ---
                    nuevo_user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email
                    )

                    Usuario.objects.create(
                        user=nuevo_user,
                        fullname=data.get('fullname'),
                        rut=rut,
                        email=email,
                        phone=data.get('phone'),
                        address=data.get('address'),
                        region=data.get('region'),
                        city=data.get('city'),
                        user_type=data.get('user_type')
                    )

                    messages.success(request, f"Usuario {username} creado exitosamente.")
                    return redirect('create_user')

            except ValueError as e:
                messages.error(request, str(e))

            except IntegrityError:
                messages.error(request, "Error de integridad: Posible dato duplicado.")

            except Exception as e:
                # Errores inesperados
                messages.error(request, "Ocurrió un error inesperado al procesar el registro.")
                print(f"Error: {e}") 

    # Si es GET o hubo error, volvemos al formulario
    context = {
        'user_types': Usuario.USER_TYPE
    }
    return render(request, 'create_user.html', context)