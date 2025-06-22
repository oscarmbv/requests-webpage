# tasks/utils.py

def format_datetime_to_str(dt_object):
    """
    Toma un objeto datetime y lo convierte a un string con el formato estándar de la app.
    Asume que el objeto ya está en la zona horaria correcta.
    """
    if not dt_object:
        return "N/A"

    # Este es el formato que usaremos consistentemente en todas las notificaciones.
    # Puedes cambiarlo aquí y se actualizará en todos lados.
    return dt_object.strftime('%Y-%m-%d %H:%M %Z')