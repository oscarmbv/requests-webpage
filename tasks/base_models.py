# tasks/base_models.py

from django.db import models
from django.conf import settings # Para referenciar el modelo de usuario activo
from django.utils import timezone # Para timestamps por defecto

class RequestRelatedModel(models.Model):
    """
    Modelo base abstracto para modelos que registran eventos
    o historial relacionados con una UserRecordsRequest.

    Incluye campos comunes como la relación con la solicitud,
    el timestamp del evento y el usuario que actuó.
    """
    # Relación con la solicitud principal. CASCADE significa que si se borra
    # la solicitud, también se borrarán estos registros de historial.
    request = models.ForeignKey(
        'UserRecordsRequest', # Referencia al modelo principal (usar string si está en el mismo archivo o importado después)
        on_delete=models.CASCADE,
        # Genera automáticamente el related_name inverso como 'blockedmessages', 'resolvedmessages', etc.
        related_name="%(class)ss"
    )
    # Timestamp del evento (cuándo se bloqueó, resolvió, rechazó, etc.)
    # Nota: Los modelos hijos (BlockedMessage, etc.) definen su propio campo
    #       de timestamp con default=now, por lo que este campo podría ser
    #       redundante si siempre usas los específicos. Se mantiene aquí
    #       como ejemplo o por si se necesita un timestamp común genérico.
    #       Si no se usa, puede eliminarse de aquí.
    timestamp = models.DateTimeField(default=timezone.now)

    # Usuario que realizó la acción (quién bloqueó, resolvió, rechazó)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Mantener el registro si el usuario se elimina
        null=True, # Permitir nulo si el usuario se elimina
        blank=True # Permitir nulo en formularios/admin
    )

    class Meta:
        # Esto indica que este modelo no creará su propia tabla en la BD,
        # sino que solo sirve como base para ser heredado por otros modelos.
        abstract = True
        # Podrías definir un ordenamiento por defecto aquí si fuera aplicable
        # ordering = ['-timestamp']