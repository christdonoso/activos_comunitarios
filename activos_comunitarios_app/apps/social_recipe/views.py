from django.shortcuts import render, redirect
from django.contrib import messages
from ..social_recipe.models import SocialRecipe, Paciente
from ..users.models import Usuario
from ..comunity_assets.models import ComunityAsset


# Create your views here.

def create_recipe(request):
    if request.method == 'POST':
        # 1. Recuperar IDs de los campos ocultos
        paciente_id = request.POST.get('paciente_id')
        activo_id = request.POST.get('activo_id')
        
        # 2. Obtener instancias
        try:
            paciente = Paciente.objects.get(id=paciente_id)
            activo = ComunityAsset.objects.get(id=activo_id)
            profesional = Usuario.get_usuario(request)
            
            # 3. Crear la receta
            nueva_receta = SocialRecipe.objects.create(
                paciente=paciente,
                profesional=profesional,
                activo=activo,
                objetivo_salud=request.POST.get('objetivo_salud'),
                frecuencia=request.POST.get('frecuencia'),
                duracion=request.POST.get('duracion'),
                notas_adicionales=request.POST.get('notas_adicionales')
            )
            
            messages.success(request, f"Receta {nueva_receta.codigo_seguimiento} generada con éxito.")
            return redirect('create_recipe') # Cambia esto a tu URL de destino
            
        except Exception as e:
            messages.error(request, f"Error al generar receta: {str(e)}")
            return redirect('create_recipe')

    # Si es GET: Cargar activos aprobados para el Step 2
    activos = ComunityAsset.objects.filter(estado='aprobado')

    return render(request, 'social_recipe/create_recipe.html', {'activos': activos })

