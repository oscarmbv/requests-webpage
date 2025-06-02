# tasks/admin.py

import json
import os
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from django.contrib import messages

from .models import (
    BlockedMessage, CustomUser, OperationPrice, RejectedMessage, ResolvedMessage,
    UserRecordsRequest, AddressValidationFile, SalesforceAttachmentLog, ScheduledTaskToggle, NotificationToggle
)

# --- Configuración Admin para CustomUser ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_('Timezone Info'), {'fields': ('timezone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Timezone Info'), {'fields': ('timezone', 'first_name', 'last_name', 'email')}),
    )
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'timezone')
    list_filter = UserAdmin.list_filter + ('timezone',)
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)


# --- Inlines para Historial en UserRecordsRequest Admin ---
class BlockedMessageInline(admin.TabularInline):
    model = BlockedMessage
    extra = 0
    fields = ('blocked_by', 'blocked_at', 'reason')
    readonly_fields = ('blocked_by', 'blocked_at', 'reason')
    can_delete = False
    show_change_link = False

class ResolvedMessageInline(admin.TabularInline):
    model = ResolvedMessage
    extra = 0
    fields = ('resolved_by', 'resolved_at', 'message', 'resolved_file', 'resolved_link')
    readonly_fields = ('resolved_by', 'resolved_at', 'message', 'resolved_file', 'resolved_link')
    can_delete = False
    show_change_link = False

class RejectedMessageInline(admin.TabularInline):
    model = RejectedMessage
    extra = 0
    fields = ('rejected_by', 'rejected_at', 'reason', 'is_resolved_qa')
    readonly_fields = ('rejected_by', 'rejected_at', 'reason', 'is_resolved_qa')
    can_delete = False
    show_change_link = False

class AddressValidationFileInline(admin.TabularInline):
    model = AddressValidationFile
    extra = 0
    fields = ('uploaded_at', 'file_link_display')
    readonly_fields = ('uploaded_at', 'file_link_display')
    can_delete = False
    show_change_link = False

    @admin.display(description='File')
    def file_link_display(self, obj):
        if obj.uploaded_file:
            file_name = os.path.basename(obj.uploaded_file.name)
            return format_html('<a href="{}" target="_blank">{}</a>', obj.uploaded_file.url, file_name)
        return "-"

    def has_add_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False

