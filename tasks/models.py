# tasks/models.py

import logging
import pytz
import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from django.utils.timezone import now
from .validators import validate_file_size
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

# Importa las choices desde el archivo centralizado
from .choices import (
    TYPE_CHOICES, STATUS_CHOICES, DEACTIVATION_TOGGLE_CHOICES, LEADERSHIP_APPROVAL_CHOICES,
    UNIT_TRANSFER_TYPE_CHOICES, UNIT_TRANSFER_LANDLORD_TYPE_CHOICES, XML_STATE_CHOICES,
    PROPERTY_RECORDS_TYPE_CHOICES, PROPERTY_TYPE_CHOICES, COVERAGE_TYPE_CHOICES,
    COVERAGE_MULTIPLIER_CHOICES, INTEGRATION_TYPE_CHOICES, TEAM_CHOICES,
    PRIORITY_CHOICES, PRIORITY_NORMAL
)

logger = logging.getLogger(__name__) # Logger específico para esta app


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que usa email como identificador principal
    y añade soporte para zona horaria.
    """
    email = models.EmailField(unique=True)
    timezone = models.CharField(
        max_length=100,
        default='UTC',
        choices=[(tz, tz) for tz in pytz.common_timezones] # Genera choices de pytz
    )

    # Campo receive_notifications (si lo tienes, mantenlo)
    # receive_notifications = models.BooleanField(default=True)

    # Usa email para login en lugar de username
    USERNAME_FIELD = 'email'
    # username sigue siendo necesario para Django por defecto, pero no para login
    REQUIRED_FIELDS = ['username']

    slack_member_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Slack User Id for notifications (optional)"
    )

    def __str__(self):
        return self.email


class UserRecordsRequest(models.Model):

    type_of_process = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default='user_records',
        db_index=True # Optimiza filtros por tipo
    )
    unique_code = models.CharField(max_length=20, unique=True, editable=False)
    timestamp = models.DateTimeField(default=now, db_index=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_requests'
    )
    team = models.CharField(
        max_length=20,
        choices=TEAM_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Assigned Team"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL,  # Establecer 'Normal' como valor por defecto en DB
        db_index=True,
        verbose_name="Priority"
    )
    partner_name = models.CharField(max_length=255, blank=True, null=True, db_index=True) # Índice para búsqueda
    properties = models.TextField(blank=True, null=True, verbose_name="Properties Affected")
    user_groups_data = models.JSONField(null=True, blank=True) # Datos para User Records
    special_instructions = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True # Optimiza filtros por estado
    )
    update_needed_flag = models.BooleanField(
        default=False,
        verbose_name="Update Needed Flag",
        help_text="Indicates if the requester/team needs a progress update."
    )
    update_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_records_update_requested_by', # related_name específico
        null=True,  # Puede ser nulo si no hay solicitud o si se limpia
        blank=True, # Puede estar en blanco en el admin/formularios
        on_delete=models.SET_NULL, # Si el usuario se elimina, se pone a NULL
        verbose_name="Update Requested By"
    )
    update_requested_at = models.DateTimeField(
        null=True,  # Puede ser nulo
        blank=True, # Puede estar en blanco
        verbose_name="Update Requested At"
    )
    user_file = models.FileField(
        upload_to='user_uploads/', # Directorio base para archivos subidos
        null=True, blank=True,
        validators=[validate_file_size],
        verbose_name='Upload File' # Label genérico, sobreescribir en forms si es necesario
    )
    user_link = models.URLField(max_length=200, blank=True, null=True)

    # --- NUEVO CAMPO PARA LA FECHA DE PROGRAMACIÓN ---
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Scheduled Date",
        help_text="Date for which the request is scheduled to become active (pending)."
    )
    effective_start_time_for_tat = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Effective Start Time for TAT",
        help_text="Timestamp marking the real start of the work cycle for TAT calculation."
    )

    # --- Campos de Flujo de Trabajo y Asignación ---
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='operated_requests',
        db_index=True # Índice para filtros
    )
    qa_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='qa_requests',
        db_index=True # Índice para filtros
    )
    operated_at = models.DateTimeField(null=True, blank=True, db_index=True) # Timestamp inicio operación
    qa_pending_at = models.DateTimeField(null=True, blank=True) # Timestamp envío a QA
    qa_in_progress_at = models.DateTimeField(null=True, blank=True) # Timestamp inicio QA
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True) # Timestamp completado
    cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True, null=True) # Razón simple, podría ir a historial
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='%(class)s_cancelled_by',null=True,blank=True,on_delete=models.SET_NULL)

    uncanceled_at = models.DateTimeField(null=True, blank=True)
    uncanceled_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='%(class)s_uncancelled_by',null=True,blank=True,on_delete=models.SET_NULL)

    is_rejected_previously = models.BooleanField(
        default=False,
        verbose_name="Previously Rejected by QA",
        help_text="Indicates if the request was rejected by QA and needs re-submission to QA."
    )

    # --- Campos de Detalles de Operación (Comunes) ---
    num_updated_users = models.PositiveIntegerField(null=True, blank=True)
    num_updated_properties = models.PositiveIntegerField(null=True, blank=True)
    bulk_updates = models.PositiveIntegerField(null=True, blank=True)
    manual_updated_properties = models.PositiveIntegerField(null=True, blank=True)
    manual_updated_units = models.PositiveIntegerField(null=True, blank=True, verbose_name="Manual Updated Units")
    update_by_csv_rows = models.PositiveIntegerField(null=True, blank=True)
    processing_reports_rows = models.PositiveIntegerField(null=True, blank=True)
    operator_spreadsheet_link = models.URLField(max_length=1024, blank=True, null=True,verbose_name="Operator Spreadsheet Link")
    operating_notes = models.TextField(blank=True, null=True)

    # --- Campos Específicos: Deactivation and Toggle ---
    deactivation_toggle_type = models.CharField(max_length=50, choices=DEACTIVATION_TOGGLE_CHOICES, null=True, blank=True)
    deactivation_toggle_active_policies = models.BooleanField(null=True, blank=True)
    deactivation_toggle_properties_with_policies = models.TextField(blank=True, null=True)
    deactivation_toggle_context = models.TextField(blank=True, null=True)
    deactivation_toggle_leadership_approval = models.CharField(max_length=50, choices=LEADERSHIP_APPROVAL_CHOICES, null=True, blank=True)
    deactivation_toggle_marked_as_churned = models.BooleanField(null=True, blank=True)

    # --- Campos Específicos: Unit Transfers ---
    unit_transfer_type = models.CharField(max_length=50, choices=UNIT_TRANSFER_TYPE_CHOICES, null=True, blank=True)
    unit_transfer_new_partner_prospect_name = models.CharField(max_length=255, null=True, blank=True)
    unit_transfer_receiving_partner_psm = models.CharField(max_length=255, null=True, blank=True)
    unit_transfer_new_policyholders = models.TextField(blank=True, null=True)
    unit_transfer_user_email_addresses = models.TextField(blank=True, null=True)
    unit_transfer_prospect_portfolio_size = models.PositiveIntegerField(null=True, blank=True)
    unit_transfer_prospect_landlord_type = models.CharField(max_length=50, choices=UNIT_TRANSFER_LANDLORD_TYPE_CHOICES, null=True, blank=True)
    unit_transfer_proof_of_sale = models.URLField(max_length=200, blank=True, null=True)

    # --- Campos Específicos: Generating XML files ---
    xml_state = models.CharField(max_length=2, choices=XML_STATE_CHOICES, null=True, blank=True)
    xml_carrier_rvic = models.BooleanField(default=False)
    xml_carrier_ssic = models.BooleanField(default=False)
    xml_rvic_zip_file = models.FileField(upload_to='xml_zip_files/', null=True, blank=True, validators=[validate_file_size])
    xml_ssic_zip_file = models.FileField(upload_to='xml_zip_files/', null=True, blank=True, validators=[validate_file_size])

    # --- Campos Específicos: Generating XML files (Output) ---
    operator_rvic_file_slot1 = models.FileField(upload_to='operator_xml_files/', null=True, blank=True,validators=[validate_file_size],help_text="Slot 1 for RVIC file uploaded by operator.")
    operator_rvic_file_slot2 = models.FileField(upload_to='operator_xml_files/', null=True, blank=True,validators=[validate_file_size],help_text="Slot 2 for RVIC file (e.g., ZIP for UT_RVIC) by operator.")
    operator_ssic_file_slot1 = models.FileField(upload_to='operator_xml_files/', null=True, blank=True,validators=[validate_file_size],help_text="Slot 1 for SSIC file uploaded by operator.")
    operator_ssic_file_slot2 = models.FileField(upload_to='operator_xml_files/', null=True, blank=True,validators=[validate_file_size],help_text="Slot 2 for SSIC file (e.g., ZIP for UT_SSIC) by operator.")

    # --- Campos Específicos: Address Validation ---
    address_validation_policyholders = models.TextField(blank=True, null=True)
    address_validation_opportunity_id = models.CharField(max_length=255, blank=True, null=True)
    address_validation_user_email_addresses = models.TextField(blank=True, null=True)

    # --- Campos Específicos: Stripe Disputes ---
    stripe_premium_disputes = models.PositiveIntegerField(null=True, blank=True,verbose_name="Rhino Super Premium Disputes")
    stripe_ri_disputes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Rhino Super RI Disputes")

    # --- Campos Específicos: Property Records ---
    property_records_type = models.CharField(max_length=50, choices=PROPERTY_RECORDS_TYPE_CHOICES, null=True,blank=True)
    property_records_new_names = models.TextField(blank=True, null=True)
    property_records_new_pmc = models.CharField(max_length=255, blank=True, null=True)
    property_records_new_policyholder = models.TextField(blank=True, null=True)
    property_records_corrected_address = models.TextField(blank=True, null=True)  # TextField simple por ahora
    property_records_updated_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, null=True,blank=True)
    property_records_units = models.TextField(blank=True, null=True)
    property_records_coverage_type = models.CharField(max_length=50, choices=COVERAGE_TYPE_CHOICES, null=True,blank=True)
    property_records_coverage_multiplier = models.CharField(max_length=10, choices=COVERAGE_MULTIPLIER_CHOICES,null=True, blank=True)
    property_records_coverage_amount = models.DecimalField(max_digits=11, decimal_places=2,null=True, blank=True,validators=[MinValueValidator(Decimal('330.00')),MaxValueValidator(Decimal('200000000.00'))])
    property_records_integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPE_CHOICES, null=True,blank=True)
    property_records_integration_codes = models.TextField(blank=True, null=True)
    property_records_bank_details = models.TextField(blank=True, null=True)

    # --- Integración con Salesforce (Address Validation) ---
    salesforce_standard_opp_id = models.CharField(max_length=18,null=True,blank=True,verbose_name="Salesforce Standard Opportunity ID",help_text="The standard 18-character ID of the Opportunity in Salesforce.")
    salesforce_opportunity_name = models.CharField(max_length=255, null=True, blank=True,verbose_name="Salesforce Opportunity Name")
    salesforce_number_of_units = models.PositiveIntegerField(null=True, blank=True,verbose_name="Salesforce Number of Units")
    salesforce_link = models.URLField(max_length=1024, null=True, blank=True,verbose_name="Salesforce Opportunity Link")
    salesforce_account_manager = models.CharField(max_length=255, null=True, blank=True,verbose_name="Salesforce Account Manager")
    salesforce_closed_won_date = models.DateField(null=True, blank=True, verbose_name="Salesforce Closed Won Date")
    salesforce_leasing_integration_software = models.CharField(max_length=255, null=True, blank=True, verbose_name="Salesforce Leasing Integration Software")
    salesforce_information_needed_for_assets = models.TextField(null=True, blank=True, verbose_name="Salesforce Information Needed For Assets")

    # --- Integración con Salesforce (Address Validation) Parametros de Salida ---
    assets_uploaded = models.BooleanField(null=True,blank=True,default=False,verbose_name="Assets Uploaded (AV)")
    av_number_of_units = models.PositiveIntegerField(null=True,blank=True,verbose_name="Number of Units (AV Operation)")
    av_number_of_invalid_units = models.PositiveIntegerField(null=True, blank=True, default=0,verbose_name="Number of Invalid Units (AV Operation)")
    link_to_assets = models.URLField(max_length=1024,null=True,blank=True,verbose_name="Link to Assets (AV)")
    success_output_link = models.URLField(max_length=1024,null=True,blank=True,verbose_name="Success Output Link (AV)")
    failed_output_link = models.URLField(max_length=1024,null=True,blank=True,verbose_name="Failed Output Link (AV)")
    rhino_accounts_created = models.BooleanField(null=True,blank=True,default=False,verbose_name="Rhino Accounts Created? (AV)")

    # Client Price Subtotals at Completion
    subtotal_user_update_client_price_completed = models.DecimalField(verbose_name="User Update Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_property_update_client_price_completed = models.DecimalField(verbose_name="Property Update Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_bulk_update_client_price_completed = models.DecimalField(verbose_name="Bulk Update Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_manual_property_update_client_price_completed = models.DecimalField(verbose_name="Manual Property Update Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_csv_update_client_price_completed = models.DecimalField(verbose_name="CSV Update Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_processing_report_client_price_completed = models.DecimalField(verbose_name="Processing Report Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_manual_unit_update_client_price_completed = models.DecimalField(verbose_name="Manual Unit Update Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_address_validation_unit_client_price_completed = models.DecimalField(verbose_name="Address Validation Unit Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_stripe_dispute_client_price_completed = models.DecimalField(verbose_name="Stripe Dispute Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    subtotal_xml_file_client_price_completed = models.DecimalField(verbose_name="XML File Price Subtotal", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    grand_total_client_price_completed = models.DecimalField(verbose_name="Grand Total Price", max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)

    # Operate Cost Subtotals at Completion
    subtotal_user_update_operate_cost_completed = models.DecimalField(verbose_name="User Update Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_property_update_operate_cost_completed = models.DecimalField(verbose_name="Property Update Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_bulk_update_operate_cost_completed = models.DecimalField(verbose_name="Bulk Update Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_manual_property_update_operate_cost_completed = models.DecimalField(verbose_name="Manual Property Update Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_csv_update_operate_cost_completed = models.DecimalField(verbose_name="CSV Update Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_processing_report_operate_cost_completed = models.DecimalField(verbose_name="Processing Report Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_manual_unit_update_operate_cost_completed = models.DecimalField(verbose_name="Manual Unit Update Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_address_validation_unit_operate_cost_completed = models.DecimalField(verbose_name="Address Validation Unit Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_stripe_dispute_operate_cost_completed = models.DecimalField(verbose_name="Stripe Dispute Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_xml_file_operate_cost_completed = models.DecimalField(verbose_name="XML File Subtotal (Operate Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    grand_total_operate_cost_completed = models.DecimalField(verbose_name="Grand Total (Operate Cost) at Completion", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)

    # QA Cost Subtotals at Completion
    subtotal_user_update_qa_cost_completed = models.DecimalField(verbose_name="User Update Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_property_update_qa_cost_completed = models.DecimalField(verbose_name="Property Update Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_bulk_update_qa_cost_completed = models.DecimalField(verbose_name="Bulk Update Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_manual_property_update_qa_cost_completed = models.DecimalField(verbose_name="Manual Property Update Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_csv_update_qa_cost_completed = models.DecimalField(verbose_name="CSV Update Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_processing_report_qa_cost_completed = models.DecimalField(verbose_name="Processing Report Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_manual_unit_update_qa_cost_completed = models.DecimalField(verbose_name="Manual Unit Update Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_address_validation_unit_qa_cost_completed = models.DecimalField(verbose_name="Address Validation Unit Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_stripe_dispute_qa_cost_completed = models.DecimalField(verbose_name="Stripe Dispute Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    subtotal_xml_file_qa_cost_completed = models.DecimalField(verbose_name="XML File Subtotal (QA Cost)", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)
    grand_total_qa_cost_completed = models.DecimalField(verbose_name="Grand Total (QA Cost) at Completion", max_digits=8, decimal_places=5, null=True, blank=True, default=0.00000)

    discount_percentage = models.DecimalField(
        verbose_name="Discount Percentage",
        max_digits=4,  # Permite valores hasta 999.9, suficiente para 100.0
        decimal_places=1,
        default=Decimal('0.0'),
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('100.0'))
        ],
        help_text="Enter a percentage value (e.g., 15 for 15%) to be discounted from the grand total."
    )

    final_price_client_completed = models.DecimalField(
        verbose_name="Final Price (with discount)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        help_text="The final client price after any discounts have been applied. This field is calculated automatically."
    )

    slack_thread_ts = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Slack Thread Timestamp",
        help_text="El timestamp del mensaje principal de Slack para agrupar notificaciones en un hilo."
    )

    def __str__(self):
        team_display = self.get_team_display() or "Unassigned"
        return f"{self.get_type_of_process_display()} Request ({self.unique_code}) - Team: {team_display}"

    @property
    def calculated_discount_amount(self):
        """
        Calcula el monto monetario del descuento basado en el porcentaje.
        Retorna un objeto Decimal.
        """
        if self.grand_total_client_price_completed is not None and self.discount_percentage is not None:
            if self.discount_percentage > 0:
                # Se asegura de que el cálculo se haga con Decimal para mantener la precisión
                discount_value = self.grand_total_client_price_completed * (
                            self.discount_percentage / Decimal('100.0'))
                return discount_value.quantize(Decimal('0.01'))  # Redondear a 2 decimales
        return Decimal('0.00')

    @property
    def final_price_after_discount(self):
        """
        Calcula el precio final después de aplicar el descuento.
        Retorna un objeto Decimal.
        """
        if self.grand_total_client_price_completed is not None:
            # Reutiliza la propiedad anterior para el cálculo
            return self.grand_total_client_price_completed - self.calculated_discount_amount
        return Decimal('0.00')

    def get_type_prefix(self):
        """Obtiene el prefijo para el unique_code basado en el tipo."""
        return {
            'user_records': 'UR',
            'deactivation_toggle': 'DT',
            'unit_transfer': 'UT',
            'generating_xml': 'XF',
            'address_validation': 'AV',
            'stripe_disputes': 'SD',
            'property_records': 'PR',
        }.get(self.type_of_process, 'Gen')

    def save(self, *args, **kwargs):

        is_new = self._state.adding

        if not self.unique_code:
            now_utc = timezone.now()
            year = now_utc.year % 100
            quarter = (now_utc.month - 1) // 3 + 1
            prefix = f"{self.get_type_prefix()}-{year:02d}Q{quarter}"

            last_request = UserRecordsRequest.objects.filter(
                type_of_process=self.type_of_process,
                unique_code__startswith=prefix
            ).order_by('-unique_code').first()

            new_seq = 1
            if last_request:
                try:
                    sequence_part = last_request.unique_code.split(prefix)[-1]
                    last_seq = int(sequence_part)
                    new_seq = last_seq + 1
                except (IndexError, ValueError, TypeError) as e:
                    logger.warning(f"Could not parse sequence number from code: {last_request.unique_code} for prefix {prefix}. Error: {e}. Starting sequence from 1.")
                    new_seq = 1
            self.unique_code = f"{prefix}{new_seq:03d}"

        if is_new and not self.status:
            self.status = 'pending'

        if self.grand_total_client_price_completed is not None:
            self.final_price_client_completed = self.final_price_after_discount

        super().save(*args, **kwargs)

    @property
    def local_timestamp(self):
        tz_name = 'UTC'
        if self.requested_by and self.requested_by.timezone:
            tz_name = self.requested_by.timezone
        try:
            tz = pytz.timezone(tz_name)
            return self.timestamp.astimezone(tz)
        except pytz.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone '{tz_name}' for user {self.requested_by_id}. Falling back to UTC.")
            return self.timestamp.astimezone(pytz.utc)
        except Exception as e:
             logger.error(f"Error converting timestamp for request {self.id} to timezone '{tz_name}': {e}")
             return self.timestamp

    @property
    def calculated_turn_around_time(self):
        if self.status == 'completed' and self.completed_at and self.effective_start_time_for_tat:
            if self.completed_at > self.effective_start_time_for_tat:
                return self.completed_at - self.effective_start_time_for_tat
        return None

    class Meta:
        verbose_name = 'Request'
        verbose_name_plural = 'Requests'
        ordering = ['-timestamp']

class BlockedMessage(models.Model):
    """Registra cuándo y por qué se bloqueó una solicitud."""
    request = models.ForeignKey(UserRecordsRequest, on_delete=models.CASCADE, related_name='blocked_messages')
    blocked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    blocked_at = models.DateTimeField(default=now)
    reason = models.TextField()

    def __str__(self):
        by = self.blocked_by.email if self.blocked_by else 'System'
        return f"Blocked for {self.request.unique_code} by {by}"

    class Meta:
        ordering = ['-blocked_at'] # Más recientes primero


class ResolvedMessage(models.Model):
    """Registra cuándo y cómo se resolvió una solicitud bloqueada."""
    request = models.ForeignKey(UserRecordsRequest, on_delete=models.CASCADE, related_name='resolved_messages')
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(default=now)
    message = models.TextField()
    resolved_file = models.FileField(upload_to='user_records/resolutions/', null=True, blank=True, validators=[validate_file_size])
    resolved_link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        by = self.resolved_by.email if self.resolved_by else 'System'
        return f"Resolved for {self.request.unique_code} by {by}"

    class Meta:
        ordering = ['-resolved_at'] # Más recientes primero


class RejectedMessage(models.Model):
    """Registra cuándo y por qué se rechazó una solicitud (generalmente desde QA)."""
    request = models.ForeignKey(UserRecordsRequest, on_delete=models.CASCADE, related_name='rejected_messages')
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    rejected_at = models.DateTimeField(default=now)
    reason = models.TextField()
    is_resolved_qa = models.BooleanField(default=False) # Indica si el rechazo fue resuelto por QA

    def __str__(self):
        by = self.rejected_by.email if self.rejected_by else 'System'
        return f"Rejected for {self.request.unique_code} by {by}"

    class Meta:
        ordering = ['-rejected_at'] # Más recientes primero


# --- Modelo de Precios ---

class OperationPrice(models.Model):
    """
    Modelo Singleton para almacenar precios y costos de las operaciones.
    Se asume que solo existirá una instancia (pk=1).
    """
    # Precios Cliente
    user_update_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="User Update Price")
    property_update_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Property Update Price")
    bulk_update_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Bulk Update Price")
    manual_property_update_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Manual Property Update Price")
    csv_update_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="CSV Update Row Price")
    processing_report_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Processing Report Row Price")
    manual_unit_update_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Manual Unit Update Price")
    address_validation_unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Address Validation Unit Price")
    stripe_dispute_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Stripe Dispute Price")
    xml_file_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="XML File Price")

    # Costos Operación
    user_update_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="User Update Operate Cost")
    property_update_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="User Update Operate Cost")
    bulk_update_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Bulk Update Operate Cost")
    manual_property_update_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Manual Property Update Operate Cost")
    csv_update_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="CSV Update Row Operate Cost")
    processing_report_operate_cost = models.DecimalField(max_digits=6,decimal_places=3, default=0.000, verbose_name="Processing Report Row Operate Cost")
    manual_unit_update_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Manual Unit Update Operate Cost")
    address_validation_unit_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Address Validation Unit Operate Cost")
    stripe_dispute_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Stripe Dispute Operate Cost")
    xml_file_operate_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="XML File Operate Cost")

    # Costos QA
    user_update_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="User Update QA Cost")
    property_update_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Property Update QA Cost")
    bulk_update_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Bulk Update QA Cost")
    manual_property_update_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Manual Property Update QA Cost")
    csv_update_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="CSV Update Row QA Cost")
    processing_report_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Processing Report Row QA Cost")
    manual_unit_update_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Manual Unit Update QA Cost")
    address_validation_unit_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Address Validation Unit QA Cost")
    stripe_dispute_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="Stripe Dispute QA Cost")
    xml_file_qa_cost = models.DecimalField(max_digits=6, decimal_places=3, default=0.000, verbose_name="XML File QA Cost")


    def __str__(self):
        return "Operation Prices and Costs"

    class Meta:
        # Asegura que solo haya una fila (usando la vista admin o get_or_create)
        verbose_name = "Operation Price and Cost"
        verbose_name_plural = "Operation Prices and Costs"

class AddressValidationFile(models.Model):
    """Almacena archivos individuales subidos para una solicitud de Address Validation."""
    request = models.ForeignKey(
        UserRecordsRequest,
        related_name='address_validation_files', # Nombre para acceder desde UserRecordsRequest
        on_delete=models.CASCADE
        # Omitimos limit_choices_to por simplicidad por ahora
    )
    uploaded_file = models.FileField(
        upload_to='address_validation_uploads/', # Directorio específico
        validators=[validate_file_size] # Usa tu validador
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        file_name = os.path.basename(self.uploaded_file.name) if self.uploaded_file else 'No file'
        return f"AV File for {self.request.unique_code} ({file_name})"

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = "Address Validation File"
        verbose_name_plural = "Address Validation Files"

class SalesforceAttachmentLog(models.Model):
    """
    Almacena metadatos de adjuntos de Salesforce para solicitudes creadas automáticamente.
    """
    request = models.ForeignKey(
        UserRecordsRequest,
        related_name='salesforce_attachments', # Para acceder desde UserRecordsRequest
        on_delete=models.CASCADE,
        verbose_name="Associated Request"
    )
    file_name = models.CharField(max_length=255, verbose_name="File Name")
    file_extension = models.CharField(max_length=50, blank=True, null=True, verbose_name="File Extension")
    salesforce_file_link = models.URLField(max_length=1024, verbose_name="Salesforce File Link")

    def __str__(self):
        return f"Salesforce Attachment '{self.file_name}' for Request '{self.request.unique_code}'"

    class Meta:
        verbose_name ="Salesforce Attachment Log"
        verbose_name_plural ="Salesforce Attachment Logs"
        ordering = ['-request__timestamp', 'file_name']

class ScheduledTaskToggle(models.Model):
    """
    Modelo para controlar el estado de activación/desactivación
    de tareas programadas específicas.
    Se espera una única instancia por tarea que se quiera controlar.
    """
    task_name = models.CharField(max_length=255, unique=True, primary_key=True, help_text="Unique identifier for the scheduled task.")
    is_enabled = models.BooleanField(default=True, help_text="MCheck to enable task execution. Uncheck to pause.")
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_name} - {'Enabled' if self.is_enabled else 'Paused'}"

    class Meta:
        verbose_name = "Scheduled Task Toggle"
        verbose_name_plural = "Scheduled Task Toggles"


class NotificationToggle(models.Model):
    """
    Modelo para habilitar/deshabilitar notificaciones por correo electrónico para eventos específicos.
    """
    event_key = models.CharField(
        max_length=100,
        unique=True,
        primary_key=True,
        help_text="Clave única para el evento de notificación (ej. 'new_request_created')."
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Breve descripción de para qué es este evento de notificación."
    )
    is_email_enabled = models.BooleanField(
        default=True,
        help_text="Marcar para habilitar las notificaciones por correo para este evento. Desmarcar para deshabilitar."
    )

    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        email_status = 'Habilitado' if self.is_email_enabled else 'Deshabilitado'
        return f"{self.description or self.event_key} (Email: {email_status})"

    class Meta:
        verbose_name = "Control de Evento de Notificación"
        verbose_name_plural = "Controles de Eventos de Notificación"
        ordering = ['description', 'event_key']