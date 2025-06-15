# tasks/migrations/0065_populate_toggles.py (el número puede variar)

from django.db import migrations
import datetime
from django.utils import timezone

def create_initial_toggles(apps, schema_editor):
    """
    Crea los toggles de tareas programadas y notificaciones si no existen.
    """
    ScheduledTaskToggle = apps.get_model('tasks', 'ScheduledTaskToggle')
    NotificationToggle = apps.get_model('tasks', 'NotificationToggle')
    db_alias = schema_editor.connection.alias

    # --- Toggles para Tareas Programadas (Corregido a task_name) ---
    scheduled_toggles_to_create = [
        'salesforce_sync_opportunities',
    ]
    for name in scheduled_toggles_to_create:
        toggle, created = ScheduledTaskToggle.objects.using(db_alias).get_or_create(
            task_name=name,  # CORRECCIÓN #1
            defaults={'is_enabled': True}
        )
        if created:
            print(f"Created ScheduledTaskToggle: {name}")

    # --- Toggles para Notificaciones (Corregido a event_key) ---
    NOTIFICATION_EVENTS_SETUP = {
        'new_request_created': '1. Nueva Solicitud Creada (Manual y Salesforce)',
        'request_pending_approval': '2. Solicitud (Deactivation) Pendiente de Aprobación',
        'request_approved': '3. Solicitud (Deactivation) Aprobada',
        'scheduled_request_activated': '4. Solicitud Programada Activada (a Pendiente)',
        'update_requested': '5. Actualización Solicitada para una Tarea',
        'update_provided': '6. Actualización Provista para una Tarea',
        'request_blocked': '7. Solicitud Bloqueada',
        'request_resolved': '8. Solicitud Bloqueada Resuelta',
        'request_sent_to_qa': '9. Solicitud Enviada a QA',
        'request_rejected': '10. Solicitud Rechazada desde QA/Admin',
        'request_cancelled': '11. Solicitud Cancelada',
        'request_uncancelled': '12. Solicitud Descancelada',
        'request_completed': '13. Solicitud Completada',
    }
    for event_key, description in NOTIFICATION_EVENTS_SETUP.items():
        toggle, created = NotificationToggle.objects.using(db_alias).get_or_create(
            event_key=event_key,  # CORRECCIÓN #2
            defaults={'description': description, 'is_email_enabled': True}
        )
        if created:
            print(f"Created NotificationToggle: {event_key}")


class Migration(migrations.Migration):

    dependencies = [
        # La dependencia debe ser la migración anterior a esta
        ('tasks', '0064_populate_final_price'),
    ]

    operations = [
        migrations.RunPython(create_initial_toggles),
    ]