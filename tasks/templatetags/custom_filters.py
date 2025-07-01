import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """
    Devuelve solo el nombre del archivo de una ruta completa.
    Ejemplo: 'folder/file.txt' -> 'file.txt'
    """
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    return os.path.basename(str(value))