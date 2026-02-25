from django.db import models
from apps.users.models import Usuario

from django.db import transaction


# Create your models here.


class ComunityAsset(models.Model):

    TIPO_ACTIVO_CHOICES = [
        ('espacio_publico', 'Espacio Público / Área Verde'),
        ('organizacion_social', 'Organización Social'),
        ('establecimiento_salud', 'Establecimiento de Salud'),
        ('establecimiento_educacional', 'Establecimiento Educacional'),
        ('organizacion_deportiva', 'Club Deportivo'),
        ('grupo_apoyo', 'Grupo de Apoyo'),
        ('programa_municipal', 'Programa Municipal'),
        ('centro_cultural', 'Centro Cultural / Biblioteca'),
        ('organizacion_adulto_mayor', 'Organización Adulto Mayor'),
        ('organizacion_juvenil', 'Organización Juvenil'),
        ('red_vecinal', 'Junta de Vecinos'),
        ('otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Revisión'),
        ('aprobado', 'Aprobado / Validado'),
        ('rechazado', 'Rechazado'),
    ]

    CATEGORIA_MAIS_CHOICES = [
        ('estres', 'Reducir Estrés'),
        ('deporte', 'Hacer Deporte'),
        ('social', 'Apoyo Social'),
        ('taller', 'Talleres'),
    ]  

    FINANCIAMIENTO_CHOICES = [
            ('gratuito', 'Gratuito / Público'),
            ('copago', 'Copago / Fonasa'),
            ('pago', 'Privado / De Pago'),
            ('donacion', 'Aporte Voluntario / Donación'),
        ]

    POBLACION_CHOICES = [
        ('general', 'Público General'),
        ('ninos', 'Niños y Adolescentes'),
        ('adulto_mayor', 'Personas Mayores'),
        ('mujeres', 'Mujeres / Gestantes'),
        ('migrantes', 'Población Migrante'),
        ('discapacidad', 'Personas con Discapacidad'),
    ]

    # --- INFORMACIÓN DEL ACTIVO ---
    nombre = models.CharField(max_length=255)
    tipo_activo = models.CharField(max_length=50, choices=TIPO_ACTIVO_CHOICES, blank=True, null=True)
    categoria_mais = models.CharField(max_length=50, choices=CATEGORIA_MAIS_CHOICES, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    comuna = models.CharField(max_length=100, blank=True, null=True)
    horario = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    # --- CONTACTO ---
    contacto_nombre = models.CharField(max_length=255, blank=True, null=True)
    contacto_email = models.CharField(max_length=255, blank=True, null=True)
    contacto_fono = models.CharField(max_length=255, blank=True, null=True)


    # --- UBICACIÓN ---
    latitude = models.FloatField()
    longitude = models.FloatField()

    # --- ACCESIBILIDAD Y EQUIPAMIENTO ---
    accesibilidad_silla_ruedas = models.BooleanField(
        default=False, 
        verbose_name="Acceso para sillas de ruedas"
    )
    accesibilidad_visual = models.BooleanField(
        default=False, 
        verbose_name="Señalética Braille o sonora"
    )
    estacionamiento_general = models.BooleanField(
        default=False, 
        verbose_name="Cuenta con estacionamiento"
    )
    estacionamiento_discapacidad = models.BooleanField(
        default=False, 
        verbose_name="Estacionamiento preferencial para discapacidad"
    )
    baño_accesible = models.BooleanField(
        default=False, 
        verbose_name="Cuenta con baño adaptado"
    )

    # --- METADATOS Y ESTADO ACTUAL ---
    tipo_financiamiento = models.CharField(
        max_length=20, 
        choices=FINANCIAMIENTO_CHOICES, 
        default='gratuito'
    )
    poblacion_objetivo = models.CharField(
        max_length=20, 
        choices=POBLACION_CHOICES, 
        default='general'
    )
    requiere_inscripcion = models.BooleanField(
        default=False, 
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='activos_creados')
    aceptado_por = models.ForeignKey(
            Usuario, 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True, 
            related_name='activos_validados'
        )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente'
    )

    def cambiar_estado(self, nuevo_estado, usuario, observaciones=None):
        """
        Gestiona el cambio de estado, actualiza metadatos del activo 
        y registra automáticamente el movimiento en el historial.
        """

        with transaction.atomic():
            # 1. Lógica de negocio según el nuevo estado
            if nuevo_estado == 'pendiente':
                self.aceptado_por = None
            else:
                # Tanto para aprobado como rechazado, registramos quién tomó la acción
                self.aceptado_por = usuario
            
            self.estado = nuevo_estado
            self.save()

            # 2. Registro de auditoría
            return AssetHistory.objects.create(
                asset=self,
                estado=nuevo_estado,
                responsable=usuario,
                observaciones=observaciones
            )
        
    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"


class AssetHistory(models.Model):
    """
    Tabla de auditoría para seguir cada cambio de estado del activo.
    """
    asset = models.ForeignKey(
        ComunityAsset, 
        on_delete=models.CASCADE, 
        related_name='historial'
    )
    estado = models.CharField(
        max_length=20, 
        choices=ComunityAsset.ESTADO_CHOICES
    )
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='acciones_validación'
    )
    observaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Motivo del rechazo o notas de la validación"
    )
    
    class Meta:
        ordering = ['-fecha_movimiento']

    def __str__(self):
        return f"{self.asset.nombre} -> {self.estado} por {self.responsable}"