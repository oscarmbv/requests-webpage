# tasks/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone
import logging

logger_tasks_apps = logging.getLogger(__name__)  # <--- AÑADIDO


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = _('Task Management')

    def ready(self):
        # Es una buena práctica llamar al metodo ready() de la superclase si tu AppConfig hereda de otra
        # que no sea la base AppConfig, o si futuras versiones de Django lo requieren más estrictamente.
        # Para django.apps.AppConfig base, no es estrictamente necesario si no hay lógica base que mantener.
        # super().ready()

        # Usamos el logger que definimos arriba
        logger_tasks_apps.info(f"[{timezone.now()}] TasksConfig.ready() CALLED - App: {self.name}")
        from django.conf import settings

        # --- Código existente para Django Q Schedule ---
        if 'django_q' in settings.INSTALLED_APPS:
            logger_tasks_apps.info(
                f"[{timezone.now()}] Django-Q is in INSTALLED_APPS. Attempting to import Schedule...")
            try:
                from django_q.models import Schedule
                logger_tasks_apps.info(f"[{timezone.now()}] Successfully imported django_q.models.Schedule.")

                # Tarea para process_scheduled_requests
                schedule_name_daily = 'Process Scheduled User Requests Daily at 1 PM UTC'
                function_path_daily = 'tasks.scheduled_jobs.process_scheduled_requests'
                if not Schedule.objects.filter(name=schedule_name_daily).exists():
                    Schedule.objects.create(
                        name=schedule_name_daily,
                        func=function_path_daily,
                        schedule_type=Schedule.DAILY,
                        next_run=datetime.datetime.now(tz=timezone.utc).replace(
                            hour=13, minute=0, second=0, microsecond=0
                        ),
                        repeats=-1,
                    )
                    logger_tasks_apps.info(f"[{timezone.now()}] CREATED schedule: {schedule_name_daily}")
                else:
                    logger_tasks_apps.info(f"[{timezone.now()}] FOUND schedule: {schedule_name_daily} already exists.")

                # Tarea para Sincronización con Salesforce
                schedule_name_salesforce = 'Sync Salesforce Opportunities Multiple Times Daily'
                function_path_salesforce = 'tasks.salesforce_sync.sync_salesforce_opportunities_task'
                if not Schedule.objects.filter(name=schedule_name_salesforce).exists():
                    now_utc_for_sf = timezone.now()
                    run_hours = [13, 16, 19]  # Horas UTC
                    next_run_time_sf = None
                    for hour in run_hours:
                        potential_next_run = now_utc_for_sf.replace(hour=hour, minute=0, second=0, microsecond=0)
                        if potential_next_run > now_utc_for_sf:
                            next_run_time_sf = potential_next_run
                            break
                    if next_run_time_sf is None:  # Si todas las horas de hoy ya pasaron
                        next_run_time_sf = (now_utc_for_sf + datetime.timedelta(days=1)).replace(hour=run_hours[0],
                                                                                                 minute=0, second=0,
                                                                                                 microsecond=0)
                    Schedule.objects.create(
                        name=schedule_name_salesforce,
                        func=function_path_salesforce,
                        schedule_type=Schedule.CRON,
                        cron='0 13,16,19 * * *',  # A las 13:00, 16:00, y 19:00 UTC todos los días
                        next_run=next_run_time_sf,
                        repeats=-1,
                    )
                    logger_tasks_apps.info(
                        f"[{timezone.now()}] CREATED schedule: {schedule_name_salesforce} with CRON '0 13,16,19 * * *'. Next run: {next_run_time_sf.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                else:
                    logger_tasks_apps.info(
                        f"[{timezone.now()}] FOUND schedule: {schedule_name_salesforce} already exists.")

            except ImportError as e_import_schedule:
                logger_tasks_apps.critical(
                    f"[{timezone.now()}] CRITICAL: Failed to import django_q.models.Schedule: {e_import_schedule}")
                # Considera no retornar aquí para que el resto de ready() pueda ejecutarse si es independiente.
            except Exception as e_schedule:
                logger_tasks_apps.error(f"[{timezone.now()}] ERROR handling Django Q Schedules: {e_schedule}", exc_info=True)
        else:
            logger_tasks_apps.info(
                f"[{timezone.now()}] Django-Q not in INSTALLED_APPS. Skipping all Django Q schedule creation.")
        # --- Fin código Django Q Schedule ---

        # ---- Asegurar que los NotificationToggles existan ----
        # Solo ejecutar si la app 'admin' y 'tasks' están instaladas y la DB está lista (evitar errores en migraciones)
        if all(app in settings.INSTALLED_APPS for app in ['django.contrib.admin', self.name]):
            try:
                # Importar modelos aquí para asegurar que el AppRegistry esté listo
                from .models import NotificationToggle

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
                    toggle, created = NotificationToggle.objects.get_or_create(
                        event_key=event_key,
                        defaults={'description': description, 'is_email_enabled': True}  # Habilitado por defecto
                    )
                    if created:
                        logger_tasks_apps.info(
                            f"Created NotificationToggle for event: '{event_key}' - '{description}' (Email Enabled by default)")
                    # else: # Opcional: loguear si ya existe
                    # logger_tasks_apps.debug(f"NotificationToggle for event: '{event_key}' already exists.")

            except Exception as e_toggles:
                # Esto puede ocurrir si las migraciones aún no se han aplicado completamente para el modelo NotificationToggle
                # o si hay otro problema de base de datos al inicio.
                # Es importante loguearlo pero no necesariamente detener el inicio de la aplicación.
                print(
                    f"ADVERTENCIA en TasksConfig.ready(): No se pudieron crear/verificar los NotificationToggles: {e_toggles}")
                logger_tasks_apps.warning(f"Could not create/check NotificationToggles during app ready: {e_toggles}", exc_info=False)

        logger_tasks_apps.info(f"[{timezone.now()}] TasksConfig.ready() FINISHED for app: {self.name}")