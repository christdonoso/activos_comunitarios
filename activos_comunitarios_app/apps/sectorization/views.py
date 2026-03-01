from django.shortcuts import render
import json
from django.http import JsonResponse
from .models import SectorTerritorial
# Create your views here.


def create_sector(request):
    return render(request, 'sectorization/create_sector.html')


def save_sector(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            perfil = request.user.usuario
            
            # Creamos el registro en la DB
            nuevo_sector = SectorTerritorial.objects.create(
                cesfam=perfil.cesfam,
                nombre=data.get('nombre'),
                poblacion=data.get('poblacion') or 0,
                color=data.get('color'),
                geojson=data.get('geojson')
            )
            
            return JsonResponse({
                'status': 'success',
                'id': nuevo_sector.id,
                'message': 'Sector guardado correctamente'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# views.py

def delete_sector(request, id):
    if request.method == 'DELETE':
        try:
            # Solo permitimos borrar sectores que pertenezcan al CESFAM del usuario
            perfil = request.user.usuario
            sector = SectorTerritorial.objects.get(id=id, cesfam=perfil.cesfam)
            sector.delete()
            return JsonResponse({'status': 'success'})
        except SectorTerritorial.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sector no encontrado'}, status=404)


def update_sector(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        sector = SectorTerritorial.objects.get(id=id, cesfam=request.user.usuario.cesfam)
        sector.geojson = data.get('geojson')
        sector.save()
        return JsonResponse({'status': 'updated'})
