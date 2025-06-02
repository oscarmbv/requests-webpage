# tasks/salesforce_sync.py

import logging
from collections import defaultdict
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed, SalesforceError
from .models import UserRecordsRequest, SalesforceAttachmentLog, CustomUser, ScheduledTaskToggle
from .choices import PRIORITY_NORMAL, TEAM_REVENUE
from django_q.tasks import async_task

# Configuración del logger
logger = logging.getLogger(__name__)
SALESFORCE_SYNC_TASK_NAME = 'salesforce_sync_opportunities'

SALESFORCE_SYSTEM_USER_EMAIL = 'invisibletech@sayrhino.com'  # Cambia esto si es necesario


def get_salesforce_system_user():
    """
    Obtiene o crea el usuario del sistema para Salesforce.
    """
    try:
        user = CustomUser.objects.get(email=SALESFORCE_SYSTEM_USER_EMAIL)
    except CustomUser.DoesNotExist:
        logger.warning(f"Usuario del sistema de Salesforce '{SALESFORCE_SYSTEM_USER_EMAIL}' no encontrado. Intentando crear uno.")

        raise CustomUser.DoesNotExist(
            f"El usuario del sistema de Salesforce con email '{SALESFORCE_SYSTEM_USER_EMAIL}' no existe. "
            f"Por favor, créalo manualmente en el admin de Django."
        )
    return user


