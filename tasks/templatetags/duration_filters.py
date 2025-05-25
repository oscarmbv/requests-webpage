from django import template
from datetime import timedelta

register = template.Library()


@register.filter
def format_timedelta(value):
    if not isinstance(value, timedelta):
        return ""

    total_seconds = int(value.total_seconds())

    if total_seconds < 0:
        return " (negative)"

    if total_seconds == 0:
        if value.microseconds > 0:
            milliseconds = value.microseconds // 1000
            if milliseconds > 0:
                return f"{milliseconds} ms"
        return "0 s"

    days = total_seconds // 86400
    remaining_seconds_after_days = total_seconds % 86400

    hours = remaining_seconds_after_days // 3600
    remaining_seconds_after_hours = remaining_seconds_after_days % 3600

    minutes = remaining_seconds_after_hours // 60
    seconds = remaining_seconds_after_hours % 60

    parts = []

    if days > 0:
        parts.append(f"{days} d")
        if hours > 0:
            parts.append(f"{hours} h")
        elif len(parts) < 2 and minutes > 0:
            display_minutes = minutes
            if seconds >= 30:
                display_minutes += 1
            if display_minutes > 0:
                parts.append(f"{display_minutes} min")
        elif len(parts) < 2 and seconds > 0 and minutes == 0 and hours == 0:
            parts.append(f"{seconds} s")


    elif hours > 0:  # No hay días, pero sí horas
        parts.append(f"{hours} h")
        if minutes > 0:
            display_minutes = minutes
            if seconds >= 30:
                display_minutes += 1
            if display_minutes > 0:
                parts.append(f"{display_minutes} m")
        elif len(parts) < 2 and seconds > 0 and minutes == 0:
            parts.append(f"{seconds} s")


    elif minutes > 0:

        display_minutes = minutes
        if seconds >= 30:
            display_minutes += 1

        parts.append(f"{display_minutes} m")

    elif seconds > 0:
        parts.append(f"{seconds} s")

    if not parts and total_seconds > 0:
        if seconds > 0:
            parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")
        else:
            if value.microseconds > 0:
                milliseconds = value.microseconds // 1000
                if milliseconds > 0:
                    return f"{milliseconds} ms"
            return "0 s"

    return ", ".join(parts) if parts else "0 s"