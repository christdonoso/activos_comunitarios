from django.shortcuts import render
from ..comunity_assets.models import ComunityAsset
from django.http import JsonResponse
from ..social_recipe.models import Paciente
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
    print(assets_list)
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
    rut = request.GET.get('rut')
    print(rut)
    try:
        p = Paciente.objects.get(rut=rut)
        return JsonResponse({
            'success': True,
            'id': p.id,
            'nombre': p.nombre,
            'rut': p.rut,
            'edad': 67, # Aquí podrías calcular la edad real con la fecha de nacimiento
            'sector': p.sector,
            'direccion': p.direccion
        })
    except Paciente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Paciente no encontrado'}, status=404)
