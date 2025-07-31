# tasks/forms.py

from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.db import models
import logging
from django.utils import timezone
from datetime import timedelta
import pytz
from django.conf import settings
from tinymce.widgets import TinyMCE

logger = logging.getLogger(__name__)

# Importa los modelos necesarios
from .models import UserRecordsRequest, OperationPrice, CustomUser

# Importa las choices DIRECTAMENTE desde choices.py
from .choices import (
    ACCESS_LEVEL_CHOICES, DEACTIVATION_TOGGLE_CHOICES, LEADERSHIP_APPROVAL_CHOICES,
    UNIT_TRANSFER_TYPE_CHOICES, UNIT_TRANSFER_LANDLORD_TYPE_CHOICES, XML_STATE_CHOICES,
    PROPERTY_RECORDS_TYPE_CHOICES, PROPERTY_TYPE_CHOICES, COVERAGE_TYPE_CHOICES,
    COVERAGE_MULTIPLIER_CHOICES, INTEGRATION_TYPE_CHOICES, REQUEST_TYPE_CHOICES,
    PRIORITY_CHOICES, PRIORITY_NORMAL,
)

# --- Formularios de Usuario ---
class CustomUserChangeForm(UserChangeForm):
    """Formulario para editar datos básicos del usuario."""
    password = None
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'timezone', 'slack_member_id')
        widgets = { # Widgets con clases Bootstrap
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
            'slack_member_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = { # Labels traducibles
            'username': _('Username'), 'email': _('Email Address'),
            'first_name': _('First Name'), 'last_name': _('Last Name'),
            'timezone': _('Timezone'),
            'slack_member_id': _('Slack Member ID'),
        }
    def clean_email(self): # Validación de email único
        email = self.cleaned_data.get('email')
        if self.instance.pk:
             if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                 raise ValidationError(_("A user with that email already exists."))
        elif CustomUser.objects.filter(email=email).exists():
             raise ValidationError(_("A user with that email already exists."))
        return email

