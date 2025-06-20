# tasks/notifications.py
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import requests  # Para Telegram
from django_q.tasks import async_task
from .models import UserRecordsRequest, CustomUser, NotificationToggle
from .choices import TYPE_CHOICES
import pytz
import json
from django.utils import timezone
from .models import BlockedMessage
from .choices import (
    EVENT_KEY_NEW_REQUEST_CREATED,
    EVENT_KEY_REQUEST_PENDING_APPROVAL,
    EVENT_KEY_REQUEST_APPROVED,
    EVENT_KEY_SCHEDULED_REQUEST_ACTIVATED,
    EVENT_KEY_UPDATE_REQUESTED,
    EVENT_KEY_UPDATE_PROVIDED,
    EVENT_KEY_REQUEST_BLOCKED,
    EVENT_KEY_REQUEST_RESOLVED,
    EVENT_KEY_REQUEST_SENT_TO_QA,
    EVENT_KEY_REQUEST_REJECTED,
    EVENT_KEY_REQUEST_CANCELLED,
    EVENT_KEY_REQUEST_UNCANCELLED,
    EVENT_KEY_REQUEST_COMPLETED
)

logger = logging.getLogger(__name__)


def get_absolute_url_for_request(request_obj, http_request=None):
    if not request_obj or not hasattr(request_obj, 'pk'):
        logger.warning("get_absolute_url_for_request: No request_obj o pk para generar URL.")
        return "#"

    path = "#"  # Default path to #
    try:
        path_temp = reverse('tasks:request_detail', kwargs={'pk': request_obj.pk})
        if path_temp:  # Ensure reverse did not return None or empty
            path = path_temp
        logger.info(f"[get_absolute_url] Path reversed: {path} for pk {request_obj.pk}")
    except Exception as e:
        logger.error(
            f"[get_absolute_url] Error al reversar URL 'tasks:request_detail' para pk {getattr(request_obj, 'pk', 'N/A')}: {e}",
            exc_info=True)
        return "#"  # Return "#" on error

    final_url = "#"  # Default final_url to #
    if http_request:
        try:
            abs_url = http_request.build_absolute_uri(path)
            if abs_url:
                final_url = abs_url
            logger.info(f"[get_absolute_url] Built with http_request: {final_url}")
        except Exception as e:
            logger.error(f"[get_absolute_url] Error con http_request.build_absolute_uri: {e}. Usando SITE_DOMAIN.",
                         exc_info=True)
            # Fall through to SITE_DOMAIN logic
            pass  # Ensure we still try SITE_DOMAIN

    if final_url == "#" or not http_request:  # If http_request failed or was not provided
        site_domain = getattr(settings, 'SITE_DOMAIN', 'http://localhost:8000')
        logger.info(f"[get_absolute_url] Using SITE_DOMAIN: {site_domain}")
        if not site_domain:  # Handle empty SITE_DOMAIN
            logger.error("[get_absolute_url] settings.SITE_DOMAIN is not set or is empty!")
            return "#"  # Return "#" if site_domain is invalid

        if site_domain.endswith('/'):
            site_domain = site_domain[:-1]

        if path != "#":  # Only append path if it's valid
            final_url = f"{site_domain}{path}"
        else:  # If path itself was "#"
            final_url = "#"
        logger.info(f"[get_absolute_url] Built with SITE_DOMAIN: {final_url}")

    return final_url


def send_request_notification_email(subject, template_name_base, context, recipient_list, request_obj=None,
                                    http_request_for_url=None):
    """
    Envía un correo electrónico de notificación formateado (HTML y texto).
    template_name_base es el nombre del archivo sin .html o .txt
    """
    if not recipient_list:
        logger.warning(f"No recipients provided for email subject: {subject}")
        return False

    if 'request_obj' not in context and request_obj:
        context['request_obj'] = request_obj

    context['request_url'] = get_absolute_url_for_request(request_obj, http_request_for_url)
    # Para asegurar que las plantillas siempre tengan estas variables, incluso si están vacías
    context.setdefault('event_details_html', 'Detalles del evento no proporcionados.')
    context.setdefault('event_details_plain', 'Detalles del evento no proporcionados.')

    try:
        html_message = render_to_string(f'tasks/emails/{template_name_base}.html', context)
        plain_message = render_to_string(f'tasks/emails/{template_name_base}.txt', context)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_list} for subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Error sending email (Subject: {subject}, To: {recipient_list}): {e}", exc_info=True)
        return False

def send_slack_notification(message_payload):
    """
    Envía una notificación a Slack usando un Incoming Webhook.
    'message_payload' debe ser un diccionario con formato de Slack Block Kit.
    """
    webhook_url = settings.SLACK_WEBHOOK_URL
    if not webhook_url:
        print("SLACK_WEBHOOK_URL no está configurada. Saltando notificación.")
        return

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(message_payload),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # Lanza un error si la petición no fue exitosa
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar notificación a Slack: {e}")