# --- Configuración Admin para UserRecordsRequest ---
@admin.register(UserRecordsRequest)
class UserRecordsRequestAdmin(admin.ModelAdmin):
    list_display = (
        'unique_code', 'type_of_process', 'requested_by_link', 'partner_name', 'priority','team', 'status',
        'operator_link', 'qa_agent_link', 'timestamp', 'completed_at',
    )
    list_filter = ('status', 'type_of_process', 'team', 'priority', 'timestamp', 'operator', 'qa_agent', 'requested_by')
    search_fields = ('unique_code', 'partner_name', 'requested_by__email', 'operator__email', 'qa_agent__email', 'special_instructions', 'team', 'priority')
    readonly_fields = (
        'unique_code', 'timestamp', 'requested_by_link', 'operator_link', 'qa_agent_link',
        'operated_at', 'qa_pending_at', 'qa_in_progress_at', 'completed_at', 'cancelled_at',
        'user_groups_data_display',
        'user_file_link',
        'user_link_display', 'cancel_reason', 'properties', 'team',
        # Deactivation/Toggle
        'deactivation_toggle_type', 'deactivation_toggle_active_policies',
        'deactivation_toggle_properties_with_policies', 'deactivation_toggle_context',
        'deactivation_toggle_leadership_approval', 'deactivation_toggle_marked_as_churned',
        # Unit Transfer
        'unit_transfer_type', 'unit_transfer_new_partner_prospect_name', 'unit_transfer_receiving_partner_psm',
        'unit_transfer_new_policyholders', 'unit_transfer_user_email_addresses',
        'unit_transfer_prospect_portfolio_size', 'unit_transfer_prospect_landlord_type', 'unit_transfer_proof_of_sale',
        # Generating XML
        'xml_state', 'xml_carrier_rvic', 'xml_carrier_ssic', 'xml_rvic_zip_file', 'xml_ssic_zip_file',
        # Address Validation
        'address_validation_policyholders', 'address_validation_opportunity_id',
        'address_validation_user_email_addresses',
        # Stripe Disputes
        'stripe_premium_disputes', 'stripe_ri_disputes',
        # PROPERTY RECORDS
        'property_records_new_names', 'property_records_new_pmc',
        'property_records_new_policyholder', 'property_records_corrected_address',
        'property_records_updated_type', 'property_records_units',
        'property_records_coverage_type', 'property_records_coverage_multiplier',
        'property_records_coverage_amount', 'property_records_integration_type',
        'property_records_integration_codes', 'property_records_bank_details',
        # Operation Details
        'num_updated_users', 'num_updated_properties', 'bulk_updates',
        'manual_updated_properties', 'update_by_csv_rows', 'processing_reports_rows', 'operating_notes',
        # Salesforce Opportunities
        'salesforce_opportunity_name', 'salesforce_number_of_units', 'salesforce_link',
        'salesforce_account_manager', 'salesforce_closed_won_date',
        'salesforce_leasing_integration_software', 'salesforce_information_needed_for_assets', 'salesforce_standard_opp_id',
        'assets_uploaded',
        'av_number_of_units',
        'av_number_of_invalid_units',
        'link_to_assets',
        'success_output_link',
        'failed_output_link',
        'rhino_accounts_created',
    )
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    fieldsets = (
        # ... (Fieldsets existentes: Request Info, Status & Assignment, Request Data) ...
        (_('Request Info'),
         {'fields': ('unique_code', 'type_of_process', 'requested_by_link', 'timestamp', 'partner_name')}),
        # noqa: E501
        (_('Status & Assignment'), {'fields': ('status', 'team', 'priority', 'operator_link', 'qa_agent_link', 'update_needed_flag', 'is_rejected_previously', 'scheduled_date', 'effective_start_time_for_tat')}),
        (_('Request Data (General Submission)'),
         {'fields': ('properties', 'user_groups_data_display', 'user_file_link', 'user_link_display', 'special_instructions')}),
        # noqa: E501
        (_('Deactivation/Toggle Details'), {'classes': ('collapse',),
                                            'fields': ('deactivation_toggle_type',
                                                       'deactivation_toggle_active_policies',
                                                       'deactivation_toggle_properties_with_policies',
                                                       'deactivation_toggle_context',
                                                       'deactivation_toggle_leadership_approval',
                                                       'deactivation_toggle_marked_as_churned')}),  # noqa: E501
        (_('Unit Transfer Details'), {'classes': ('collapse',),
                                      'fields': ('unit_transfer_type', 'unit_transfer_new_partner_prospect_name',
                                                 'unit_transfer_receiving_partner_psm',
                                                 'unit_transfer_new_policyholders',
                                                 'unit_transfer_user_email_addresses',
                                                 'unit_transfer_prospect_portfolio_size',
                                                 'unit_transfer_prospect_landlord_type',
                                                 'unit_transfer_proof_of_sale')}),  # noqa: E501
        (_('Generating XML Details'), {'classes': ('collapse',),
                                       'fields': ('xml_state', 'xml_carrier_rvic', 'xml_carrier_ssic',
                                                  'xml_rvic_zip_file', 'xml_ssic_zip_file')}),  # noqa: E501
        (_('Address Validation Details (Submission & Salesforce Info)'), {'classes': ('collapse',),
                                                        'fields': (
                                                            'address_validation_policyholders',
                                                            'address_validation_opportunity_id', # Custom SF ID
                                                            'address_validation_user_email_addresses',
                                                            # Campos de Info de Salesforce
                                                            'salesforce_standard_opp_id',
                                                            'salesforce_opportunity_name',
                                                            'salesforce_number_of_units',
                                                            'salesforce_link',
                                                            'salesforce_account_manager',
                                                            'salesforce_closed_won_date',
                                                            'salesforce_leasing_integration_software',
                                                            'salesforce_information_needed_for_assets',
                                                        )
                                                    }),
        (_('Stripe Disputes Details'),
         {'classes': ('collapse',), 'fields': ('stripe_premium_disputes', 'stripe_ri_disputes')}),
        (_('Property Records Details'), {'classes': ('collapse',), 'fields': (
            'property_records_type',
            'property_records_new_names', 'property_records_new_pmc',
            'property_records_new_policyholder', 'property_records_corrected_address',
            'property_records_updated_type', 'property_records_units',
            'property_records_coverage_type', 'property_records_coverage_multiplier',
            'property_records_coverage_amount', 'property_records_integration_type',
            'property_records_integration_codes', 'property_records_bank_details',
        )}),
        (_('Operation Details Recorded'),
         {'classes': ('collapse', 'wide'),  # 'wide' para más espacio si hay muchos campos
          'fields': (
              'operated_at',
              ('num_updated_users', 'num_updated_properties'),  # Agrupar en una línea
              ('bulk_updates', 'manual_updated_properties', 'manual_updated_units'),  # Agrupar
              'update_by_csv_rows', 'processing_reports_rows',
              'operator_spreadsheet_link',
              ('av_number_of_units', 'av_number_of_invalid_units'),
              'link_to_assets',
              ('success_output_link', 'failed_output_link'),
              ('assets_uploaded', 'rhino_accounts_created'),
              'operating_notes',
          )
          }),
        (_('Workflow Timestamps'), {'classes': ('collapse',),
                                    'fields': ('qa_pending_at', 'qa_in_progress_at', 'completed_at', 'cancelled_at',
                                               'cancel_reason')}),  # noqa: E501
    )
    inlines = [AddressValidationFileInline, BlockedMessageInline, ResolvedMessageInline, RejectedMessageInline]

    actions = ['trigger_salesforce_sync_action', 'trigger_scheduled_jobs_action']

    def trigger_salesforce_sync_action(self, request, queryset):
        """
        Acción de Admin para encolar la tarea de sincronización de Salesforce.
        """
        try:
            async_task('tasks.salesforce_sync.sync_salesforce_opportunities_task')
            self.message_user(request, "La tarea de sincronización con Salesforce ha sido encolada.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error al encolar la tarea de sincronización: {e}", messages.ERROR)

    trigger_salesforce_sync_action.short_description = "Sincronizar Opportunities desde Salesforce"

    def trigger_scheduled_jobs_action(self, request, queryset):
        """
        Acción de Admin para encolar la tarea 'process_scheduled_requests'.
        """
        try:
            async_task('tasks.scheduled_jobs.process_scheduled_requests')
            self.message_user(request, "La tarea para procesar solicitudes programadas ha sido encolada.",messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error al encolar la tarea de procesamiento de solicitudes programadas: {e}",messages.ERROR)

    trigger_scheduled_jobs_action.short_description = "Ejecutar Procesador de Solicitudes Programadas"

    @admin.display(description='Requested By')
    def requested_by_link(self, obj): # noqa: E704
        if obj.requested_by: url = reverse("admin:tasks_customuser_change", args=[obj.requested_by.pk]); return format_html('<a href="{}">{}</a>', url, obj.requested_by.email) # noqa: E701, E501
        return "-" # noqa: E704
    @admin.display(description='Operator')
    def operator_link(self, obj): # noqa: E704
        if obj.operator: url = reverse("admin:tasks_customuser_change", args=[obj.operator.pk]); return format_html('<a href="{}">{}</a>', url, obj.operator.email) # noqa: E701, E501
        return "-" # noqa: E704
    @admin.display(description='QA Agent')
    def qa_agent_link(self, obj): # noqa: E704
        if obj.qa_agent: url = reverse("admin:tasks_customuser_change", args=[obj.qa_agent.pk]); return format_html('<a href="{}">{}</a>', url, obj.qa_agent.email) # noqa: E701, E501
        return "-" # noqa: E704
    @admin.display(description='Single Uploaded File')
    def user_file_link(self, obj): # noqa: E704
        if obj.user_file: return format_html('<a href="{}" target="_blank">{}</a>', obj.user_file.url, os.path.basename(obj.user_file.name)) # noqa: E701, E501
        return "-" # noqa: E704
    @admin.display(description='Uploaded Link')
    def user_link_display(self, obj): # noqa: E704
        if obj.user_link: return format_html('<a href="{}" target="_blank">Link</a>', obj.user_link) # noqa: E701, E501
        return "-" # noqa: E704
    @admin.display(description='User Groups Data')
    def user_groups_data_display(self, obj): # noqa: E704
        if obj.user_groups_data:
            try: formatted_json = json.dumps(obj.user_groups_data, indent=2); return format_html('<pre style="white-space: pre-wrap; word-wrap: break-word;">{}</pre>', formatted_json) # noqa: E701, E501
            except TypeError: return str(obj.user_groups_data) # noqa: E701
        return "-" # noqa: E704

# --- Configuración Admin para Modelos de Historial ---
class HistoryMessageAdmin(admin.ModelAdmin):
    """Clase base para mostrar mensajes de historial."""
    list_display = ('request_link', 'actor_email', 'timestamp_with_tz', 'short_reason')
    # Eliminamos list_filter de la clase base
    search_fields = ('request__unique_code', 'actor__email', 'reason', 'message')
    timestamp_order_field = 'timestamp' # Campo base para ordenar (sobrescrito en hijos)

    @admin.display(description='Request Code', ordering='request__unique_code')
    def request_link(self, obj):
        if obj.request: url = reverse("admin:tasks_userrecordsrequest_change", args=[obj.request.pk]); return format_html('<a href="{}">{}</a>', url, obj.request.unique_code)
        return "-"
    @admin.display(description='Actor', ordering='actor__email')
    def actor_email(self, obj):
        if obj.actor: return obj.actor.email
        return 'N/A'
    @admin.display(description='Timestamp')
    def timestamp_with_tz(self, obj):
        ts_field_name = f"{obj._meta.model_name.split('message')[0]}_at"
        ts = getattr(obj, ts_field_name, obj.timestamp)
        if ts: return timezone.localtime(ts).strftime('%Y-%m-%d %H:%M:%S %Z')
        return 'N/A'
    timestamp_with_tz.admin_order_field = 'timestamp_order_field'

    @admin.display(description='Reason/Message')
    def short_reason(self, obj):
        reason = getattr(obj, 'reason', getattr(obj, 'message', '')) or ""
        return (reason[:75] + '...') if len(reason) > 75 else reason

    def get_fieldsets(self, request, obj=None):
         base_fields = ('request_link', 'actor_email', 'timestamp_with_tz')
         if isinstance(obj, BlockedMessage): return ((None, {'fields': base_fields + ('reason',)}),)
         elif isinstance(obj, ResolvedMessage): return ((None, {'fields': base_fields + ('message', 'resolved_file', 'resolved_link')}),)
         elif isinstance(obj, RejectedMessage): return ((None, {'fields': base_fields + ('reason', 'is_resolved_qa')}),)
         return ((None, {'fields': base_fields}),)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly = [f.name for f in self.model._meta.fields]
            display_methods = [m for m in self.list_display if callable(getattr(self, m, None))]
            readonly.extend(display_methods)
            if hasattr(obj, 'resolved_file'): readonly.append('resolved_file')
            if hasattr(obj, 'resolved_link'): readonly.append('resolved_link')
            return list(set(readonly))
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser


@admin.register(BlockedMessage)
class BlockedMessageAdmin(HistoryMessageAdmin):
    list_filter = ('blocked_at', 'blocked_by') # Usar el campo específico '_at'
    timestamp_order_field = 'blocked_at'

@admin.register(ResolvedMessage)
class ResolvedMessageAdmin(HistoryMessageAdmin):
    list_filter = ('resolved_at', 'resolved_by') # Usar el campo específico '_at'
    timestamp_order_field = 'resolved_at'

@admin.register(RejectedMessage)
class RejectedMessageAdmin(HistoryMessageAdmin):
     list_display = HistoryMessageAdmin.list_display + ('is_resolved_qa',)
     list_filter = ('rejected_at', 'rejected_by', 'is_resolved_qa') # Usar campo '_at' y añadir 'is_resolved_qa'
     timestamp_order_field = 'rejected_at'

@admin.register(AddressValidationFile)
class AddressValidationFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_id', 'file_link_display', 'uploaded_at') # Mostrar link al archivo
    list_filter = ('request__type_of_process', 'uploaded_at')
    search_fields = ('request__unique_code', 'uploaded_file__name')
    readonly_fields = ('id', 'request', 'uploaded_file', 'uploaded_at', 'file_link_display')

    @admin.display(description='File')
    def file_link_display(self, obj):
         if obj.uploaded_file:
             file_name = os.path.basename(obj.uploaded_file.name)
             return format_html('<a href="{}" target="_blank">{}</a>', obj.uploaded_file.url, file_name)
         return "-"

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

# --- Configuración Admin para OperationPrice ---
@admin.register(OperationPrice)
class OperationPriceAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    fieldsets = (
        ('Client Prices', {'fields': ('user_update_price', 'property_update_price', 'bulk_update_price', 'manual_property_update_price', 'csv_update_price', 'processing_report_price', 'manual_unit_update_price', 'address_validation_unit_price', 'stripe_dispute_price', 'xml_file_price')}),
        ('Operate Costs', {'fields': ('user_update_operate_cost', 'property_update_operate_cost', 'bulk_update_operate_cost', 'manual_property_update_operate_cost', 'csv_update_operate_cost', 'processing_report_operate_cost', 'manual_unit_update_operate_cost', 'address_validation_unit_operate_cost', 'stripe_dispute_operate_cost', 'xml_file_operate_cost')}),
        ('QA Costs', {'fields': ('user_update_qa_cost', 'property_update_qa_cost', 'bulk_update_qa_cost', 'manual_property_update_qa_cost', 'csv_update_qa_cost', 'processing_report_qa_cost', 'manual_unit_update_qa_cost', 'address_validation_unit_qa_cost', 'stripe_dispute_qa_cost', 'xml_file_qa_cost')}),
    )

    @admin.display(description=_('Configuration Item'))
    def admin_display_name(self, obj):
        return str(obj)

    def has_add_permission(self, request): return not OperationPrice.objects.exists()
    def has_delete_permission(self, request, obj=None): return False


@admin.register(SalesforceAttachmentLog)  # <--- REGISTRAR SalesforceAttachmentLog SI NO LO HAS HECHO
class SalesforceAttachmentLogAdmin(admin.ModelAdmin):
    list_display = ('request_link_admin', 'file_name', 'file_extension', 'salesforce_file_link_display')
    search_fields = ('request__unique_code', 'file_name')
    readonly_fields = ('request', 'file_name', 'file_extension', 'salesforce_file_link')
    list_select_related = ('request',)  # Optimizar query

    @admin.display(description='Request Code', ordering='request__unique_code')
    def request_link_admin(self, obj):  # Renombrado para evitar conflicto con el de UserRecordsRequestAdmin
        if obj.request:
            url = reverse("admin:tasks_userrecordsrequest_change", args=[obj.request.pk])
            return format_html('<a href="{}">{}</a>', url, obj.request.unique_code)
        return "-"

    @admin.display(description='Salesforce File Link')
    def salesforce_file_link_display(self, obj):
        if obj.salesforce_file_link:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">View in Salesforce</a>',
                               obj.salesforce_file_link)
        return "-"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(ScheduledTaskToggle)
class ScheduledTaskToggleAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'is_enabled', 'last_modified')
    list_editable = ('is_enabled',)
    list_filter = ('is_enabled',)
    search_fields = ('task_name',)
    readonly_fields = ('last_modified',)

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(NotificationToggle)
class NotificationToggleAdmin(admin.ModelAdmin):
    list_display = ('event_key', 'description', 'is_email_enabled', 'last_modified')
    list_editable = ('is_email_enabled', 'description') # Permite editar estos campos en la vista de lista
    search_fields = ('event_key', 'description')
    readonly_fields = ('last_modified',) # event_key es primary_key, no editable post-creación
    list_filter = ('is_email_enabled',)