class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario para cambiar la contraseña."""
    old_password = forms.CharField(label=_("Old password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True, 'class': 'form-control'}))
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), strip=False, help_text=_("Your password must be at least 8 characters long."))
    new_password2 = forms.CharField(label=_("Confirm New password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}))
    def clean_new_password1(self): # Usa validadores de Django
        password = self.cleaned_data.get('new_password1')
        validate_password(password, self.user)
        return password

# --- Formularios de Request ---
class UserGroupForm(forms.Form):
    """Formulario para un grupo de usuarios en UserRecordsRequest."""
    type_of_request = forms.ChoiceField(
        choices=REQUEST_TYPE_CHOICES,
        label='Type of Request',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True # Asumiendo que siempre se requiere
    )
    deactivate_user = forms.BooleanField(
        label="Deactivate user(s) from portal?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    user_email_addresses = forms.CharField(
        label='User Email Address(es)',
        widget=forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'placeholder': 'email1@example.com, email2@example.com\nemail3@example.com'}), # Añadido form-control-sm
        help_text='Enter one or more email addresses, separated by commas or newlines.',
        required=True
    )
    access_level = forms.ChoiceField(
        choices=ACCESS_LEVEL_CHOICES,
        label='User Access Level (no need for Remove User)',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}), # Añadido form-select-sm
        help_text='Not needed for Remove User(s)',
        required=False # Mantenido False, se maneja en __init__ y JS
    )
    properties = forms.CharField(
        label='Properties',
        widget=forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'placeholder': 'Property1, Property2\nProperty3'}), # Añadido form-control-sm
        help_text='Enter one or more properties, separated by commas or newlines.',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nota: Acceder a self.data en __init__ puede ser problemático.
        # La lógica de JS que habilita/deshabilita y marca como required
        # en el frontend es probablemente más robusta para la UX.
        # Pero mantenemos la lógica original de required=True/False aquí.
        is_remove = False
        if self.data: # Si hay datos (POST)
             type_field_name = f"{self.prefix}-type_of_request"
             is_remove = self.data.get(type_field_name) == 'remove'
        elif self.initial: # Si hay datos iniciales (GET, poco común en formsets así)
             is_remove = self.initial.get('type_of_request') == 'remove'

        if not is_remove:
            self.fields['access_level'].required = True
        else:
             self.fields['access_level'].required = False

    def clean_user_email_addresses(self):
        # (Esta función de limpieza se mantiene igual)
        emails_input = self.cleaned_data.get('user_email_addresses', '')
        emails = [email.strip().lower() for line in emails_input.splitlines() for email in line.split(',') if email.strip()]
        invalid_emails = []
        for email in emails:
            try: forms.EmailField().clean(email) # Valida formato individual
            except ValidationError: invalid_emails.append(email)
        if invalid_emails: raise ValidationError(_("Invalid email addresses found: %(emails)s") % {'emails': ', '.join(invalid_emails)})
        # Devolver la lista es útil para la vista
        return emails # O `return "\n".join(emails)` si prefieres string

    def clean_properties(self):
        # (Esta función de limpieza se mantiene igual)
        properties_input = self.cleaned_data.get('properties', '')
        properties = [prop.strip() for line in properties_input.splitlines() for prop in line.split(',') if prop.strip()]
        return properties # O `return "\n".join(properties)`

class UserRecordsRequestForm(forms.Form):
    """Formulario principal para crear UserRecordsRequest."""
    partner_name = forms.CharField(max_length=255, label='Partner Name', widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    special_instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), label='Special Instructions (optional)', required=False)
    user_file = forms.FileField(label='Upload Spreadsheet (optional)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    user_link = forms.URLField(label='Provide a Link Instead (optional)', required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}))
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES, label="Priority",
        widget=forms.RadioSelect, initial=PRIORITY_NORMAL, required=True
    )
    schedule_request = forms.BooleanField(
        label="Schedule this request?",
        required=False,
        initial=False,  # Por defecto, no está programada
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})  # Para estilo Bootstrap
    )
    scheduled_date = forms.DateField(
        label="Schedule for Date",
        required=False,  # Se hará obligatorio con JS y validación en clean()
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Select a future date (tomorrow onwards)."
    )

    submit_on_behalf_of = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False, is_active=True).order_by('email'),
        required=False,
        label="Submit request on behalf of (Admin Only)",
        help_text="Select a client to create this request on their behalf. Leave blank to create it for yourself.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.user or not self.user.is_staff:
            if 'submit_on_behalf_of' in self.fields:
                del self.fields['submit_on_behalf_of']

    def clean(self):
        cleaned_data = super().clean()
        schedule_request_flag = cleaned_data.get('schedule_request')
        scheduled_date_value = cleaned_data.get('scheduled_date')

        if schedule_request_flag:
            if not scheduled_date_value:
                self.add_error('scheduled_date', _("Please select a date if you want to schedule the request."))
            else:
                user_tz_str = self.user.timezone if self.user and hasattr(self.user,'timezone') and self.user.timezone else settings.TIME_ZONE
                try:
                    user_timezone = pytz.timezone(user_tz_str)
                except pytz.UnknownTimeZoneError:
                    logger.warning(f"Unknown timezone '{user_tz_str}' for user {self.user.pk if self.user else 'Anonymous'}. Falling back to project TIME_ZONE.")
                    user_timezone = pytz.timezone(settings.TIME_ZONE)  # Fallback a la zona horaria del proyecto (UTC)

                today_in_user_tz = timezone.now().astimezone(user_timezone).date()
                tomorrow_in_user_tz = today_in_user_tz + timedelta(days=1)

                if scheduled_date_value < tomorrow_in_user_tz:
                    self.add_error('scheduled_date', _("Scheduled date must be tomorrow (your local time) or later."))
        return cleaned_data

class BlockForm(forms.Form):
    """Formulario para la razón de bloqueo."""
    reason = forms.CharField(label='Reason for Blocking', widget=TinyMCE(attrs={'id': 'block-reason-editor', 'class': 'tinymce-target', 'data-config': 'simple'}), required=True)


class ResolveForm(forms.Form):
    """Formulario para resolver una solicitud bloqueada."""
    message = forms.CharField(label='Resolution Message', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True)
    resolved_file = forms.FileField(label='Upload Resolution File (optional)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    resolved_link = forms.URLField(label='Provide Resolution Link Instead (optional)', required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}))


class RejectForm(forms.Form):
    """Formulario para la razón de rechazo."""
    reason = forms.CharField(label='Reason for Rejection', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True)


class OperateForm(forms.ModelForm):
    """Formulario para registrar detalles de la operación."""
    class Meta:
        model = UserRecordsRequest
        fields = [
            'num_updated_users', 'num_updated_properties', 'bulk_updates',
            'manual_updated_properties', 'update_by_csv_rows', 'manual_updated_units',
            'processing_reports_rows', 'operator_spreadsheet_link', 'operating_notes',
            'assets_uploaded', 'av_number_of_units', 'av_number_of_invalid_units', 'link_to_assets',
            'success_output_link', 'failed_output_link', 'rhino_accounts_created',
            'stripe_premium_disputes', 'stripe_ri_disputes',
        ]
        widgets = { # Widgets con clases Bootstrap y min="0"
            'num_updated_users': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'num_updated_properties': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'bulk_updates': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'manual_updated_properties': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'manual_updated_units': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'update_by_csv_rows': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'processing_reports_rows': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'operator_spreadsheet_link': forms.URLInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'https://docs.google.com/spreadsheets/...'}),
            'operating_notes': TinyMCE(attrs={'id': 'operate-notes-editor', 'class': 'tinymce-target', 'data-config': 'full'}),
            'assets_uploaded': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'av_number_of_units': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'av_number_of_invalid_units': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'link_to_assets': forms.URLInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'https://sheets.google.com/...'}),
            'success_output_link': forms.URLInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'https://sheets.google.com/...'}),
            'failed_output_link': forms.URLInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'https://sheets.google.com/...'}),
            'rhino_accounts_created': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stripe_premium_disputes': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'stripe_ri_disputes': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
        }
        labels = { # Labels mejorados
            'num_updated_users': 'Users Updated/Added/Removed',
            'num_updated_properties': 'Properties Updated',
            'bulk_updates': 'Bulk Updates (Count)',
            'manual_updated_properties': 'Manual Property Updates (Count)',
            'manual_updated_units': 'Manual Updated Units (Count)',
            'update_by_csv_rows': 'Rows Processed (CSV Update)',
            'processing_reports_rows': 'Rows Processed (Reports)',
            'operator_spreadsheet_link': 'Operator Spreadsheet Link',
            'operating_notes': 'Operator Notes',
            'assets_uploaded': 'Assets Uploaded?',
            'av_number_of_units': 'Number of Units (Address Validation)',
            'av_number_of_invalid_units': 'Number of Invalid Units (AV)',
            'link_to_assets': 'Link to Assets (Google Sheet)',
            'success_output_link': 'Success Output Link (Google Sheet)',
            'failed_output_link': 'Failed Output Link (Google Sheet)',
            'rhino_accounts_created': 'Rhino Accounts Created?',
            'stripe_premium_disputes': 'Rhino Super Premium Disputes Count',
            'stripe_ri_disputes': 'Rhino Super RI Disputes Count',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        av_specific_fields = [
            'assets_uploaded', 'av_number_of_units', 'av_number_of_invalid_units',
            'link_to_assets', 'success_output_link', 'failed_output_link',
            'rhino_accounts_created',
        ]

        stripe_disputes_fields = ['stripe_premium_disputes', 'stripe_ri_disputes']

        hide_for_av = ['processing_reports_rows', 'operator_spreadsheet_link']
        hide_for_stripe = ['processing_reports_rows', 'operator_spreadsheet_link',
                           'num_updated_users', 'num_updated_properties', 'bulk_updates',
                           'manual_updated_properties', 'manual_updated_units',
                           'update_by_csv_rows']

        if instance:
            if instance.type_of_process == 'address_validation':
                for field_name in hide_for_av:
                    if field_name in self.fields: del self.fields[field_name]
                for field_name in stripe_disputes_fields:  # Ocultar campos de Stripe
                    if field_name in self.fields: del self.fields[field_name]

                # Configurar obligatoriedad para AV
                if 'av_number_of_units' in self.fields: self.fields['av_number_of_units'].required = True
                if 'av_number_of_invalid_units' in self.fields: self.fields[
                    'av_number_of_invalid_units'].required = True
                if 'link_to_assets' in self.fields: self.fields['link_to_assets'].required = True
                if 'operating_notes' in self.fields: self.fields['operating_notes'].required = True

                # Pre-llenar av_number_of_units
                if 'av_number_of_units' in self.fields and instance.salesforce_number_of_units is not None:
                    if not self.data.get(self.add_prefix('av_number_of_units')):  # Solo si no hay datos POST
                        self.fields['av_number_of_units'].initial = instance.salesforce_number_of_units


            elif instance.type_of_process == 'stripe_disputes':
                for field_name in hide_for_stripe:
                    if field_name in self.fields: del self.fields[field_name]
                for field_name in av_specific_fields:  # Ocultar campos de AV
                    if field_name in self.fields: del self.fields[field_name]

                # Hacer los campos de Stripe obligatorios (pueden ser 0)
                if 'stripe_premium_disputes' in self.fields: self.fields['stripe_premium_disputes'].required = True
                if 'stripe_ri_disputes' in self.fields: self.fields['stripe_ri_disputes'].required = True
                if 'operating_notes' in self.fields: self.fields[
                    'operating_notes'].required = True  # Opcional: hacer notas obligatorias también para Stripe

            elif instance.type_of_process == 'generating_xml':
                for field_name in av_specific_fields + stripe_disputes_fields:
                    if field_name in self.fields: del self.fields[field_name]

            else:
                for field_name in av_specific_fields + stripe_disputes_fields:
                    if field_name in self.fields:
                        del self.fields[field_name]
                if 'operating_notes' in self.fields:
                    self.fields['operating_notes'].required = False  # Notas opcionales por defecto
                if 'operator_spreadsheet_link' in self.fields:
                    self.fields['operator_spreadsheet_link'].required = False

        for field_name, field in self.fields.items():
            if isinstance(field, forms.IntegerField) or isinstance(field, forms.DecimalField):
                is_min_value_0_present = any(
                    isinstance(v, MinValueValidator) and v.limit_value == 0 for v in field.validators
                )
                if not is_min_value_0_present:
                    field.validators.append(MinValueValidator(0))
                # No sobrescribir 'required' si ya se estableció arriba
                if not hasattr(field, 'user_set_required'):  # Evitar conflicto con lo ya establecido
                    field.required = False
            elif isinstance(field, forms.URLField) and not hasattr(field, 'user_set_required'):
                field.required = False  # Links opcionales por defecto

        for field_name in ['av_number_of_units', 'av_number_of_invalid_units', 'link_to_assets',
                           'operating_notes', 'stripe_premium_disputes', 'stripe_ri_disputes']:
            if field_name in self.fields and self.fields[field_name].required:
                self.fields[field_name].user_set_required = True


class OperationPriceForm(forms.ModelForm):
    """Formulario para gestionar precios y costos."""
    class Meta:
        model = OperationPrice
        fields = '__all__'
        widgets = { # Widgets con step para decimales
            field.name: forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
            for field in OperationPrice._meta.get_fields() if isinstance(field, models.DecimalField)
        }


class DeactivationToggleRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de Deactivation/Toggle."""
    # Usa las choices importadas directamente
    submit_on_behalf_of = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False, is_active=True).order_by('email'),
        required=False,
        label="Submit request on behalf of (Admin Only)",
        help_text="Select a client to create this request on their behalf. Leave blank to create it for yourself.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    deactivation_toggle_type = forms.ChoiceField(choices=DEACTIVATION_TOGGLE_CHOICES, label='Type of Request', required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    partner_name = forms.CharField(max_length=255, label='Partner', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    properties = forms.CharField(label='Properties Affected', required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Enter existing property IDs or names, separated by comma or newline.')
    deactivation_toggle_active_policies = forms.BooleanField(label='Are there Active Policies on these properties?', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    deactivation_toggle_properties_with_policies = forms.CharField(label='If yes, specify properties with Active Policies', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Separate by comma or newline.')
    deactivation_toggle_context = forms.CharField(label='Context (brief explanation)', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    deactivation_toggle_leadership_approval = forms.ChoiceField(choices=LEADERSHIP_APPROVAL_CHOICES, label='Leadership Approval', required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    deactivation_toggle_marked_as_churned = forms.BooleanField(label='Marked as Churned in SF', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    special_instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), label='Special Instructions (optional)', required=False)
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        label="Priority",
        widget=forms.RadioSelect,
        initial=PRIORITY_NORMAL,
        required=True
    )
    schedule_request = forms.BooleanField(
        label="Schedule this request?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    scheduled_date = forms.DateField(
        label="Schedule for Date",
        required=False,  # Se hará obligatorio con JS y validación en clean()
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Select a future date (tomorrow or later, your local time)."
    )

    class Meta:
        model = UserRecordsRequest
        fields = [
            'deactivation_toggle_type', 'partner_name', 'properties',
            'deactivation_toggle_active_policies', 'deactivation_toggle_properties_with_policies',
            'deactivation_toggle_context', 'deactivation_toggle_marked_as_churned',
            'special_instructions', 'priority', 'schedule_request', 'scheduled_date',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_staff:
            current_fields = self.fields
            new_order = {'submit_on_behalf_of': current_fields.pop('submit_on_behalf_of')}
            new_order.update(current_fields)
            self.fields = new_order
        else:
            if 'submit_on_behalf_of' in self.fields:
                del self.fields['submit_on_behalf_of']

        tipo = self.data.get('deactivation_toggle_type') or self.initial.get('deactivation_toggle_type')

        if tipo in ['partner_deactivation', 'toggle_off_homepage_signups']:
            self.fields['properties'].required = False
            self.fields['properties'].widget.attrs['disabled'] = True

        if tipo in ['toggle_on_invites', 'toggle_on_cash_deposit', 'toggle_off_cash_deposit']:
            self.fields['deactivation_toggle_active_policies'].widget.attrs['disabled'] = True
            self.fields['deactivation_toggle_context'].widget.attrs['disabled'] = True

        if tipo != 'partner_deactivation':
            self.fields['deactivation_toggle_marked_as_churned'].widget.attrs['disabled'] = True

    def clean_properties(self):
        properties = self.cleaned_data.get('properties')
        if properties:
            raw_list = [p.strip() for line in properties.splitlines() for p in line.split(',') if p.strip()]
            return "\n".join(raw_list)
        return properties

    def clean_deactivation_toggle_properties_with_policies(self):
        properties = self.cleaned_data.get('deactivation_toggle_properties_with_policies')
        if properties:
            raw_list = [p.strip() for line in properties.splitlines() for p in line.split(',') if p.strip()]
            return "\n".join(raw_list)
        return properties

    def clean(self):
        cleaned_data = super().clean()
        deact_type = cleaned_data.get('deactivation_toggle_type')
        properties_value = cleaned_data.get('properties')
        context_value = cleaned_data.get('deactivation_toggle_context')
        has_active_policies = cleaned_data.get('deactivation_toggle_active_policies')
        properties_with_policies = cleaned_data.get('deactivation_toggle_properties_with_policies')

        # --- 1. PROPERTIES solo obligatorio si es 'property_deactivation' ---
        if deact_type == 'property_deactivation' and not properties_value:
            self.add_error('properties', _("Please specify the properties to deactivate."))

        # --- 2. Validación de propiedades con policies ---
        if has_active_policies and not properties_with_policies:
            self.add_error('deactivation_toggle_properties_with_policies',
                           _("Please specify which properties have active policies."))

        # --- 3. Deshabilitar y limpiar campos según el tipo ---
        if deact_type in ['partner_deactivation', 'toggle_off_homepage_signups']:
            cleaned_data['properties'] = None

        if deact_type in ['toggle_on_invites', 'toggle_on_cash_deposit', 'toggle_off_cash_deposit']:
            cleaned_data['deactivation_toggle_active_policies'] = False
            cleaned_data['deactivation_toggle_context'] = ''

        # --- 4. Marked as Churned solo para partner_deactivation ---
        if deact_type != 'partner_deactivation':
            cleaned_data['deactivation_toggle_marked_as_churned'] = None

        # --- 5. Validación de programación ---
        schedule_request_flag = cleaned_data.get('schedule_request')
        scheduled_date_value = cleaned_data.get('scheduled_date')

        if schedule_request_flag:
            if not scheduled_date_value:
                self.add_error('scheduled_date', _("Please select a date if you want to schedule the request."))
            else:
                user_tz_str = (
                    self.user.timezone
                    if self.user and hasattr(self.user, 'timezone') and self.user.timezone
                    else settings.TIME_ZONE
                )
                try:
                    user_timezone = pytz.timezone(user_tz_str)
                except pytz.UnknownTimeZoneError:
                    logger.warning(
                        f"Unknown timezone '{user_tz_str}' for user {self.user.pk if self.user else 'Anonymous'}. Falling back to project TIME_ZONE.")
                    user_timezone = pytz.timezone(settings.TIME_ZONE)

                today_in_user_tz = timezone.now().astimezone(user_timezone).date()
                tomorrow_in_user_tz = today_in_user_tz + timedelta(days=1)

                if scheduled_date_value < tomorrow_in_user_tz:
                    self.add_error('scheduled_date', _("Scheduled date must be tomorrow (your local time) or later."))

        return cleaned_data


class UnitTransferRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de Unit Transfer."""
    # Usa las choices importadas directamente
    submit_on_behalf_of = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False, is_active=True).order_by('email'),
        required=False,
        label="Submit request on behalf of (Admin Only)",
        help_text="Select a client to create this request on their behalf. Leave blank to create it for yourself.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    unit_transfer_type = forms.ChoiceField(choices=UNIT_TRANSFER_TYPE_CHOICES, label='Type of Request', required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    partner_name = forms.CharField(max_length=255, label='Partner Name (Origin)', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    unit_transfer_new_partner_prospect_name = forms.CharField(max_length=255, label='New Partner or Prospect Name (Destination)', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    unit_transfer_receiving_partner_psm = forms.CharField(max_length=255, label="Receiving Partner's PSM (Optional)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    properties = forms.CharField(label='Properties to Transfer', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Enter existing property IDs or names, separated by comma or newline. Required if no file/link.')
    unit_transfer_new_policyholders = forms.CharField(label='New Policyholder(s) (Optional)', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Separate by comma or newline.')
    unit_transfer_user_email_addresses = forms.CharField(label='User Email Address(es) for New Partner (Optional)', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Separate by comma or newline.')
    unit_transfer_prospect_portfolio_size = forms.IntegerField(label='Prospect Portfolio Size', required=False, validators=[MinValueValidator(0)], widget=forms.NumberInput(attrs={'class': 'form-control'}))
    unit_transfer_prospect_landlord_type = forms.ChoiceField(choices=UNIT_TRANSFER_LANDLORD_TYPE_CHOICES, label='Prospect Landlord Type', required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    unit_transfer_proof_of_sale = forms.URLField(label='Proof of Sale (Link)', required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}))
    special_instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), label='Special Instructions (optional)', required=False)
    user_file = forms.FileField(label='Upload Properties File (optional)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    user_link = forms.URLField(label='Provide a Spreadsheet Link Instead (optional)', required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}))

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES, label="Priority",
        widget=forms.RadioSelect, initial=PRIORITY_NORMAL, required=True
    )
    schedule_request = forms.BooleanField(
        label="Schedule this request?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    scheduled_date = forms.DateField(
        label="Schedule for Date",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Select a future date (tomorrow onwards)."
    )
    class Meta:
        model = UserRecordsRequest
        fields = [
            'unit_transfer_type', 'partner_name', 'unit_transfer_new_partner_prospect_name',
            'unit_transfer_receiving_partner_psm', 'properties',
            'unit_transfer_new_policyholders', 'unit_transfer_user_email_addresses',
            'unit_transfer_prospect_portfolio_size', 'unit_transfer_prospect_landlord_type',
            'unit_transfer_proof_of_sale', 'special_instructions', 'user_file', 'user_link',
            'priority', 'schedule_request', 'scheduled_date'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_staff:
            current_fields = self.fields
            # Creamos un nuevo diccionario de campos con el nuestro al principio.
            new_order = {'submit_on_behalf_of': current_fields.pop('submit_on_behalf_of')}
            new_order.update(current_fields)
            self.fields = new_order
        else:
            if 'submit_on_behalf_of' in self.fields:
                del self.fields['submit_on_behalf_of']

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('unit_transfer_type')
        portfolio_size = cleaned_data.get('unit_transfer_prospect_portfolio_size')
        landlord_type = cleaned_data.get('unit_transfer_prospect_landlord_type')
        user_file = cleaned_data.get('user_file')
        user_link = cleaned_data.get('user_link')
        properties_value = cleaned_data.get('properties')

        if request_type == 'partner_to_prospect':
            if portfolio_size is None:
                self.add_error('unit_transfer_prospect_portfolio_size',
                               'Este campo es obligatorio para el tipo Partner to Prospect.')
            if not landlord_type:
                self.add_error('unit_transfer_prospect_landlord_type',
                               'Este campo es obligatorio para el tipo Partner to Prospect.')

        # Validación para 'properties' si no hay archivo/enlace (ya estaba)
        if not user_file and not user_link and not properties_value:
            self.add_error('properties',_('Properties to Transfer are required if no file or link is provided.'))

        schedule_request_flag = cleaned_data.get('schedule_request')
        scheduled_date_value = cleaned_data.get('scheduled_date')

        if schedule_request_flag:
            if not scheduled_date_value:
                self.add_error('scheduled_date', _("Please select a date if you want to schedule the request."))
            else:
                user_tz_str = self.user.timezone if self.user and hasattr(self.user,'timezone') and self.user.timezone else settings.TIME_ZONE
                try:
                    user_timezone = pytz.timezone(user_tz_str)
                except pytz.UnknownTimeZoneError:
                    logger.warning(f"Unknown timezone '{user_tz_str}' for user {self.user.pk if self.user else 'Anonymous'}. Falling back to project TIME_ZONE.")
                    user_timezone = pytz.timezone(settings.TIME_ZONE)

                today_in_user_tz = timezone.now().astimezone(user_timezone).date()
                tomorrow_in_user_tz = today_in_user_tz + timedelta(days=1)

                if scheduled_date_value < tomorrow_in_user_tz:
                    self.add_error('scheduled_date', _("Scheduled date must be tomorrow (your local time) or later."))

        return cleaned_data

    def clean_unit_transfer_user_email_addresses(self):
        emails_input = self.cleaned_data.get('unit_transfer_user_email_addresses', '')
        if not emails_input:
            return ''
        emails = [
            email.strip().lower() for line in emails_input.splitlines()
            for email in line.split(',') if email.strip()
        ]
        invalid_emails = []
        for email in emails:
            try:
                forms.EmailField().clean(email)
            except ValidationError:
                invalid_emails.append(email)
        if invalid_emails:
            raise ValidationError(
                _("Invalid email addresses found: %(emails)s") % {'emails': ', '.join(invalid_emails)}
            )
        return "\n".join(emails)

class GeneratingXmlRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de Generating XML."""
    # Usa las choices importadas directamente
    xml_state = forms.ChoiceField(choices=XML_STATE_CHOICES, label='State', required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    xml_carrier_rvic = forms.BooleanField(label='RVIC', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    xml_carrier_ssic = forms.BooleanField(label='SSIC', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    user_file = forms.FileField(label='Upload Spreadsheet', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    xml_rvic_zip_file = forms.FileField(label='RVIC ZIP File (Required for CA, MS, UT, WA)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    xml_ssic_zip_file = forms.FileField(label='SSIC ZIP File (Required for CA, MS, UT, WA)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    special_instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), label='Special Instructions (optional)', required=False)
    #priority = forms.ChoiceField(
    #    choices=PRIORITY_CHOICES, label="Priority",
    #    widget=forms.RadioSelect, initial=PRIORITY_NORMAL, required=True
    #)
    class Meta:
        model = UserRecordsRequest
        fields = [
            'xml_state', 'xml_carrier_rvic', 'xml_carrier_ssic',
            'user_file', 'xml_rvic_zip_file', 'xml_ssic_zip_file',
            'special_instructions', #'priority',
        ]

    def clean(self):
        # La lógica de clean() se mantiene como estaba, ya era correcta
        cleaned_data = super().clean()
        state = cleaned_data.get('xml_state')
        rvic_selected = cleaned_data.get('xml_carrier_rvic')
        ssic_selected = cleaned_data.get('xml_carrier_ssic')
        rvic_zip_file = cleaned_data.get('xml_rvic_zip_file')
        ssic_zip_file = cleaned_data.get('xml_ssic_zip_file')

        if not rvic_selected and not ssic_selected:
            self.add_error(None, _("Please select at least one carrier (RVIC or SSIC)."))

        states_requiring_zip = ['CA', 'MS', 'UT', 'WA']
        if state in states_requiring_zip:
            if rvic_selected and not rvic_zip_file:
                self.add_error('xml_rvic_zip_file', _("RVIC ZIP File is required for %(state)s when RVIC is selected.") % {'state': state})
            if ssic_selected and not ssic_zip_file:
                 self.add_error('xml_ssic_zip_file', _("SSIC ZIP File is required for %(state)s when SSIC is selected.") % {'state': state})
        # else: # Opcional: validar que NO se suban si no son necesarios
        #     if rvic_zip_file:
        #          self.add_error('xml_rvic_zip_file', f"RVIC ZIP File is not required for {state}.")
        #     if ssic_zip_file:
        #          self.add_error('xml_ssic_zip_file', f"SSIC ZIP File is not required for {state}.")

        return cleaned_data

class AddressValidationRequestForm(forms.ModelForm):
    submit_on_behalf_of = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False, is_active=True).order_by('email'),
        required=False,
        label="Submit request on behalf of (Admin Only)",
        help_text="Select a client to create this request on their behalf. Leave blank to create it for yourself.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    partner_name = forms.CharField(label='Partner', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address_validation_policyholders = forms.CharField(label='Policyholder(s)', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Separate multiple policyholders by comma or newline.')
    address_validation_opportunity_id = forms.CharField(label='Opportunity Id', required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'})) # required=False por defecto
    user_link = forms.URLField(label='Provide a Link Instead (Optional)', required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}))
    address_validation_user_email_addresses = forms.CharField(label='User Email Address(es)', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), help_text='Enter one or more email addresses, separated by commas or newlines.')
    special_instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), label='Special Instructions (optional)', required=False)

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        label="Priority",
        widget=forms.RadioSelect,
        initial=PRIORITY_NORMAL,
        required=True
    )
    schedule_request = forms.BooleanField(
        label="Schedule this request?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    scheduled_date = forms.DateField(
        label="Schedule for Date",
        required=False,  # Se hará obligatorio con JS y validación en clean()
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Select a future date (tomorrow or later, your local time)."
    )
    class Meta:
        model = UserRecordsRequest
        # Lista de campos que SÍ pertenecen a UserRecordsRequest para este form
        fields = [
            'partner_name', 'address_validation_policyholders',
            'address_validation_opportunity_id', 'user_link',
            'address_validation_user_email_addresses', 'special_instructions',
            'priority', 'schedule_request', 'scheduled_date',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_staff:
            current_fields = self.fields
            new_order = {'submit_on_behalf_of': current_fields.pop('submit_on_behalf_of')}
            new_order.update(current_fields)
            self.fields = new_order
        else:
            if 'submit_on_behalf_of' in self.fields:
                del self.fields['submit_on_behalf_of']

    def clean_address_validation_user_email_addresses(self):
        # ... (lógica de limpieza de emails sin cambios) ...
        emails_input = self.cleaned_data.get('address_validation_user_email_addresses', '')
        if not emails_input: return ''
        emails = [email.strip() for line in emails_input.splitlines() for email in line.split(',') if email.strip()]
        invalid_emails = []
        for email in emails:
            try: forms.EmailField().clean(email)
            except ValidationError: invalid_emails.append(email)
        if invalid_emails: raise ValidationError(_("Invalid email addresses found: %(emails)s") % {'emails': ', '.join(invalid_emails)})
        return "\n".join(emails)


    def clean(self):
        cleaned_data = super().clean()
        opportunity_id = cleaned_data.get('address_validation_opportunity_id')
        user_link = cleaned_data.get('user_link')
        files_provided = bool(self.files.get('request_files'))

        logger.debug(f"[Clean AV Form] OppID: '{opportunity_id}', Link: '{user_link}', Files Uploaded: {files_provided}")

        # Requerir Opportunity ID solo si NO hay link Y NO hay archivos Y el campo está vacío
        if not files_provided and not user_link and not opportunity_id:
            logger.warning("[Clean AV Form] Validation Error: Opportunity ID required.")
            self.add_error('address_validation_opportunity_id', _('Opportunity ID is required if neither file(s) nor a link is provided.'))

        schedule_request_flag = cleaned_data.get('schedule_request')
        scheduled_date_value = cleaned_data.get('scheduled_date')

        if schedule_request_flag:
            if not scheduled_date_value:
                self.add_error('scheduled_date', _("Please select a date if you want to schedule the request."))
            else:
                # Validación de zona horaria del usuario
                user_tz_str = self.user.timezone if self.user and hasattr(self.user,
                                                                          'timezone') and self.user.timezone else settings.TIME_ZONE
                try:
                    user_timezone = pytz.timezone(user_tz_str)
                except pytz.UnknownTimeZoneError:
                    logger.warning(
                        f"Unknown timezone '{user_tz_str}' for user {self.user.pk if self.user else 'Anonymous'}. Falling back to project TIME_ZONE.")
                    user_timezone = pytz.timezone(settings.TIME_ZONE)

                today_in_user_tz = timezone.now().astimezone(user_timezone).date()
                tomorrow_in_user_tz = today_in_user_tz + timedelta(days=1)

                if scheduled_date_value < tomorrow_in_user_tz:
                    self.add_error('scheduled_date', _("Scheduled date must be tomorrow (your local time) or later."))

        return cleaned_data

class StripeDisputesRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de Stripe Disputes."""
    # Definir campos explícitamente para control y widgets
    #priority = forms.ChoiceField(
    #    choices=PRIORITY_CHOICES, label="Priority",
    #    widget=forms.RadioSelect, initial=PRIORITY_NORMAL, required=True
    #)
    submit_on_behalf_of = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False, is_active=True).order_by('email'),
        required=False,
        label="Submit request on behalf of (Admin Only)",
        help_text="Select a client to create this request on their behalf. Leave blank to create it for yourself.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    stripe_premium_disputes = forms.IntegerField(
        label="Rhino Super Premium Disputes",
        required=True,
        min_value=0, # Permitir 0, pero la validación exigirá > 0 si el otro está vacío
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    stripe_ri_disputes = forms.IntegerField(
        label="Rhino Super RI Disputes",
        required=True, # Validación personalizada en clean()
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    # Reutilizamos user_file, pero ajustamos label y help_text
    user_file = forms.FileField(
        label="Upload CSV with Disputes",
        required=True, # Este archivo es obligatorio
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Required columns: Market, Dispute Id, Deadline, Internal Notes",
    )
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Special Instructions (optional)',
        required=False
    )

    class Meta:
        model = UserRecordsRequest
        fields = [
            'stripe_premium_disputes',
            'stripe_ri_disputes',
            'user_file',
            'special_instructions', #'priority',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_staff:
            current_fields = self.fields
            new_order = {'submit_on_behalf_of': current_fields.pop('submit_on_behalf_of')}
            new_order.update(current_fields)
            self.fields = new_order
        else:
            # Si NO es un admin, eliminamos el campo del formulario
            if 'submit_on_behalf_of' in self.fields:
                del self.fields['submit_on_behalf_of']

    def clean(self):
        cleaned_data = super().clean()
        premium_disputes = cleaned_data.get('stripe_premium_disputes')
        ri_disputes = cleaned_data.get('stripe_ri_disputes')

        # Consideramos None o 0 como no llenado para la validación
        premium_filled = premium_disputes is not None and premium_disputes > 0
        ri_filled = ri_disputes is not None and ri_disputes > 0

        if not premium_filled and not ri_filled:
            raise ValidationError(
                _("Please enter a value greater than 0 for at least one of the dispute types (Premium or RI)."),
                code='no_dispute_count'
            )

        return cleaned_data

class PropertyRecordsRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de Property Records."""

    submit_on_behalf_of = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False, is_active=True).order_by('email'),
        required=False,
        label="Submit request on behalf of (Admin Only)",
        help_text="Select a client to create this request on their behalf. Leave blank to create it for yourself.",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        label="Priority",
        widget=forms.RadioSelect,
        initial=PRIORITY_NORMAL,
        required=True
    )
    schedule_request = forms.BooleanField(
        label="Schedule this request?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    scheduled_date = forms.DateField(
        label="Schedule for Date",
        required=False,  # Se hará obligatorio con JS y validación en clean()
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Select a future date (tomorrow or later, your local time)."
    )
    # --- Campos Primera Columna (Obligatorios inicialmente) ---
    property_records_type = forms.ChoiceField(
        choices=PROPERTY_RECORDS_TYPE_CHOICES,
        label='Type of Request',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    partner_name = forms.CharField(
        label='Partner Name', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    properties = forms.CharField(
        label='Properties Affected', required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Enter existing property IDs or names, separated by comma or newline.'
    )

    # --- Campos Opcionales Primera Columna ---
    user_file = forms.FileField(
        label='Upload File (Optional)', required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )
    user_link = forms.URLField(
        label='Provide a Link Instead (Optional)', required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'})
    )
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Special Instructions (optional)',
        required=False
    )

    # --- Campos Segunda Columna (Condicionales) ---
    # Todos required=False por defecto, la lógica JS/clean se encargará
    property_records_new_names = forms.CharField(
        label='New Property Names', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Update the Property Name or Building Name for existing properties.'
    )
    property_records_new_pmc = forms.CharField(
        label='New Property Management Company', required=False,
        max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Update the Owner for existing properties (for large requests, use Unit Transfer).'
    )
    property_records_new_policyholder = forms.CharField(
        label='New Policyholder', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Update the Policyholder for existing properties.'
    )
    property_records_corrected_address = forms.CharField(
        label='Corrected Address', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Street Address, City, State ZIP'}),
        help_text='Correct the Address for existing properties.'
    )
    property_records_updated_type = forms.ChoiceField(
        choices=PROPERTY_TYPE_CHOICES, label='Updated Property Type', required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    property_records_units = forms.CharField(
        label='Property Units', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Add new units for existing properties (for large requests, use Address Validation).'
    )
    property_records_coverage_type = forms.ChoiceField(
        choices=COVERAGE_TYPE_CHOICES, label='Coverage Type', required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    property_records_coverage_multiplier = forms.ChoiceField(
        choices=COVERAGE_MULTIPLIER_CHOICES, label='Coverage Multiplier', required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    property_records_coverage_amount = forms.DecimalField(
        label='Coverage Amount (USD)', required=False,
        max_digits=11, decimal_places=2,
        min_value=Decimal('330.00'), max_value=Decimal('200000000.00'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text = _('Enter numeric values only, without the $ symbol. Example: 1234.50')
    )
    property_records_integration_type = forms.ChoiceField(
        choices=INTEGRATION_TYPE_CHOICES, label='Integration Type', required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    property_records_integration_codes = forms.CharField(
        label='Integration Codes', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Add new lines or separate with commas.'
    )
    property_records_bank_details = forms.CharField(
        label='Bank Details', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        help_text='Invisible will only handle Bank Details updates for Claims.'
    )

    class Meta:
        model = UserRecordsRequest
        # Incluir TODOS los campos que maneja este formulario
        fields = [
            'property_records_type', 'partner_name', 'properties',
            'user_file', 'user_link', 'special_instructions',
            'property_records_new_names', 'property_records_new_pmc',
            'property_records_new_policyholder', 'property_records_corrected_address',
            'property_records_updated_type', 'property_records_units',
            'property_records_coverage_type', 'property_records_coverage_multiplier',
            'property_records_coverage_amount', 'property_records_integration_type',
            'property_records_integration_codes', 'property_records_bank_details',
            'priority', 'schedule_request', 'scheduled_date',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_staff:
            current_fields = self.fields
            # Creamos un nuevo diccionario de campos con el nuestro al principio
            new_order = {'submit_on_behalf_of': current_fields.pop('submit_on_behalf_of')}
            new_order.update(current_fields)
            self.fields = new_order
        else:
            if 'submit_on_behalf_of' in self.fields:
                del self.fields['submit_on_behalf_of']

        conditionally_required_fields = [
            'property_records_new_names', 'property_records_new_pmc',
            'property_records_new_policyholder', 'property_records_corrected_address',
            'property_records_updated_type', 'property_records_units',
            'property_records_coverage_type', 'property_records_coverage_multiplier',
            'property_records_coverage_amount', 'property_records_integration_type',
            'property_records_integration_codes', 'property_records_bank_details',
        ]

        for field_name in conditionally_required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

        optional_select_fields = [
            'property_records_updated_type', 'property_records_coverage_type',
            'property_records_coverage_multiplier', 'property_records_integration_type',
        ]


    def clean(self):
        cleaned_data = super().clean()
        pr_type = cleaned_data.get('property_records_type')

        # --- INICIO DE LA LÓGICA DE LIMPIEZA Y VALIDACIÓN CONDICIONAL ---

        # Nombres de los campos de parámetros que queremos manejar condicionalmente
        # Estos son los campos que quieres que sean NULOS si no se elige el pr_type correspondiente
        param_fields_to_manage = {
            'property_records_updated_type': 'property_type',  # El pr_type que lo activa
            'property_records_coverage_type': 'coverage_type_amount',
            'property_records_coverage_multiplier': 'coverage_type_amount',
            'property_records_coverage_amount': 'coverage_type_amount',
            'property_records_integration_type': 'integration_code',
            # Otros campos condicionales de tu formulario:
            'property_records_new_names': 'property_name',
            'property_records_new_pmc': 'property_management_company',
            'property_records_new_policyholder': 'property_legal_entity',
            'property_records_corrected_address': 'address',
            'property_records_units': 'property_units',
            'property_records_integration_codes': 'integration_code',
            'property_records_bank_details': 'banking_information',
        }

        # Mapeo de 'pr_type' a los campos que DEBEN ser validados si ese pr_type es elegido
        # (y no hay bypass por archivo/enlace)
        # Tu lógica actual de required_fields_map es buena, la integraremos.
        required_fields_for_type = {
            'property_name': ['property_records_new_names'],
            'property_management_company': ['property_records_new_pmc'],
            'property_legal_entity': ['property_records_new_policyholder'],
            'address': ['property_records_corrected_address'],
            'property_type': ['property_records_updated_type'],
            'property_units': ['property_records_units'],
            'coverage_type_amount': ['property_records_coverage_type'],  # Validaremos multiplier/amount después
            'integration_code': ['property_records_integration_type', 'property_records_integration_codes'],
            'banking_information': ['property_records_bank_details'],
        }

        # Tu lógica de bypass (si se sube archivo o se da enlace, no se requieren campos específicos)
        user_file = cleaned_data.get('user_file')
        user_link = cleaned_data.get('user_link')
        file_provided_in_current_submission = bool(self.files.get('user_file'))
        instance_file_exists = bool(self.instance and self.instance.pk and self.instance.user_file)
        clear_file_checkbox_name = self.add_prefix('user_file') + '-clear'
        file_cleared = self.data.get(clear_file_checkbox_name) == 'on'
        file_is_present_or_uploaded = (
                    file_provided_in_current_submission or (instance_file_exists and not file_cleared))
        bypass_specific_field_requirements = file_is_present_or_uploaded or bool(user_link)

        # 1. Limpiar todos los campos condicionales que NO corresponden al pr_type seleccionado
        for field_name, activating_pr_type in param_fields_to_manage.items():
            if field_name in cleaned_data:  # Asegurarse que el campo está en cleaned_data
                if pr_type != activating_pr_type:
                    cleaned_data[field_name] = None  # ¡ESTO ES CLAVE PARA GUARDAR NULL!
                else:
                    # Si es el pr_type correcto, y no hay bypass, verificar si el campo está vacío
                    if not bypass_specific_field_requirements:
                        # Si el campo está en required_fields_for_type para el pr_type actual
                        if pr_type in required_fields_for_type and field_name in required_fields_for_type[pr_type]:
                            if not cleaned_data.get(field_name):
                                # Excepción: coverage_multiplier y coverage_amount tienen lógica anidada
                                if not (pr_type == 'coverage_type_amount' and field_name in [
                                    'property_records_coverage_multiplier', 'property_records_coverage_amount']):
                                    self.add_error(field_name,
                                                   _("This field is required for the selected 'Type of Request' when no file or link is provided."))

        # 2. Validaciones específicas y anidadas que ya tenías (integradas y ajustadas)
        if not bypass_specific_field_requirements:
            if not cleaned_data.get('properties'):  # 'properties' siempre es requerido si no hay bypass
                self.add_error('properties', _("Properties Affected are required if no file or link is provided."))

            if pr_type == 'coverage_type_amount':
                coverage_type_value = cleaned_data.get('property_records_coverage_type')

                if coverage_type_value == 'multiplier':
                    if not cleaned_data.get('property_records_coverage_multiplier'):
                        self.add_error('property_records_coverage_multiplier',_("Multiplier is required when Coverage Type is 'Multiplier' and no file/link is provided."))
                    cleaned_data['property_records_coverage_amount'] = None
                elif coverage_type_value == 'amount':
                    if cleaned_data.get('property_records_coverage_amount') is None:
                        self.add_error('property_records_coverage_amount',_("Coverage Amount (USD) is required when Coverage Type is 'Amount' and no file or link is provided."))
                    cleaned_data['property_records_coverage_multiplier'] = None  # Limpiar el opuesto
                elif coverage_type_value and coverage_type_value not in ['multiplier', 'amount']:
                    cleaned_data['property_records_coverage_multiplier'] = None
                    cleaned_data['property_records_coverage_amount'] = None

        # --- FIN DE LA LÓGICA DE LIMPIEZA Y VALIDACIÓN CONDICIONAL ---

        # Validación de Programación (se mantiene tu lógica)
        schedule_request_flag = cleaned_data.get('schedule_request')
        scheduled_date_value = cleaned_data.get('scheduled_date')
        if schedule_request_flag:
            if not scheduled_date_value:
                self.add_error('scheduled_date', _("Please select a date if you want to schedule the request."))
            else:
                # Tu lógica de validación de fecha (mañana o después)
                user_tz_str = self.user.timezone if self.user and hasattr(self.user,
                                                                          'timezone') and self.user.timezone else settings.TIME_ZONE
                try:
                    user_timezone = pytz.timezone(user_tz_str)
                except pytz.UnknownTimeZoneError:
                    user_timezone = pytz.timezone(settings.TIME_ZONE)  # Fallback a settings.TIME_ZONE

                today_in_user_tz = timezone.localtime(timezone.now(), user_timezone).date()
                # No se puede añadir directamente timedelta a un objeto date ingenuo si scheduled_date_value es ingenuo
                # Asegurarse que scheduled_date_value es consciente o compararlo como date
                # El DateField de Django devuelve un objeto datetime.date

                # La validación original es buena:
                tomorrow_in_user_tz = today_in_user_tz + timedelta(days=1)
                if scheduled_date_value < tomorrow_in_user_tz:  # scheduled_date_value es un objeto date
                    self.add_error('scheduled_date', _("Scheduled date must be tomorrow (your local time) or later."))

        return cleaned_data


class GeneratingXmlOperateForm(forms.ModelForm):
    qa_needs_file_correction = forms.BooleanField(
        label=_("Correct / Re-upload Files?"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_qa_needs_file_correction_gx'})
    )
    class Meta:
        model = UserRecordsRequest
        fields = [
            'operating_notes',
            'operator_rvic_file_slot1', 'operator_rvic_file_slot2',
            'operator_ssic_file_slot1', 'operator_ssic_file_slot2'
        ]
        widgets = {
            'operating_notes': TinyMCE(attrs={'id': 'operate-notes-editor', 'class': 'tinymce-target', 'data-config': 'full'})
        }
        labels = {
            'operating_notes': "Operator/QA Notes (Optional)"
        }

    def __init__(self, *args, **kwargs):
        self.context_type = kwargs.pop('context_type', 'operator_initial')
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        model_file_fields = [
            'operator_rvic_file_slot1', 'operator_rvic_file_slot2',
            'operator_ssic_file_slot1', 'operator_ssic_file_slot2'
        ]
        for f_name in model_file_fields:
            if f_name in self.fields:
                del self.fields[f_name]

        self._dynamic_file_fields_mapping = {}

        if instance and instance.type_of_process == 'generating_xml':
            xml_state = instance.xml_state
            is_rvic_selected_at_creation = instance.xml_carrier_rvic
            is_ssic_selected_at_creation = instance.xml_carrier_ssic
            states_requiring_zip_protocol = ['CA', 'MS', 'UT', 'WA']
            is_zip_protocol_state = xml_state in states_requiring_zip_protocol

            def add_file_field(form_field_name, label_text, model_target_field, is_required=True):
                initial_file = getattr(instance, model_target_field, None)
                self.fields[form_field_name] = forms.FileField(
                    label=label_text,
                    required=is_required,
                    widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
                    initial=initial_file,
                    help_text=_("If re-uploading, this will replace the current file.")
                )
                self.fields[form_field_name].model_field_name = model_target_field
                self._dynamic_file_fields_mapping[form_field_name] = model_target_field

            if is_rvic_selected_at_creation:
                if xml_state == 'UT':
                    add_file_field('op_ut_rvic_csv', _("Operator: UT RVIC CSV File"), 'operator_rvic_file_slot1', True)
                    add_file_field('op_ut_rvic_zip', _("Operator: UT RVIC ZIP File"), 'operator_rvic_file_slot2', True)
                elif is_zip_protocol_state:
                    add_file_field('op_rvic_zip', _("Operator: {} RVIC ZIP File").format(xml_state),'operator_rvic_file_slot1', True)
                else:
                    file_type_label = _("CSV File") if xml_state == 'SC' else _("XML File")
                    add_file_field('op_rvic_file', _("Operator: {} RVIC {}").format(xml_state, file_type_label),'operator_rvic_file_slot1', True)

            if is_ssic_selected_at_creation:
                if xml_state == 'UT':
                    add_file_field('op_ut_ssic_csv', _("Operator: UT SSIC CSV File"), 'operator_ssic_file_slot1', True)
                    add_file_field('op_ut_ssic_zip', _("Operator: UT SSIC ZIP File"), 'operator_ssic_file_slot2', True)
                elif is_zip_protocol_state:
                    add_file_field('op_ssic_zip', _("Operator: {} SSIC ZIP File").format(xml_state),'operator_ssic_file_slot1', True)
                else:
                    file_type_label = _("CSV File") if xml_state == 'SC' else _("XML File")
                    add_file_field('op_ssic_file', _("Operator: {} SSIC {}").format(xml_state, file_type_label),'operator_ssic_file_slot1', True)

        field_order = ['operating_notes', 'qa_needs_file_correction'] + list(self._dynamic_file_fields_mapping.keys())

        ordered_fields = {name: self.fields[name] for name in field_order if name in self.fields}
        for name, field in self.fields.items():
            if name not in ordered_fields:
                ordered_fields[name] = field
        self.fields = ordered_fields

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.operating_notes = self.cleaned_data.get('operating_notes',instance.operating_notes)  # Asegurar que operating_notes se guarde

        for form_field_name, model_field_name in getattr(self, '_dynamic_file_fields_mapping', {}).items():
            if form_field_name in self.cleaned_data:
                file_data = self.cleaned_data[form_field_name]
                if file_data is not None:
                    if file_data:
                        setattr(instance, model_field_name, file_data)
                elif file_data is False:
                    setattr(instance, model_field_name, None)
        if commit:
            instance.save()
        return instance

class ProvideUpdateForm(forms.Form):
    update_message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_provide_update_message'}), # Añadimos ID para el modal
        label="Provide Update Message",
        required=True,
        help_text="Enter the update details that will be sent in the notification."
    )