from ..comunity_assets.models import ComunityAsset
from django.http import JsonResponse
from ..social_recipe.models import Paciente, SocialRecipe

from utilities import tools
# Create your views here.


def get_all_valid_assets(request):

    assets_db = ComunityAsset.objects.filter(estado='aprobado')
    assets_list = [
        {   
            'asset_id':asset.id,
            'name': asset.nombre,
            'lat': asset.latitude,
            'lng': asset.longitude,
            'description': asset.descripcion,
            'category':asset.tipo_activo
        }
        for asset in assets_db
    ]
    return JsonResponse({'assets': assets_list})


def get_assets_by_category(request):

    category = request.GET.get('category')

    assets_db = ComunityAsset.objects.filter(
        estado='aprobado',
        tipo_activo=category
    )

    assets_list = [
        {
            'asset_id': asset.id,
            'name': asset.nombre,
            'lat': asset.latitude,
            'lng': asset.longitude,
            'description': asset.descripcion,
            'category': asset.tipo_activo
        }
        for asset in assets_db
    ]

    return JsonResponse({'assets': assets_list})


def get_paciente(request):
    try:
        rut = request.GET.get('rut')
        p = Paciente.objects.get(rut=rut)
        return JsonResponse({
            'success': True,
            'id': p.id,
            'nombre': p.nombre,
            'rut': p.rut,
            'edad': tools.calcular_edad(p.fecha_nacimiento), # Aquí podrías calcular la edad real con la fecha de nacimiento
            'sector': p.sector,
            'direccion': p.direccion
        })
    except Paciente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Paciente no encontrado'}, status=404)
    

def get_social_recipe(request):

    # 1. Limpieza del RUT: eliminamos puntos, guiones y espacios
    rut_limpio = request.GET.get('rut').replace(".", "")
    print(rut_limpio)
    try:
        # 2. Buscamos al paciente por el RUT limpio
        paciente = Paciente.objects.get(rut=rut_limpio)
        
        # 3. Obtenemos la última receta emitida para este paciente
        # Usamos select_related para traer los datos del Activo de forma eficiente
        receta = SocialRecipe.objects.filter(paciente=paciente).select_related('activo').latest('fecha_emision')
        
        # 4. Mapeo de categorías: 
        # Tu modelo usa 'estres', pero el frontend usa 'promocion_estres'. 
        # Ajustamos esto aquí para que el JS active el filtro correcto.
        mapeo_frontend = {
            'estres': 'promocion_estres',
            'deporte': 'promocion_deporte',
            'social': 'participacion_social',
            'taller': 'promocion_taller',
        }
        
        categoria_front = mapeo_frontend.get(receta.activo.categoria_mais, 'otro')

        data = {
            "success": True,
            "paciente": {
                "nombre": paciente.nombre,
                "sector": paciente.sector or "No asignado",
            },
            "receta": {
                "codigo": receta.codigo_seguimiento,
                "objetivo": receta.objetivo_salud,
                "frecuencia": receta.frecuencia,
                "duracion": receta.duracion,
                "nombre_activo": receta.activo.nombre,
                "id_activo": receta.activo.id,
                "categoria_front": categoria_front, # El ID que el JS usará para filtrar
                "lat": receta.activo.latitude,
                "lng": receta.activo.longitude,
            }
        }
        return JsonResponse(data)

    except Paciente.DoesNotExist:
        return JsonResponse({
            "success": False, 
            "message": "El RUT ingresado no existe en nuestra base de datos de pacientes."
        }, status=404)
    
    except SocialRecipe.DoesNotExist:
        return JsonResponse({
            "success": False, 
            "message": "Paciente encontrado, pero no tiene una receta social asignada todavía."
        }, status=404)
        
    except Exception as e:
        # Captura errores inesperados para que la app no se caiga
        return JsonResponse({
            "success": False, 
            "message": "Error interno del servidor al procesar la solicitud."
        }, status=500)
