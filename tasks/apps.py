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
        logger_tasks_apps.info(f"[{timezone.now()}] TasksConfig.ready() CALLED - App: {self.name}")
        from django.conf import settings

        # --- Código para Django Q Schedule ---
        if 'django_q' in settings.INSTALLED_APPS:
            logger_tasks_apps.info(
                f"[{timezone.now()}] Django-Q is in INSTALLED_APPS. App is ready to handle schedules.")
            # LA LÓGICA DE CREACIÓN DE SCHEDULES HA SIDO MOVIDA A UNA MIGRACIÓN DE DATOS
        else:
            logger_tasks_apps.info(
                f"[{timezone.now()}] Django-Q not in INSTALLED_APPS. Skipping all Django Q schedule creation.")
        # --- Fin código Django Q Schedule ---

        # ---- Lógica para NotificationToggles ----
        # LA LÓGICA DE CREACIÓN DE NOTIFICATIONTOGGLES HA SIDO MOVIDA A UNA MIGRACIÓN DE DATOS
        # Dejamos una advertencia en caso de que la migración falle, pero no intentamos crear desde aquí.
        if all(app in settings.INSTALLED_APPS for app in ['django.contrib.admin', self.name]):
            try:
                from .models import NotificationToggle
                if NotificationToggle.objects.count() == 0:
                     logger_tasks_apps.warning("NotificationToggles not found. Ensure data migration has run.")
            except Exception as e:
                # Esto puede pasar si las tablas aún no existen. Es seguro ignorarlo aquí.
                logger_tasks_apps.warning(f"Could not check for NotificationToggles, likely because tables are not created yet: {e}")


        logger_tasks_apps.info(f"[{timezone.now()}] TasksConfig.ready() FINISHED for app: {self.name}")