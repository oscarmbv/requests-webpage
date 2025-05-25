# tasks/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = _('Task Management')

    def ready(self):
        print(f"[{timezone.now()}] TasksConfig.ready() CALLED")  # Para ver cuándo se ejecuta
        from django.conf import settings

        if 'django_q' not in settings.INSTALLED_APPS:
            print(f"[{timezone.now()}] Django-Q not in INSTALLED_APPS. Skipping all schedule creation.")
            return

        print(f"[{timezone.now()}] Django-Q is in INSTALLED_APPS. Attempting to import Schedule...")
        try:
            from django_q.models import Schedule
            print(f"[{timezone.now()}] Successfully imported django_q.models.Schedule.")
        except ImportError as e_import_schedule:
            print(f"[{timezone.now()}] CRITICAL: Failed to import django_q.models.Schedule: {e_import_schedule}")
            return  # No podemos continuar si Schedule no se puede importar

        # --- Tarea existente para process_scheduled_requests ---
        schedule_name_daily = 'Process Scheduled User Requests Daily at 1 PM UTC'
        function_path_daily = 'tasks.scheduled_jobs.process_scheduled_requests'
        print(f"[{timezone.now()}] Checking/Creating schedule: {schedule_name_daily}")
        try:
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
                print(f"[{timezone.now()}] CREATED schedule: {schedule_name_daily}")
            else:
                print(f"[{timezone.now()}] FOUND schedule: {schedule_name_daily} already exists.")
        except Exception as e_daily:
            print(f"[{timezone.now()}] ERROR handling schedule '{schedule_name_daily}': {e_daily}")

        # --- NUEVA TAREA: Sincronización con Salesforce ---
        schedule_name_salesforce = 'Sync Salesforce Opportunities Multiple Times Daily'
        function_path_salesforce = 'tasks.salesforce_sync.sync_salesforce_opportunities_task'
        print(f"[{timezone.now()}] Checking/Creating schedule: {schedule_name_salesforce}")
        try:
            if not Schedule.objects.filter(name=schedule_name_salesforce).exists():
                # Simplificado next_run para prueba inicial, Django-Q lo ajustará para el CRON.
                # O usa la lógica anterior si prefieres ser más explícito con la primera ejecución.
                now_utc_for_sf = timezone.now()
                run_hours = [13, 16, 19]
                next_run_time_sf = None
                for hour in run_hours:
                    potential_next_run = now_utc_for_sf.replace(hour=hour, minute=0, second=0, microsecond=0)
                    if potential_next_run > now_utc_for_sf:
                        next_run_time_sf = potential_next_run
                        break
                if next_run_time_sf is None:
                    next_run_time_sf = (now_utc_for_sf + datetime.timedelta(days=1)).replace(hour=run_hours[0],
                                                                                             minute=0, second=0,
                                                                                             microsecond=0)

                print(
                    f"[{timezone.now()}] Attempting to create schedule: {schedule_name_salesforce} with func: {function_path_salesforce}")
                Schedule.objects.create(
                    name=schedule_name_salesforce,
                    func=function_path_salesforce,
                    schedule_type=Schedule.CRON,
                    cron='0 13,16,19 * * *',
                    next_run=next_run_time_sf,
                    repeats=-1,
                )
                print(
                    f"[{timezone.now()}] CREATED schedule: {schedule_name_salesforce} with CRON '0 13,16,19 * * *'. Next run: {next_run_time_sf.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            else:
                print(f"[{timezone.now()}] FOUND schedule: {schedule_name_salesforce} already exists.")
        except Exception as e_salesforce:
            # Esta excepción es crucial. Si hay un error al crear la tarea de Salesforce, se mostrará aquí.
            print(f"[{timezone.now()}] ERROR handling schedule '{schedule_name_salesforce}': {e_salesforce}")
            import traceback
            traceback.print_exc()  # Imprime el traceback completo del error

        print(f"[{timezone.now()}] TasksConfig.ready() FINISHED")