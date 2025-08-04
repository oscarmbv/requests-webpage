# tasks/utils.py
import markdown2
import bleach
import re

def format_datetime_to_str(dt_object):
    """
    Toma un objeto datetime y lo convierte a un string con el formato estándar de la app.
    Asume que el objeto ya está en la zona horaria correcta.
    """
    if not dt_object:
        return "N/A"

    return dt_object.strftime('%Y-%m-%d %H:%M %Z')

def convert_markdown_to_html(markdown_text):
    """
    Convierte Markdown a HTML semántico y seguro.
    """
    if not markdown_text:
        return ""

    html = markdown2.markdown(markdown_text, extras=["target-blank-links"])

    safe_html = bleach.clean(
        html,
        tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'br'],
        attributes={'a': ['href', 'title', 'target']}
    )

    return safe_html

def convert_markdown_to_plain_text(markdown_text):
    """
    Convierte un texto en formato Markdown a texto plano.
    """
    if not markdown_text:
        return ""

    html = markdown2.markdown(markdown_text)

    plain_text = bleach.clean(html, tags=[], strip=True)
    return plain_text