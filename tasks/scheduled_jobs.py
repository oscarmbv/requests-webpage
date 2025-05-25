# tasks/scheduled_jobs.py

from django.utils import timezone
from .models import UserRecordsRequest  # Asegúrate de que la ruta al modelo sea correcta
import logging

logger = logging.getLogger(__name__)  # Usar el logger de Django-Q o el de tu app


def process_scheduled_requests():
    """
    Busca solicitudes con estado 'scheduled' cuya fecha programada
    es hoy o anterior, y las cambia a 'pending'.
    Esta función está diseñada para ser llamada por Django-Q.
    """
    logger.info("Task 'process_scheduled_requests' running...")
    today_utc = timezone.now().date()  # Obtiene la fecha actual en UTC
    current_time_utc = timezone.now()

    requests_to_activate = UserRecordsRequest.objects.filter(
        status='scheduled',
        scheduled_date__lte=today_utc
    )

    activated_count = 0
    if requests_to_activate.exists():  # Solo procede si hay algo que hacer
        for req in requests_to_activate:
            try:
                req.status = 'pending'
                req.effective_start_time_for_tat = current_time_utc
                fields_to_update = ['status', 'effective_start_time_for_tat']
                req.save(update_fields=fields_to_update)
                logger.info(f"Activated request: {req.unique_code} (ID: {req.id}) - Status changed to 'pending'. TAT start set to: {current_time_utc}. Was scheduled for: {req.scheduled_date}")
                activated_count += 1
            except Exception as e:
                logger.error(f"Error activating request {req.unique_code} (ID: {req.id}): {e}", exc_info=True)

    if activated_count > 0:
        logger.info(f"Successfully activated {activated_count} scheduled requests.")
    else:
        logger.info(f"No scheduled requests to activate for today ({today_utc.strftime('%Y-%m-%d')}) or earlier.")

    return f"Processed {activated_count} scheduled requests."