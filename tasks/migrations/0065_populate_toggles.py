# tasks/migrations/0065_populate_toggles.py (el número puede variar)

from django.db import migrations
import datetime
from django.utils import timezone

def create_initial_toggles(apps, schema_editor):
    """
    Crea los toggles de tareas programadas y notificaciones si no existen.
    """
    # Obtenemos los modelos de la versión histórica de la app 'tasks'
    ScheduledTaskToggle = apps.get_model('tasks', 'ScheduledTaskToggle')
    NotificationToggle = apps.get_model('tasks', 'NotificationToggle')
    db_alias = schema_editor.connection.alias

    # --- Toggles para Tareas Programadas ---
    scheduled_toggles_to_create = [
        'salesforce_sync_opportunities',
        # Añade aquí cualquier otro toggle de tarea programada que necesites
    ]
    for name in scheduled_toggles_to_create:
        ScheduledTaskToggle.objects.using(db_alias).get_or_create(
            task_name=name,
            defaults={'is_enabled': True}
        )
        print(f"Checked/Created ScheduledTaskToggle: {name}")

    # --- Toggles para Notificaciones ---
    # (Aquí he replicado la lógica que vi en tu código, puedes ajustarla si es necesario)
    notification_events = [
        'new_request_created', 'request_approved', 'request_rejected',
        'request_completed', 'request_blocked', 'request_cancelled',
        'request_uncancelled', 'update_provided', 'update_requested',
        'sent_to_qa', 'request_resolved', 'salesforce_new_request'
    ]
    for event in notification_events:
        NotificationToggle.objects.using(db_alias).get_or_create(
            event_name=event,
            defaults={'is_enabled': True}
        )
        print(f"Checked/Created NotificationToggle: {event}")


class Migration(migrations.Migration):

    dependencies = [
        # La dependencia debe ser la migración anterior a esta
        ('tasks', '0064_populate_final_price'),
    ]

    operations = [
        migrations.RunPython(create_initial_toggles),
    ]