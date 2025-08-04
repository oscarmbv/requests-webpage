import os
from django import template
from django.utils.safestring import mark_safe
from ..utils import convert_markdown_to_html, convert_markdown_to_plain_text

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

@register.filter(name='markdown_to_html')
def markdown_to_html(markdown_text):
    """Convierte un texto Markdown a HTML seguro para usar en plantillas."""
    if not markdown_text:
        return ""
    return mark_safe(convert_markdown_to_html(markdown_text))

@register.filter(name='markdown_to_plain_text')
def markdown_to_plain_text(markdown_text):
    """Convierte un texto Markdown a texto plano para usar en plantillas."""
    if not markdown_text:
        return ""
    # Llama a la función que convierte a texto plano
    return convert_markdown_to_plain_text(markdown_text)