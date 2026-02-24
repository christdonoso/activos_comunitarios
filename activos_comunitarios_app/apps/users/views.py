from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages

from apps.users.models import Usuario

from utilities import tools

# Create your views here.


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


def edit_user(request, id):

    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':

        data = request.POST.copy()
        for junk in ['csrfmiddlewaretoken']:
            data.pop(junk, None)

        for k,v in data.items():
            setattr(usuario,k, v)
        
        usuario.user.email = request.POST.get('email')
        
        usuario.user.save()
        usuario.save()
        
        messages.success(request, f"Usuario {usuario.fullname} actualizado correctamente.")
        return redirect('manage_users')

    return render(request, 'edit_user.html', {
        'usuario': usuario,
        'user_types': Usuario.USER_TYPE 
    })


def manage_users(request):
    # 1. Capturar parámetros de búsqueda y filtro
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    
    # 2. Queryset base con 'select_related' para optimizar la DB
    usuarios_qs = Usuario.objects.select_related('user').all()

    # 3. Aplicar filtros lógicos
    if search_query:
        usuarios_qs = usuarios_qs.filter(
            Q(fullname__icontains=search_query) | 
            Q(rut__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    if type_filter:
        usuarios_qs = usuarios_qs.filter(user_type=type_filter)

    context = {
        'usuarios': usuarios_qs,
        'user_types': Usuario.USER_TYPE,
        'stats': {
            'total': Usuario.objects.count(),
            'activos': User.objects.filter(is_active=True).count(),
            'admins': Usuario.objects.filter(user_type='ADMIN').count(), # Ajusta según tus tipos
        }
    }
    return render(request, 'manage_users.html', context)


def toggle_user_status(request, user_id):

    target_user = get_object_or_404(User, id=user_id)
    
    # Evitar que un admin se desactive a sí mismo
    if request.user.id == target_user.id:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
        return redirect('manage_users')

    # Cambiamos el estado
    target_user.is_active = not target_user.is_active
    target_user.save()

    status_text = "activado" if target_user.is_active else "desactivado"
    messages.success(request, f"El usuario {target_user.usuario.fullname} ha sido {status_text}.")
    
    return redirect('manage_users')