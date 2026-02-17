from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ComunityAsset

from utilities import tools
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


def validate_assets(request):

    activos_pendientes = ComunityAsset.objects.filter(estado='pendiente')
    total_count = ComunityAsset.objects.filter(estado='pendiente').count()

    context = {
        'assets_pendientes': activos_pendientes,
        'total_count': total_count,
    }
    
    return render(request, 'comunity_assets/validate_assets.html', context)


def approved_assets(request):
    approved_assets = ComunityAsset.objects.filter(estado='aprobado')
    total_count = ComunityAsset.objects.filter(estado='aprobado').count()

    context = {
        'approved_assets': approved_assets,
        'total_count': total_count,
    }
    return render(request, 'comunity_assets/approved_assets.html', context)


def rejected_assets(request):
    # Traemos los activos rechazados, pre-cargando el historial ordenado por fecha descendente
    # y el usuario que lo aceptó/rechazó para evitar múltiples consultas.
    rejected_assets = ComunityAsset.objects.filter(estado='rechazado')\
        .select_related('aceptado_por')\
        .prefetch_related('historial')

    total_count = ComunityAsset.objects.filter(estado='aprobado').count()

    context = {
        'rejected_assets': rejected_assets,
        'total_count': total_count,
    }
    return render(request, 'comunity_assets/rejected_assets.html', context)


def process_asset_action(request):
    if request.method != 'POST':
        return redirect('validate_assets')

    activo_id = request.POST.get('asset_id')
    action = request.POST.get('action')
    activo = get_object_or_404(ComunityAsset, id=activo_id)
    
    # Usuario que realiza la acción (asumiendo relación request.user.usuario)
    validador = request.user.usuario

    # Mapeo de acciones a estados del modelo
    if action == 'approve':
        activo.cambiar_estado('aprobado', validador, "Validado mediante panel oficial.")
        messages.success(request, f"El activo '{activo.nombre}' ha sido aprobado exitosamente.")
        return redirect('validate_assets')

    elif action == 'reject':
        motivo = request.POST.get('motivo')
        if not motivo:
            messages.error(request, "Error: Debes proporcionar un motivo para rechazar la propuesta.")
            return redirect('validate_assets')
        
        activo.cambiar_estado('rechazado', validador, motivo)
        messages.warning(request, f"La propuesta '{activo.nombre}' ha sido rechazada.")
        return redirect('validate_assets')

    elif action == 'revert_to_pending':
        activo.cambiar_estado('pendiente', validador, "Re-evaluación solicitada desde el historial.")
        messages.info(request, f"El activo '{activo.nombre}' ha vuelto a la lista de pendientes.")
        return redirect('rejected_assets')

    return redirect('validate_assets')


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