def escape_markdown_v2(text):
    """
    Escapa caracteres especiales para el modo MarkdownV2 de Telegram.
    """
    if not isinstance(text, str):
        text = str(text)
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return "".join(['\\' + char if char in escape_chars else char for char in text])


def send_telegram_message(bot_token, chat_id, message_text):
    """
    Envía un mensaje a través de un bot de Telegram usando MarkdownV2.
    El message_text ya debe estar escapado correctamente ANTES de llamar a esta función.
    """
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado. No se puede enviar el mensaje de Telegram.")
        return None
    if not chat_id:
        logger.error("chat_id no proporcionado para mensaje de Telegram.")
        return None

    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'MarkdownV2'
    }
    try:
        response = requests.post(telegram_api_url, data=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Telegram message sent successfully to chat_id {chat_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error sending Telegram message to chat_id {chat_id}: {e} - Response: {e.response.text if e.response else 'No response'}",
            exc_info=True)
        return None
    except Exception as e_general:
        logger.error(f"Unexpected error sending Telegram message: {e_general}", exc_info=True)
        return None

def is_email_notification_enabled(event_key_param):
    """
    Verifica si las notificaciones por email están habilitadas para un evento dado.
    """
    try:
        toggle = NotificationToggle.objects.get(event_key=event_key_param)
        if not toggle.is_email_enabled:
            logger.info(f"Email notifications for event '{event_key_param}' are DISABLED by admin toggle.")
            return False
        logger.info(f"Email notifications for event '{event_key_param}' are ENABLED.")
        return True
    except NotificationToggle.DoesNotExist:
        logger.warning(f"NotificationToggle for event_key '{event_key_param}' not found in DB. Defaulting to ENABLED. Please create this toggle in Django Admin.")
        return True # O False, según tu preferencia de comportamiento por defecto
    except Exception as e:
        logger.error(f"Error checking NotificationToggle for event '{event_key_param}': {e}. Defaulting to ENABLED.", exc_info=True)
        return True # Falla segura: intentar enviar si hay un error al consultar el toggle.

# 1
def notify_new_request_created(request_pk, http_request_host=None, http_request_scheme=None):
    """
    Prepara y envía notificaciones cuando se crea una nueva solicitud.
    Llamada de forma asíncrona.
    """
    # Usar la constante importada de tasks.choices
    current_event_key = EVENT_KEY_NEW_REQUEST_CREATED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related('requested_by').get(pk=request_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return

    # --- Preparación de datos comunes ---
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
        logger.info(f"[{current_event_key}] Construyendo URL con http_request_host: {http_request_host}")
    else:
        logger.info(f"[{current_event_key}] No http_request_host/scheme, se usará SITE_DOMAIN para URL.")

    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)
    logger.info(f"[{current_event_key}] URL generada para notificación: {request_url}")

    caracas_tz = pytz.timezone('America/Caracas')
    timestamp_in_caracas = request_obj.timestamp.astimezone(caracas_tz)
    is_salesforce_originated = bool(request_obj.salesforce_standard_opp_id)
    type_display = request_obj.get_type_of_process_display()

    # --- Lógica de Email (solo si está habilitado) ---
    if is_email_notification_enabled(current_event_key):
        if is_salesforce_originated:
            subject = f"{request_obj.unique_code}: New request created from Salesforce"
            email_template_base = 'salesforce_new_request'
        else:
            subject = f"{request_obj.unique_code}: New {type_display} Request"
            email_template_base = 'new_request_created'

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'timestamp_in_caracas_str': timestamp_in_caracas.strftime("%B %d, %Y, %I:%M %p %Z"),
            # request_url se añade dentro de send_request_notification_email
        }
        email_recipient_list = ['oscarmbv@gmail.com']  # Temporal

        logger.info(
            f"Preparando email para '{current_event_key}' de {request_obj.unique_code} a: {email_recipient_list}")
        send_request_notification_email(
            subject,
            email_template_base,
            email_context,
            email_recipient_list,
            request_obj=request_obj,
            # http_request_for_url no se pasa aquí si ya se usó para construir request_url
        )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # --- Lógica de Telegram (se envía independientemente del toggle de email por ahora) ---
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        url_for_telegram_link = request_url  # Usar URL cruda para el enlace

        if is_salesforce_originated:
            telegram_message_text = (
                f"*{req_code_escaped}*: New request has been created from a Salesforce Opportunity\n"
                f"[View Request Details]({url_for_telegram_link})"
            )
        else:
            type_display_escaped = escape_markdown_v2(type_display)
            requested_by_escaped = escape_markdown_v2(request_obj.requested_by.email)
            timestamp_caracas_str_escaped = escape_markdown_v2(timestamp_in_caracas.strftime("%Y-%m-%d %H:%M %Z"))

            additional_info_line_telegram = ""
            if request_obj.type_of_process == 'generating_xml':
                xml_state_display = request_obj.get_xml_state_display()
                if xml_state_display:
                    additional_info_line_telegram = f"State: {escape_markdown_v2(xml_state_display)}\n"
            elif request_obj.partner_name:
                additional_info_line_telegram = f"Partner: {escape_markdown_v2(request_obj.partner_name)}\n"

            telegram_message_text = (
                f"*{req_code_escaped}*: New {type_display_escaped} request\n"
                f"Sent by: {requested_by_escaped}\n"
                f"At: {timestamp_caracas_str_escaped}\n"
                f"{additional_info_line_telegram}"
                f"[View Request Details]({url_for_telegram_link})"
            )

        logger.info(f"Preparando mensaje de Telegram para '{current_event_key}' de {request_obj.unique_code} a chat_id: {settings.TELEGRAM_DEFAULT_CHAT_ID}")
        send_telegram_message(
            settings.TELEGRAM_BOT_TOKEN,
            settings.TELEGRAM_DEFAULT_CHAT_ID,
            telegram_message_text
        )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados. No se enviará Telegram para '{current_event_key}' de {request_obj.unique_code}.")

