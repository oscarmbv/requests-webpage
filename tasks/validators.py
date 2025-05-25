# tasks/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ # Para traducciones futuras

# Considera definir el límite en settings.py si necesitas más flexibilidad
# from django.conf import settings
# FILE_UPLOAD_MAX_SIZE_MB = getattr(settings, 'FILE_UPLOAD_MAX_SIZE_MB', 10) # Default 10MB
FILE_UPLOAD_MAX_SIZE_MB = 10 # Límite actual de 10MB

def validate_file_size(value):
    """
    Valida que el tamaño del archivo subido no exceda un límite predefinido.

    Args:
        value: El objeto FieldFile (o UploadedFile) a validar.

    Raises:
        ValidationError: Si el tamaño del archivo excede el límite.

    Returns:
        El mismo valor si la validación pasa.
    """
    if value is None: # No validar si no se subió archivo (el campo debe ser opcional)
        return value

    try:
        file_size = value.size
    except AttributeError:
        # Si 'value' no tiene 'size', no podemos validar (podría ser otro tipo de dato)
        # Podrías loguear esto o simplemente retornar el valor.
        # logger.warning(f"Could not determine size for value of type {type(value)}")
        return value

    # Límite en bytes
    limit = FILE_UPLOAD_MAX_SIZE_MB * 1024 * 1024

    if file_size > limit:
        # Mensaje de error más informativo
        error_message = _(
            'File size cannot exceed %(limit_mb)s MB. Current file size is %(current_size_mb).2f MB.'
        ) % {
            'limit_mb': FILE_UPLOAD_MAX_SIZE_MB,
            'current_size_mb': file_size / (1024 * 1024)
            }
        raise ValidationError(error_message)

    return value # Devuelve el archivo si es válido

# Podrías añadir más validadores aquí si los necesitas, por ejemplo:
# def validate_file_extension(value):
#     import os
#     ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
#     valid_extensions = ['.pdf', '.doc', '.docx', '.xlsx', '.csv', '.zip'] # Ejemplo
#     if not ext.lower() in valid_extensions:
#         raise ValidationError(_('Unsupported file extension. Allowed types are: %(valid_exts)s') % {'valid_exts': ', '.join(valid_extensions)})
#     return value