def sync_salesforce_opportunities_task():
    """
    Tarea principal para sincronizar Opportunities de Salesforce y crear UserRecordsRequests.
    """
    logger.info(f"Iniciando la tarea '{SALESFORCE_SYNC_TASK_NAME}'...")

    try:
        task_toggle, created = ScheduledTaskToggle.objects.get_or_create(task_name=SALESFORCE_SYNC_TASK_NAME, defaults={'is_enabled': True})
        if created:
            logger.info(f"Registro de control para la tarea '{SALESFORCE_SYNC_TASK_NAME}' creado y habilitado por defecto.")

        if not task_toggle.is_enabled:
            logger.info(f"La tarea '{SALESFORCE_SYNC_TASK_NAME}' está actualmente pausada en la configuración. Saltando ejecución.")
            return f"Task '{SALESFORCE_SYNC_TASK_NAME}' paused. Did not run."
    except Exception as e:
        logger.error(f"Error al verificar el estado de la tarea '{SALESFORCE_SYNC_TASK_NAME}': {e}", exc_info=True)
        return f"Error checking status for task '{SALESFORCE_SYNC_TASK_NAME}'. Aborting."

    logger.info(f"La tarea '{SALESFORCE_SYNC_TASK_NAME}' está habilitada. Procediendo con la sincronización.")

    # Obtener credenciales desde Django settings (configuradas con django-environ)
    sf_username = settings.SF_USERNAME
    sf_password = settings.SF_PASSWORD
    sf_security_token = settings.SF_SECURITY_TOKEN
    sf_consumer_key = settings.SF_CONSUMER_KEY
    sf_consumer_secret = settings.SF_CONSUMER_SECRET
    sf_domain = settings.SF_DOMAIN
    sf_version = settings.SF_VERSION
    salesforce_lightning_base_url = settings.SALESFORCE_LIGHTNING_BASE_URL

    # Verificar que todas las credenciales necesarias estén presentes
    required_sf_credentials = {
        "SF_USERNAME": sf_username,
        "SF_PASSWORD": sf_password,
        "SF_SECURITY_TOKEN": sf_security_token,
        "SF_CONSUMER_KEY": sf_consumer_key,
        "SF_CONSUMER_SECRET": sf_consumer_secret,
    }
    missing_credentials = [key for key, value in required_sf_credentials.items() if not value]
    if missing_credentials:
        logger.error(f"Faltan las siguientes variables de entorno de Salesforce: {', '.join(missing_credentials)}. Abortando tarea.")
        return "Error: Credenciales de Salesforce incompletas."

    sf_connection = None
    try:
        logger.info(f"Intentando conectar a Salesforce (dominio: {sf_domain}, usuario: {sf_username})...")
        sf_connection = Salesforce(
            username=sf_username,
            password=sf_password,
            security_token=sf_security_token,
            consumer_key=sf_consumer_key,
            consumer_secret=sf_consumer_secret,
            domain=sf_domain,
            version=sf_version
        )
        logger.info(f"¡Conexión exitosa a Salesforce! Instancia: {sf_connection.sf_instance}")

        soql_query_opportunities = """
        SELECT
            Id,
            Opportunity_ID__c,
            Account_Name__c, 
            Number_of_Units__c,
            Account_Manager__c,
            Name,
            Closed_Won_Date__c,
            Leasing_Integration_Software_c__c,
            Information_Needed_For_Assets__c
        FROM
            Opportunity
        WHERE
            StageName = '5-Closed Won'
            AND OwnerId <> '005f40000052NHqAAM'
            AND Exclude_from_reporting__c = false
            AND assets_uploaded__c = false
            AND Assets_Converted__c = false
            AND Send_Opportunity_to_Jetty__c = 'No'
            AND Invisible_Status__c = 'New'
            AND Closed_Won_Date__c >= 2022-06-01T00:00:00.000Z
            AND RecordTypeId IN ('012Jw000005irCDIAY', '012Jw000005ohmrIAA', '012Jw000005irDpIAI')
            AND Type IN ('SDI & Cash', 'SDI', 'Portal Audit')
        ORDER BY Closed_Won_Date__c
        """

        logger.info("Ejecutando consulta SOQL para Opportunities...")
        opp_query_result = sf_connection.query_all(soql_query_opportunities)
        opportunities = opp_query_result.get('records', [])
        logger.info(f"Consulta de Opportunities completada. Total encontradas: {len(opportunities)}")

        if not opportunities:
            logger.info("No se encontraron nuevas Opportunities para procesar.")
            return "No nuevas Opportunities encontradas."

        # Obtener el usuario del sistema una vez
        try:
            system_user = get_salesforce_system_user()
        except CustomUser.DoesNotExist as e:
            logger.error(str(e))
            return f"Error: {str(e)}"

        processed_count = 0
        skipped_count = 0

        for opp in opportunities:
            opportunity_sf_id = opp.get('Id')  # ID de Salesforce de la Opportunity
            opportunity_custom_id = opp.get('Opportunity_ID__c')

            if not opportunity_custom_id:
                logger.warning(
                    f"Opportunity con SF ID {opportunity_sf_id} no tiene valor en Opportunity_ID__c. Omitiendo.")
                skipped_count += 1
                continue

            logger.info(f"Procesando Opportunity: SF ID {opportunity_sf_id}, Custom ID {opportunity_custom_id}")


            #if UserRecordsRequest.objects.filter(address_validation_opportunity_id=opportunity_custom_id).exists():
            #    logger.info(f"UserRecordsRequest para Opportunity Custom ID {opportunity_custom_id} ya existe. Omitiendo.")
            #    skipped_count += 1
            #    continue

            try:
                with transaction.atomic():
                    creation_timestamp = timezone.now()

                    partner_name_sf = opp.get('Account_Name__c')
                    account_manager_sf = opp.get('Account_Manager__c')

                    closed_won_date_str = opp.get('Closed_Won_Date__c')
                    salesforce_closed_won_date_obj = None
                    if closed_won_date_str:
                        try:
                            # Tomar solo la parte YYYY-MM-DD de la cadena
                            salesforce_closed_won_date_obj = closed_won_date_str[:10]
                            # Verificación adicional del formato (opcional, pero bueno para depurar)
                            # from datetime import datetime
                            # datetime.strptime(salesforce_closed_won_date_obj, '%Y-%m-%d')
                            logger.debug(f"Formatted ClosedWonDate for Opp ID {opportunity_sf_id}: {salesforce_closed_won_date_obj}")
                        except (ValueError, TypeError) as e_date:
                            logger.warning(f"Could not parse/format date from ClosedWonDate string: '{closed_won_date_str}' for Opp ID {opportunity_sf_id}. Error: {e_date}. Leaving it None.")
                            salesforce_closed_won_date_obj = None # Asegurar que sea None si el parseo/formato falla

                    new_request = UserRecordsRequest.objects.create(
                        requested_by=system_user,
                        type_of_process='address_validation',
                        # Mapeo de campos según el plan y tu script:
                        partner_name=partner_name_sf,
                        address_validation_opportunity_id=opportunity_custom_id,  # Este es Opportunity_ID__c
                        salesforce_standard_opp_id=opportunity_sf_id,
                        salesforce_opportunity_name=opp.get('Name'),
                        salesforce_number_of_units=opp.get('Number_of_Units__c'),
                        salesforce_link=f"{salesforce_lightning_base_url}/Opportunity/{opportunity_sf_id}/view",
                        salesforce_account_manager=account_manager_sf,
                        # Asegúrate que el formato de fecha de Salesforce sea compatible con DateField.
                        # ClosedWonDate usualmente viene como 'YYYY-MM-DD'.
                        salesforce_closed_won_date=salesforce_closed_won_date_obj,
                        salesforce_leasing_integration_software=opp.get('Leasing_Integration_Software_c__c'),
                        salesforce_information_needed_for_assets=opp.get('Information_Needed_For_Assets__c'),
                        # Valores por defecto:
                        status='pending',
                        priority=PRIORITY_NORMAL,  # Asegúrate que PRIORITY_NORMAL esté importado/definido
                        team=TEAM_REVENUE,  # O el equipo que corresponda a Address Validation
                        timestamp=creation_timestamp,
                        effective_start_time_for_tat=creation_timestamp,
                        # Otros campos opcionales que quieras llenar por defecto
                    )
                    logger.info(f"Creado UserRecordsRequest {new_request.unique_code} para Opportunity SF ID {opportunity_sf_id}")

                    #Notificacion
                    try:
                        async_task(
                            'tasks.notifications.notify_new_request_created',
                            new_request.pk,
                            task_name=f"NotifyNewSalesforceRequest-{new_request.unique_code}",
                            hook='tasks.hooks.print_task_result'
                        )
                        logger.info(
                            f"Tarea de notificación para nueva solicitud SF {new_request.unique_code} encolada.")
                    except Exception as e_async_sf:
                        logger.error(
                            f"Error al encolar la tarea de notificación para solicitud SF {new_request.unique_code}: {e_async_sf}", exc_info=True)

                    # --- 3. Creación de SalesforceAttachmentLog ---
                    # (Salesforce Implementation.pdf, Paso 3.2, sección "Creación de SalesforceAttachmentLog")
                    # Primero, obtener los ContentDocumentIds vinculados a esta Opportunity
                    cdl_soql_query = f"SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId = '{opportunity_sf_id}'"
                    cdl_result = sf_connection.query_all(cdl_soql_query)
                    content_document_links = cdl_result.get('records', [])

                    if content_document_links:
                        content_document_ids = [link['ContentDocumentId'] for link in content_document_links]
                        formatted_doc_ids = ",".join([f"'{doc_id}'" for doc_id in content_document_ids])

                        # Luego, obtener Title y FileExtension de ContentVersion para esos ContentDocumentIds
                        cv_soql_query = f"SELECT ContentDocumentId, Title, FileExtension FROM ContentVersion WHERE ContentDocumentId IN ({formatted_doc_ids}) AND IsLatest = true"
                        cv_result = sf_connection.query_all(cv_soql_query)
                        content_versions = cv_result.get('records', [])

                        for cv in content_versions:
                            file_title = cv.get('Title', 'Untitled')
                            file_ext = cv.get('FileExtension', '')
                            full_file_name = f"{file_title}.{file_ext}" if file_ext else file_title

                            attachment_sf_link = f"{salesforce_lightning_base_url}/ContentDocument/{cv.get('ContentDocumentId')}/view"

                            SalesforceAttachmentLog.objects.create(
                                request=new_request,
                                file_name=full_file_name,
                                file_extension=file_ext,
                                salesforce_file_link=attachment_sf_link
                            )
                        logger.info(f"Registrados {len(content_versions)} adjuntos de Salesforce para la solicitud {new_request.unique_code}")

                    # --- 4. Actualización en Salesforce ---
                    # (Salesforce Implementation.pdf, Paso 3.2, sección "Actualización en Salesforce")
                    # Actualizar el campo Invisible_Status__c de la Opportunity a "In Progress"
                    sf_connection.Opportunity.update(opportunity_sf_id, {'Invisible_Status__c': 'In Progress'})
                    logger.info(f"Actualizado Invisible_Status__c a 'In Progress' para Opportunity SF ID {opportunity_sf_id}")

                    processed_count += 1

            except Exception as e:  # Captura errores durante el procesamiento de una Opportunity específica
                logger.error(
                    f"Error procesando Opportunity SF ID {opportunity_sf_id} (Custom ID {opportunity_custom_id}): {e}",
                    exc_info=True)
                skipped_count += 1  # O manejar de otra forma, como reintentos.
                # Considerar si se debe continuar con la siguiente Opportunity o abortar la tarea.
                # Por ahora, continuamos.

        logger.info(
            f"Tarea de sincronización finalizada. Procesadas: {processed_count}, Omitidas/Errores: {skipped_count}.")
        return f"Sincronización completada. Procesadas: {processed_count}, Omitidas/Errores: {skipped_count}."

    except SalesforceAuthenticationFailed as e:
        logger.error(f"Error de autenticación en Salesforce: {e}", exc_info=True)
        return f"Error de autenticación: {e}"
    except SalesforceError as e:
        logger.error(f"Error de API de Salesforce: {e.url} - {e.resource_name} - {e.status} - {e.content}",
                     exc_info=True)
        return f"Error de API de Salesforce: {e.content}"
    except CustomUser.DoesNotExist as e:  # Captura el error si el usuario del sistema no existe
        logger.error(str(e))
        return f"Error crítico: {str(e)}"
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado durante la sincronización con Salesforce: {e}", exc_info=True)
        return f"Error inesperado: {e}"
    finally:
        logger.info("--- Fin de la tarea de sincronización de Salesforce ---")