#2
def notify_pending_approval_request(request_pk, http_request_host=None, http_request_scheme=None):
    """
    Prepara y envía notificaciones cuando una solicitud de Deactivation/Toggle
    se crea y queda en estado 'Pending for Approval'.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_PENDING_APPROVAL
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related('requested_by').get(pk=request_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return

    if request_obj.type_of_process != 'deactivation_toggle' or request_obj.status != 'pending_approval':
        logger.warning(
            f"{current_event_key} llamada para solicitud {request_obj.unique_code} que no es Deactivation/Toggle o no está Pending Approval. Status: {request_obj.status}, Type: {request_obj.type_of_process}")
        return

    # ---- Preparación de datos comunes (URL, Timestamp) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme

    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    caracas_tz = pytz.timezone('America/Caracas')
    timestamp_in_caracas = request_obj.timestamp.astimezone(caracas_tz)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        deactivation_type_display = request_obj.get_deactivation_toggle_type_display()
        subject = f"Approval Needed: {request_obj.unique_code} - {deactivation_type_display}"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            # request_url se añade dentro de send_request_notification_email
        }
        email_recipient_list = ['oscarmbv@gmail.com']  # Temporal, cuando agreguemos a Shay, tambien incluir un correo de nosotros.

        logger.info(
            f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
        send_request_notification_email(
            subject,
            'pending_approval_notification',  # Plantilla específica para este evento
            email_context,
            email_recipient_list,
            request_obj=request_obj,
        )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)

        requested_by_text = request_obj.requested_by.email
        deactivation_type_text = request_obj.get_deactivation_toggle_type_display()  # Texto crudo
        requested_at_text = timestamp_in_caracas.strftime("%Y-%m-%d %H:%M %Z")  # Texto crudo

        # Escapar las partes del mensaje que necesitan ser literales
        line1_part1 = escape_markdown_v2(f"New {deactivation_type_text} request sent by: {requested_by_text}, at {requested_at_text} and needs approval.")
        line1_part2 = escape_markdown_v2("Notification email has been sent asking for approval.")

        partner_line_telegram = ""
        if request_obj.partner_name:
            # Usar \\- para un guion literal si es necesario
            partner_line_telegram = f"\n\\- Partner: {escape_markdown_v2(request_obj.partner_name)}"

        url_for_telegram_link = request_url  # URL cruda para el hipervínculo

        telegram_message_text = (
            f"*{req_code_escaped}*: {line1_part1}\n"
            f"{line1_part2}"
            f"{partner_line_telegram}\n\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {settings.TELEGRAM_DEFAULT_CHAT_ID}")
        send_telegram_message(
            settings.TELEGRAM_BOT_TOKEN,
            settings.TELEGRAM_DEFAULT_CHAT_ID,
            telegram_message_text
        )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no están configurados. No se enviará mensaje de Telegram para '{current_event_key}' de {request_obj.unique_code}.")

#3
def notify_request_approved(request_pk, approver_user_pk, http_request_host=None, http_request_scheme=None):
    """
    Prepara y envía notificaciones cuando una solicitud ha sido aprobada.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_APPROVED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related('requested_by', 'operator', 'qa_agent').get(
            pk=request_pk)  # Incluir operador y QA si son relevantes para destinatarios
        approver_user = CustomUser.objects.get(pk=approver_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: Approver User con pk {approver_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was approved"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'approver_user': approver_user,
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')  # Temporal

        # Notificar al usuario que creó originalmente la solicitud
        if request_obj.requested_by and request_obj.requested_by.email:
            # Evitar notificar al aprobador si él mismo creó la solicitud (aunque en este flujo, el aprobador es un líder)
            if request_obj.requested_by.pk != approver_user.pk:
                recipients_email_set.add(request_obj.requested_by.email)

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_approved_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar email crudo para el aprobador en el mensaje de Telegram
        approved_by_raw_email = approver_user.email
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"✅ *Request Approved* ✅\n\n"
            f"Request *{req_code_escaped}* was approved by {escape_markdown_v2(approved_by_raw_email)}\\.\n"  # Email crudo, punto final escapado
            f"[View Request Details]({url_for_telegram_link})"
        )

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {settings.TELEGRAM_DEFAULT_CHAT_ID}")
        send_telegram_message(
            settings.TELEGRAM_BOT_TOKEN,
            settings.TELEGRAM_DEFAULT_CHAT_ID,
            telegram_message_text
        )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no están configurados. No se enviará Telegram para '{current_event_key}' de {request_obj.unique_code}.")

#4
def notify_scheduled_request_activated(request_pk):  # No necesita http_request_host/scheme
    """
    Prepara y envía notificaciones cuando una solicitud programada se activa (cambia a Pending).
    Llamada desde una tarea de Django Q, por lo que no hay http_request.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_SCHEDULED_REQUEST_ACTIVATED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related('requested_by').get(pk=request_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return

    # get_absolute_url_for_request usará settings.SITE_DOMAIN ya que no hay http_request
    request_url = get_absolute_url_for_request(request_obj)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Scheduled request {request_obj.unique_code} is now ready"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            # request_url se añade/usa dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        email_recipient_list = ['oscarmbv@gmail.com']  # Temporal
        # Podrías añadir otros destinatarios aquí, como request_obj.requested_by.email

        logger.info(
            f"Preparando email para '{current_event_key}' de {request_obj.unique_code} a: {email_recipient_list}")
        send_request_notification_email(
            subject,
            'scheduled_to_pending_notification',  # Plantilla específica para este evento
            email_context,
            email_recipient_list,
            request_obj=request_obj,
        )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        url_for_telegram_link = request_url  # URL cruda para el hipervínculo

        telegram_message_text = (
            f"🗓️ Request *{req_code_escaped}* is now ready to be operated\\.\n"  # Punto escapado
            f"[View Request Details]({url_for_telegram_link})"
        )

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {settings.TELEGRAM_DEFAULT_CHAT_ID}")
        send_telegram_message(
            settings.TELEGRAM_BOT_TOKEN,
            settings.TELEGRAM_DEFAULT_CHAT_ID,
            telegram_message_text
        )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no están configurados. No se enviará mensaje de Telegram para '{current_event_key}' de {request_obj.unique_code}.")

#5
def notify_update_requested(request_pk, update_requester_user_pk, http_request_host=None, http_request_scheme=None):
    """
    Prepara y envía notificaciones cuando un usuario solicita una actualización para una tarea.
    Notifica al operador asignado y al agente de QA si existen.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_UPDATE_REQUESTED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent', 'update_requested_by'
            # update_requested_by es quien solicitó la actualización
        ).get(pk=request_pk)
        # El update_requester_user es quien hizo clic en el botón "Request Update"
        # y ya se está pasando su PK como update_requester_user_pk
        update_requester_user = CustomUser.objects.get(pk=update_requester_user_pk)

    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(
            f"{current_event_key}: User (update_requester) con pk {update_requester_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"{update_requester_user.email} is requesting an update for {request_obj.unique_code}"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'update_requester_user': update_requester_user,  # Quien solicitó el update
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')  # Tu correo temporal

        if request_obj.operator and request_obj.operator.email:
            recipients_email_set.add(request_obj.operator.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al operador {request_obj.operator.email}")
        else:
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: No hay operador asignado o no tiene email.")

        if request_obj.qa_agent and request_obj.qa_agent.email:
            recipients_email_set.add(request_obj.qa_agent.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al QA agent {request_obj.qa_agent.email}")
        else:
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: No hay QA agent asignado o no tiene email.")

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'update_requested_notification',  # Plantilla específica para este evento
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        # Usar el email crudo para quien solicita la actualización, como funcionó antes
        update_requester_raw_email = update_requester_user.email
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"⚠️ *Update Requested* ⚠️\n\n"
            f"{escape_markdown_v2(update_requester_raw_email)} is requesting an update for request *{req_code_escaped}*\\.\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        if telegram_recipient_chat_id:
            logger.info(
                f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
        else:
            logger.warning(
                f"No Telegram chat_id configurado para recibir la notificación de '{current_event_key}' para {request_obj.unique_code}.")

    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no están configurados. No se enviará Telegram para '{current_event_key}' de {request_obj.unique_code}.")

#6
def notify_update_provided(request_pk, updated_by_user_pk, update_message, http_request_host=None,
                           http_request_scheme=None):
    """
    Notifica cuando un agente ha proporcionado una actualización para una solicitud.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_UPDATE_PROVIDED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent', 'update_requested_by'
        ).get(pk=request_pk)
        updated_by_user = CustomUser.objects.get(pk=updated_by_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(
            f"{current_event_key}: User (updated_by_user) con pk {updated_by_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Update for Request {request_obj.unique_code}"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'updated_by_user': updated_by_user,
            'update_message_text': update_message,
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')  #Temporal

        if request_obj.update_requested_by and request_obj.update_requested_by.email:
            recipients_email_set.add(request_obj.update_requested_by.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá a quien solicitó el update {request_obj.update_requested_by.email}")
        if request_obj.operator and request_obj.operator.email and request_obj.operator.pk != updated_by_user.pk:
            recipients_email_set.add(request_obj.operator.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al operador {request_obj.operator.email}")
        if request_obj.qa_agent and request_obj.qa_agent.email and request_obj.qa_agent.pk != updated_by_user.pk:
            recipients_email_set.add(request_obj.qa_agent.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al QA agent {request_obj.qa_agent.email}")
        if request_obj.requested_by and request_obj.requested_by.email:
            recipients_email_set.add(request_obj.requested_by.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al creador original {request_obj.requested_by.email}")

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para la notificación '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'update_provided_notification',  # Plantilla específica para este evento
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        # Usar email crudo para updated_by_user, como funcionó antes
        updated_by_raw_email = updated_by_user.email
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        update_message_escaped = escape_markdown_v2(update_message)
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"💬 *Update Provided for Request {req_code_escaped}* 💬\n\n"
            f"By: {escape_markdown_v2(updated_by_raw_email)}\n"  # Email crudo, pero el "By:" sí se escapa
            f"*Message:*\n{update_message_escaped}\n\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
        else:
            logger.warning(
                f"No Telegram chat_id configurado para recibir la notificación de '{current_event_key}' para {request_obj.unique_code}.")

    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no están configurados para '{current_event_key}' de {request_obj.unique_code}.")

#7
def notify_request_blocked(request_pk, blocked_by_user_pk, block_reason, http_request_host=None,
                           http_request_scheme=None):
    """
    Notifica cuando una solicitud ha sido marcada como Bloqueada.
    Principalmente notifica al creador original de la solicitud.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_BLOCKED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent'
        ).get(pk=request_pk)
        blocked_by_user = CustomUser.objects.get(pk=blocked_by_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: User (blocked_by_user) con pk {blocked_by_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} needs your input"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'blocked_by_user': blocked_by_user,
            'block_reason_text': block_reason,
            'recipient_user_email': request_obj.requested_by.email if request_obj.requested_by else "User",
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')

        if request_obj.requested_by and request_obj.requested_by.email:
            recipients_email_set.add(request_obj.requested_by.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al creador original {request_obj.requested_by.email}")
        else:
            logger.warning(
                f"'{current_event_key}' para {request_obj.unique_code}: No se pudo encontrar el email del creador original.")

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para la notificación '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_blocked_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar email crudo para blocked_by_user, como hemos hecho para otros emails en Telegram
        blocked_by_raw_email = blocked_by_user.email
        block_reason_escaped = escape_markdown_v2(block_reason)
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"🚫 *Request Blocked* 🚫\n\n"
            f"Request *{req_code_escaped}* was flagged as blocked by {escape_markdown_v2(blocked_by_raw_email)}\\.\n"  # Email crudo, punto final escapado
            f"*Reason:*\n{block_reason_escaped}\n\n"
            f"[View Request Details and Resolve]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no están configurados para '{current_event_key}' de {request_obj.unique_code}.")

#8
def notify_request_resolved(request_pk, resolved_by_user_pk, resolution_message, http_request_host=None,
                            http_request_scheme=None):
    """
    Notifica cuando una solicitud previamente bloqueada ha sido resuelta.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_RESOLVED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'update_requested_by'
        ).get(pk=request_pk)
        resolved_by_user = CustomUser.objects.get(pk=resolved_by_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: User (resolved_by_user) con pk {resolved_by_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was resolved"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'resolved_by_user': resolved_by_user,
            'resolution_message_text': resolution_message,
            'recipient_user_email': "",  # Se puede ajustar si es necesario para el saludo en la plantilla
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')

        if request_obj.requested_by and request_obj.requested_by.email:
            recipients_email_set.add(request_obj.requested_by.email)
            # Actualizar el email para el saludo en la plantilla si el creador es el principal notificado
            if not email_context['recipient_user_email']:  # Solo si no se ha establecido antes
                email_context['recipient_user_email'] = request_obj.requested_by.email

        last_block_message = BlockedMessage.objects.filter(request=request_obj).order_by('-blocked_at').first()
        if last_block_message and last_block_message.blocked_by and last_block_message.blocked_by.email:
            recipients_email_set.add(last_block_message.blocked_by.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá a quien bloqueó {last_block_message.blocked_by.email}")

        if request_obj.operator and request_obj.operator.email:
            recipients_email_set.add(request_obj.operator.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al operador {request_obj.operator.email}")

        if not email_context['recipient_user_email']:  # Fallback para el saludo
            email_context['recipient_user_email'] = "User"

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para la notificación '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_resolved_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar email crudo para resolved_by_user en Telegram
        resolved_by_raw_email = resolved_by_user.email
        resolution_message_escaped = escape_markdown_v2(resolution_message)
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"✅ *Request Resolved* ✅\n\n"
            f"Request *{req_code_escaped}* was resolved by {escape_markdown_v2(resolved_by_raw_email)}\\.\n"  # Email crudo, punto final escapado
            f"*Resolution Message:*\n{resolution_message_escaped}\n\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados para '{current_event_key}' de {request_obj.unique_code}.")

#9
def notify_request_sent_to_qa(request_pk, operator_user_pk, http_request_host=None, http_request_scheme=None):
    """
    Notifica cuando una solicitud ha sido enviada a la cola de QA.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_SENT_TO_QA
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related('requested_by', 'operator').get(pk=request_pk)
        operator_user = CustomUser.objects.get(pk=operator_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: User (operator) con pk {operator_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was sent to QA"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'operator_user': operator_user,
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        email_recipient_list = ['oscarmbv@gmail.com']  # Temporal
        # Podrías añadir a un grupo de QA aquí o al creador original

        logger.info(
            f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
        send_request_notification_email(
            subject,
            'sent_to_qa_notification',  # Plantilla específica
            email_context,
            email_recipient_list,
            request_obj=request_obj,
        )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar email crudo para el operador en Telegram
        operator_raw_email = operator_user.email
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"➡️ Request *{req_code_escaped}* was sent to QA by {escape_markdown_v2(operator_raw_email)}\\.\n"  # Email crudo, punto final escapado
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados para '{current_event_key}' de {request_obj.unique_code}.")

#10
def notify_request_rejected(request_pk, rejected_by_user_pk, rejection_reason, http_request_host=None,
                            http_request_scheme=None):
    """
    Notifica cuando una solicitud ha sido rechazada (generalmente desde QA).
    Principalmente notifica al operador asignado.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_REJECTED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent'
        ).get(pk=request_pk)
        rejected_by_user = CustomUser.objects.get(pk=rejected_by_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: User (rejected_by_user) con pk {rejected_by_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was rejected by {rejected_by_user.email}"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'rejected_by_user': rejected_by_user,
            'rejection_reason_text': rejection_reason,
            'recipient_user_email': "",  # Para el saludo, se puede ajustar
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')

        if request_obj.operator and request_obj.operator.email:
            recipients_email_set.add(request_obj.operator.email)
            logger.info(
                f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al operador {request_obj.operator.email}")
            # Ajustar el saludo para el operador
            if not email_context['recipient_user_email']:
                email_context['recipient_user_email'] = request_obj.operator.email
        else:
            logger.warning(
                f"'{current_event_key}' para {request_obj.unique_code}: No hay operador asignado con email para notificar.")
            if not email_context['recipient_user_email']:  # Fallback si no hay operador
                email_context['recipient_user_email'] = "Team"

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_rejected_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar email crudo para rejected_by_user en Telegram
        rejected_by_raw_email = rejected_by_user.email
        rejection_reason_escaped = escape_markdown_v2(rejection_reason)
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"❌ *Request Rejected* ❌\n\n"
            f"Request *{req_code_escaped}* was rejected by {escape_markdown_v2(rejected_by_raw_email)}\\.\n"  # Email crudo, punto final escapado
            f"*Reason:*\n{rejection_reason_escaped}\n\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(
            f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados para '{current_event_key}' de {request_obj.unique_code}.")

#11
def notify_request_cancelled(request_pk, cancelled_by_user_pk, http_request_host=None, http_request_scheme=None):
    """
    Notifica cuando una solicitud ha sido cancelada.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_CANCELLED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent'
        ).get(pk=request_pk)
        cancelled_by_user = CustomUser.objects.get(pk=cancelled_by_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: User (cancelled_by_user) con pk {cancelled_by_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was cancelled by {cancelled_by_user.email}"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'cancelled_by_user': cancelled_by_user,
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')

        if request_obj.operator and request_obj.operator.email:
            recipients_email_set.add(request_obj.operator.email)
        if request_obj.qa_agent and request_obj.qa_agent.email:
            recipients_email_set.add(request_obj.qa_agent.email)
        if request_obj.requested_by and request_obj.requested_by.email:
            if request_obj.requested_by.pk != cancelled_by_user.pk:
                recipients_email_set.add(request_obj.requested_by.email)
                logger.info(
                    f"Notificación '{current_event_key}' para {request_obj.unique_code}: Se añadirá al creador original {request_obj.requested_by.email} (diferente de quien canceló).")
            else:
                logger.info(
                    f"Notificación '{current_event_key}' para {request_obj.unique_code}: El creador original ({request_obj.requested_by.email}) es quien canceló, no se duplicará notificación.")

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_cancelled_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar email crudo para cancelled_by_user en Telegram
        cancelled_by_raw_email = cancelled_by_user.email
        url_for_telegram_link = request_url

        telegram_message_text = (
            f"🛑 *Request Cancelled* 🛑\n\n"
            f"Request *{req_code_escaped}* was cancelled by {escape_markdown_v2(cancelled_by_raw_email)}\\.\n"  # Email crudo, punto final escapado
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(
            f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados para '{current_event_key}' de {request_obj.unique_code}.")

#12
def notify_request_uncancelled(request_pk, uncancelled_by_user_pk, original_cancelled_by_user_pk,
                               http_request_host=None, http_request_scheme=None):
    """
    Notifica cuando una solicitud previamente cancelada ha sido descancelada.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_UNCANCELLED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent'
        ).get(pk=request_pk)
        uncancelled_by_user = CustomUser.objects.get(pk=uncancelled_by_user_pk)

        original_cancelled_by_user = None
        if original_cancelled_by_user_pk:
            try:
                original_cancelled_by_user = CustomUser.objects.get(pk=original_cancelled_by_user_pk)
            except CustomUser.DoesNotExist:
                logger.warning(
                    f"{current_event_key}: Original cancelled_by_user with pk {original_cancelled_by_user_pk} not found.")

    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(
            f"{current_event_key}: User (uncancelled_by_user) con pk {uncancelled_by_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was un-cancelled by {uncancelled_by_user.email}"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'uncancelled_by_user': uncancelled_by_user,
            'original_cancelled_by_user': original_cancelled_by_user,
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')

        if request_obj.operator and request_obj.operator.email:
            recipients_email_set.add(request_obj.operator.email)
        if request_obj.qa_agent and request_obj.qa_agent.email:
            recipients_email_set.add(request_obj.qa_agent.email)
        if request_obj.requested_by and request_obj.requested_by.email:
            if request_obj.requested_by.pk != uncancelled_by_user.pk:
                recipients_email_set.add(request_obj.requested_by.email)
        if original_cancelled_by_user and original_cancelled_by_user.email:
            if original_cancelled_by_user.pk != uncancelled_by_user.pk:
                recipients_email_set.add(original_cancelled_by_user.email)

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para la notificación '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_uncancelled_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped_for_bold = escape_markdown_v2(request_obj.unique_code)
        uncancelled_by_email_escaped = escape_markdown_v2(uncancelled_by_user.email)

        text_part1 = escape_markdown_v2("Request ")
        text_part2 = escape_markdown_v2(f" was un-cancelled by ")
        text_part3 = escape_markdown_v2(f" and is now 'Pending'.")

        url_for_telegram_link = request_url

        telegram_message_text = (
            f"🔄 *Request Un\\-cancelled* 🔄\n\n"
            f"{text_part1}*{req_code_escaped_for_bold}*{text_part2}{uncancelled_by_email_escaped}{text_part3}\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        logger.info(
            f"Final Telegram message to be sent for {current_event_key} {request_obj.unique_code} to chat_id {settings.TELEGRAM_DEFAULT_CHAT_ID}:\n>>>\n{telegram_message_text}\n<<<")

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados para '{current_event_key}' de {request_obj.unique_code}.")

#13
def notify_request_completed(request_pk, qa_user_pk, http_request_host=None, http_request_scheme=None):
    """
    Notifica cuando una solicitud ha sido completada.
    """
    # ----> 1. USA LA CONSTANTE DEL EVENTO <----
    current_event_key = EVENT_KEY_REQUEST_COMPLETED
    logger.info(f"Processing notification for event '{current_event_key}', request_pk: {request_pk}")

    try:
        request_obj = UserRecordsRequest.objects.select_related(
            'requested_by', 'operator', 'qa_agent'
        ).get(pk=request_pk)
        qa_completer_user = CustomUser.objects.get(pk=qa_user_pk)
    except UserRecordsRequest.DoesNotExist:
        logger.error(f"{current_event_key}: UserRecordsRequest con pk {request_pk} no encontrada.")
        return
    except CustomUser.DoesNotExist:
        logger.error(f"{current_event_key}: User (qa_completer_user) con pk {qa_user_pk} no encontrado.")
        return

    # ---- Preparación de datos comunes (URL) ----
    temp_request_for_url_build = None
    if http_request_host and http_request_scheme:
        from django.http import HttpRequest
        temp_request_for_url_build = HttpRequest()
        temp_request_for_url_build.META['HTTP_HOST'] = http_request_host
        temp_request_for_url_build.META['wsgi.url_scheme'] = http_request_scheme
    request_url = get_absolute_url_for_request(request_obj, temp_request_for_url_build)

    # ---- Lógica de Email (solo si está habilitado) ----
    # ----> 2. VERIFICA EL TOGGLE ANTES DE ENVIAR EL EMAIL <----
    if is_email_notification_enabled(current_event_key):
        subject = f"Request {request_obj.unique_code} was completed"

        email_context = {
            'subject': subject,
            'request_obj': request_obj,
            'qa_completer_user': qa_completer_user,
            # request_url se añade dentro de send_request_notification_email
        }

        # ---- Destinatarios de Email ----
        recipients_email_set = set()
        recipients_email_set.add('oscarmbv@gmail.com')  # Tu correo temporal

        # 1. Usuario que creó originalmente la solicitud (Requested By)
        if request_obj.requested_by and request_obj.requested_by.email:
            recipients_email_set.add(request_obj.requested_by.email)

        # 2. Operador asignado (Operated By)
        if request_obj.operator and request_obj.operator.email:
            recipients_email_set.add(request_obj.operator.email)

        if qa_completer_user and qa_completer_user.email:
            recipients_email_set.add(qa_completer_user.email)

        email_recipient_list = list(recipients_email_set)

        if not email_recipient_list:
            logger.warning(
                f"No hay destinatarios de correo válidos para '{current_event_key}' de {request_obj.unique_code}.")
        else:
            logger.info(
                f"Preparando email de '{current_event_key}' para {request_obj.unique_code} a: {email_recipient_list}")
            send_request_notification_email(
                subject,
                'request_completed_notification',  # Plantilla específica
                email_context,
                email_recipient_list,
                request_obj=request_obj,
            )
    else:
        logger.info(
            f"Email sending SKIPPED for event '{current_event_key}' for request {request_obj.unique_code} due to admin toggle.")

    # ---- Notificación de Telegram (se envía independientemente del toggle de email por ahora) ----
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_DEFAULT_CHAT_ID:
        req_code_escaped = escape_markdown_v2(request_obj.unique_code)
        # Usar emails crudos
        operator_raw_email = request_obj.operator.email if request_obj.operator else "N/A"
        qa_by_raw_email = qa_completer_user.email

        tat_display = "N/A"
        if request_obj.calculated_turn_around_time:
            delta = request_obj.calculated_turn_around_time
            total_seconds = int(delta.total_seconds())
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            parts = []
            if days > 0: parts.append(f"{days}d")
            if hours > 0: parts.append(f"{hours}h")
            if minutes > 0 or not parts: parts.append(f"{minutes}m")
            tat_display = escape_markdown_v2(" ".join(parts) if parts else "0m")

        notes_line_telegram = ""
        if request_obj.operating_notes:
            notes_line_telegram = f"\n*Notes:*\n{escape_markdown_v2(request_obj.operating_notes)}"

        url_for_telegram_link = request_url

        telegram_message_text = (
            f"✅ *Request Completed* ✅\n\n"
            f"Request *{req_code_escaped}* was completed\\.\n"  # Punto escapado
            f"Operated by: {escape_markdown_v2(operator_raw_email)}\n"
            f"QA by: {escape_markdown_v2(qa_by_raw_email)}\n"
            f"Turn Around Time: {tat_display}"
            f"{notes_line_telegram}\n\n"
            f"[View Request Details]({url_for_telegram_link})"
        )

        telegram_recipient_chat_id = settings.TELEGRAM_DEFAULT_CHAT_ID

        logger.info(f"Preparando mensaje de Telegram '{current_event_key}' para {request_obj.unique_code} a chat_id: {telegram_recipient_chat_id}")
        if telegram_recipient_chat_id:
            send_telegram_message(
                settings.TELEGRAM_BOT_TOKEN,
                telegram_recipient_chat_id,
                telegram_message_text
            )
    else:
        logger.warning(f"TELEGRAM_BOT_TOKEN o TELEGRAM_DEFAULT_CHAT_ID no configurados para '{current_event_key}' de {request_obj.unique_code}.")