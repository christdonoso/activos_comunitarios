from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages

from apps.users.models import Usuario
from apps.social_recipe.models import Paciente
from apps.sectorization.models import SectorTerritorial, Cesfam

from utilities import tools

# Create your views here.


def profile(request):
    if request.method == 'GET':
        usuario = Usuario.get_usuario(request)
        cesfams = Cesfam.objects.filter(city=request.user.usuario.city)
        return render(request, 'user/profile.html', context={'usuario':usuario,'cesfams': cesfams})
    else:
        usuario = Usuario.filter_usuario(request)
        
        return render(request, 'user/profile.html', context={'usuario':usuario})
    

def create_user(request):
    if request.method == 'POST':
        print(request.POST)
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        rut = data.get('rut')
        
        # Capturamos los IDs de las relaciones
        cesfam_id = data.get('cesfam')
        sector_id = data.get('sector')

        try:
            with transaction.atomic():
                # --- VALIDACIONES DE SERVIDOR ---
                if not tools.validar_rut_chileno(rut):
                    raise ValueError("El RUT ingresado no es válido.")

                if Usuario.objects.filter(rut=rut).exists():
                    raise ValueError("Este RUT ya se encuentra registrado.")

                if User.objects.filter(username=username).exists():
                    raise ValueError("El nombre de usuario ya está en uso.")

                if User.objects.filter(email=email).exists():
                    raise ValueError("Este correo electrónico ya está registrado.")

                # 1. Crear el usuario de autenticación de Django
                nuevo_user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )

                # 2. Crear el perfil de Usuario con los campos nuevos
                Usuario.objects.create(
                    user=nuevo_user,
                    fullname=data.get('fullname'),
                    rut=rut,
                    sexo=data.get('sexo'), 
                    email=email,
                    city= request.user.usuario.cesfam.city,
                    user_type=data.get('user_type'),
                    # Asignamos las instancias de los modelos relacionados
                    cesfam_id=cesfam_id if cesfam_id else None,
                    sector_id=sector_id if sector_id else None
                )

                messages.success(request, f"Usuario {username} creado exitosamente.")
                return redirect('create_user')

        except ValueError as e:
            messages.error(request, str(e))

        except IntegrityError as e:
            messages.error(request, "Error de integridad: Posible dato duplicado.")
            print(f"IntegrityError: {e}")

        except Exception as e:
            messages.error(request, "Ocurrió un error inesperado al procesar el registro.")
            print(f"Error: {e}")

    # Carga de datos para el formulario
    # Filtramos CESFAMs por la ciudad del administrador que crea el usuario
    cesfams = Cesfam.objects.filter(city=request.user.usuario.city)
    
    context = {
        'user_types': Usuario.USER_TYPE,
        'comuna_admin': request.user.usuario.city,
        'cesfams': cesfams
    }
    return render(request, 'user/create_user.html', context)


def edit_user(request, id):

    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        cesfam = Cesfam.objects.get(id=request.POST['cesfam'])
        data = request.POST.copy()
        for junk in ['csrfmiddlewaretoken','cesfam','sector']:
            data.pop(junk, None)

        for k,v in data.items():
            setattr(usuario,k, v)
        
        usuario.user.email = request.POST.get('email')
        usuario.cesfam = cesfam
        usuario.sector = usuario.cesfam.sectores.get(id=request.POST['sector'])

        
        usuario.user.save()
        usuario.save()
        
        messages.success(request, f"Usuario {usuario.fullname} actualizado correctamente.")
        return redirect('manage_users')
    
    cesfams = Cesfam.objects.filter(city=request.user.usuario.city)
    return render(request, 'user/edit_user2.html', context={
        'usuario': usuario,
        'user_types': Usuario.USER_TYPE ,
        'cesfams': cesfams
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
    return render(request, 'user/manage_users.html', context)


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


def create_paciente(request):
    if request.method == 'POST':

        lat = request.POST.get('latitud')
        lng = request.POST.get('longitud')

        sector_detectado = "Fuera de Rango"

        try:
            cesfam_funcionario = request.user.usuario.cesfam
        except AttributeError:
            return JsonResponse({'success': False, 'message': 'Usuario no vinculado a un CESFAM'})

        if lat and lng:
            lat, lng = float(lat), float(lng)
                    
                    # 3. Traer solo los sectores de ESTE CESFAM
            sectores = SectorTerritorial.objects.filter(cesfam=cesfam_funcionario)
                    
            for s in sectores:
                        # El campo geojson ya es un objeto gracias a JSONField
                poligono = s.geojson 
                        
                if poligono and tools.is_point_in_polygon(lat, lng, poligono):
                    sector_detectado = s
                    sector_nombre = s.nombre
                    break

        p = Paciente.objects.create(
            rut=request.POST.get('rut'),
            nombre=request.POST.get('nombre'),
            fecha_nacimiento=request.POST.get('fecha_nacimiento'),
            direccion=request.POST.get('direccion'),
            sector=sector_detectado,
            telefono=request.POST.get('telefono'),
            latitude=lat,  
            longitude=lng,
        )
        return JsonResponse({
            'success': True,
            'sector': sector_nombre,
            'paciente_nombre': p.nombre,
            'id': p.id
        })
    
    # Si es GET, capturamos el RUT de la URL si viene de la búsqueda fallida
    requested_rut = request.GET.get('rut', '')
    return render(request, 'user/create_paciente.html', {'requested_rut': requested_rut})