from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..comunity_assets.models import ComunityAsset
# Create your views here.



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