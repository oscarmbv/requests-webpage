import os
from django import template
from django.utils.html import strip_tags

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

@register.filter(name='clean_for_plaintext')
def clean_for_plaintext(value):
    if not value:
        return ""
    # 1. Quita todas las etiquetas HTML
    text = strip_tags(value)
    # 2. Reemplaza los &nbsp; por espacios normales
    text = text.replace('&nbsp;', ' ')
    # 3. Elimina espacios o saltos de línea al principio y al final
    return text.strip()