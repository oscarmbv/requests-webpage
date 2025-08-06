# tasks/utils.py
import markdown2
import bleach
import html2text

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
    Convierte Markdown a HTML semántico y seguro,
    evitando la creación de <br> en saltos de línea simples.
    """
    if not markdown_text:
        return ""

    html = markdown2.markdown(
        markdown_text,
        extras={
            "target-blank-links": None,
            "break-on-newline": False
        }
    )

    safe_html = bleach.clean(
        html,
        tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'br'],
        attributes={'a': ['href', 'title', 'target']}
    )

    return safe_html


def convert_markdown_to_plain_text(markdown_text):
    """
    Convierte Markdown a un texto plano bien formateado, con el formato correcto.
    """
    if not markdown_text:
        return ""

    extras = {
        "target-blank-links": None,
        "break-on-newline": False,
    }
    html = markdown2.markdown(markdown_text, extras=extras)

    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_emphasis = True

    plain_text = h.handle(html)

    return plain_text.strip()