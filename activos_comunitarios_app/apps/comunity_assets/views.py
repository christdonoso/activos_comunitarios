from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ComunityAsset

# Create your views here.


def add_assets(request):
    if request.method == 'POST':

        data = request.POST.copy()
        for junk in ['csrfmiddlewaretoken', 'address-search']:
            data.pop(junk, None)

        # 2. Lista de booleanos que esperamos
        bool_fields = [
            'requiere_inscripcion', 'accesibilidad_silla_ruedas', 'baño_accesible', 
            'accesibilidad_visual', 'estacionamiento_general', 'estacionamiento_discapacidad'
        ]

        try:
            nuevo_activo = ComunityAsset(**data.dict())

            for field in bool_fields:
                setattr(nuevo_activo, field, field in request.POST)

            nuevo_activo.creado_por = getattr(request.user, 'usuario', None)
            nuevo_activo.save()
            
            messages.success(request, "¡Activo comunitario propuesto con éxito! tu propuesta aparecera en el mapa una vez sea aceptada por algun administrador!")
            return redirect('add_assets')

        except Exception as e:
            print(f"DEBUG: {e}")
            messages.error(request, "Error al procesar el formulario.")

    return render(request, 'comunity_assets/add_assets.html', {'ComunityAsset': ComunityAsset})


def asset_detail_validation(request, pk):
    asset = get_object_or_404(ComunityAsset, pk=pk)
    return render(request, "comunity_assets/asset_detail_validation.html", {
        "asset": asset
    })


def asset_detail(request, asset_id):

    asset = get_object_or_404(ComunityAsset, id=asset_id)
    context = {
        'asset': asset,
    }
    return render(request, 'comunity_assets/asset_detail.html', context)


def edit_asset(request, asset_id):

    asset = get_object_or_404(ComunityAsset, id=asset_id)
    
    if request.method == 'POST':

        # 1. Lista de campos que permitimos editar (Seguridad)
        editable_fields = [
            'nombre', 'tipo_activo', 'categoria_mais', 'direccion', 
            'region', 'comuna', 'horario', 'descripcion',
            'contacto_nombre', 'contacto_email', 'contacto_fono',
            'latitude', 'longitude', 'tipo_financiamiento', 'poblacion_objetivo'
        ]
        
        bool_fields = [
            'requiere_inscripcion', 'accesibilidad_silla_ruedas', 'baño_accesible', 
            'accesibilidad_visual', 'estacionamiento_general', 'estacionamiento_discapacidad'
        ]

        try:
            # 2. Actualizamos campos de texto/select (solo si vienen en el POST)
            for field in editable_fields:
                if field in request.POST:
                    value = request.POST.get(field).strip()
                    setattr(asset, field, value or None)

            # 3. Actualizamos booleanos (Lógica: Si está en POST es True, si no es False)
            for field in bool_fields:
                setattr(asset, field, field in request.POST)

            asset.save()
            
            messages.success(request, "Cambios guardados. El activo pasará a revisión.")
            return redirect('asset_detail', asset_id=asset.id)

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'comunity_assets/edit_asset.html', {'asset': asset})