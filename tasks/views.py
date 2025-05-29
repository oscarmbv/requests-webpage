import logging
import pytz
from django.db import transaction, models
import re
from datetime import datetime, time, timedelta, date
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, Value, CharField, DecimalField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import formset_factory
from django.http import HttpResponse # Necesario si implementas export CSV
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from .models import UserRecordsRequest, OperationPrice
from django.conf import settings
from simple_salesforce import Salesforce, SalesforceError
from django import forms
from decimal import Decimal
import calendar
from django.db.models.functions import Coalesce

# Importa los formularios (sin AddressValidationRequestForm)
from .forms import (
    UserRecordsRequestForm, UserGroupForm, CustomUserChangeForm,
    CustomPasswordChangeForm, BlockForm, ResolveForm, RejectForm,
    OperateForm, OperationPriceForm, DeactivationToggleRequestForm,
    UnitTransferRequestForm, GeneratingXmlRequestForm, AddressValidationRequestForm,
    StripeDisputesRequestForm, PropertyRecordsRequestForm, GeneratingXmlOperateForm
)
# Importa los modelos
from .models import (
    UserRecordsRequest, BlockedMessage, ResolvedMessage,
    RejectedMessage, OperationPrice, CustomUser, AddressValidationFile
)
from .choices import (
    TYPE_CHOICES, STATUS_CHOICES, REQUEST_TYPE_CHOICES, ACCESS_LEVEL_CHOICES,
    DEACTIVATION_TOGGLE_CHOICES, LEADERSHIP_APPROVAL_CHOICES, UNIT_TRANSFER_TYPE_CHOICES,
    UNIT_TRANSFER_LANDLORD_TYPE_CHOICES, XML_STATE_CHOICES, TEAM_CHOICES,
    TEAM_REVENUE, TEAM_SUPPORT, TEAM_COMPLIANCE, TEAM_ACCOUNTING, TEAM_LEADERSHIPS, PRIORITY_CHOICES,
    PRIORITY_NORMAL # Y PRIORITY_NORMAL
)
# Configuración del Logger
logger = logging.getLogger(__name__)

# --- Helper Functions para Permisos ---
# (Definiciones de is_admin, is_leadership, is_agent, etc. como estaban antes)
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

def is_leadership(user):
    if not user.is_authenticated: return False
    try: return user.groups.filter(name='Leaderships').exists()
    except Group.DoesNotExist: logger.warning("Group 'Leaderships' not found."); return False

def is_agent(user):
    if not user.is_authenticated: return False
    return user.groups.filter(name='Agents').exists()

def user_is_admin_or_leader(user):
    return user.is_authenticated and (is_admin(user) or is_leadership(user))

def user_in_group(user, group_name):
    """Chequea si un usuario pertenece a un grupo específico."""
    if not user.is_authenticated: return False
    # Maneja el caso donde el grupo podría no existir aún
    try:
        return user.groups.filter(name=group_name).exists()
    except Group.DoesNotExist:
        logger.warning(f"Permission check failed: Group '{group_name}' does not exist.")
        return False

def can_view_request(user, user_request):
    return user.is_authenticated and (
        user == user_request.requested_by or is_agent(user) or
        is_leadership(user) or is_admin(user)
    )

def can_cancel_request(user, user_request):
    if not user.is_authenticated: return False
    allowed_statuses = ['pending', 'scheduled', 'blocked', 'in_progress', 'qa_pending', 'pending_approval']
    is_authorized_role = is_agent(user) or is_admin(user) or is_leadership(user)
    if is_authorized_role and user_request.status in allowed_statuses: return True
    # elif user == user_request.requested_by and user_request.status in ['pending', 'blocked']: return True
    return False

def user_belongs_to_revenue_or_support(user):
    allowed = user_in_group(user, 'Revenue') or user_in_group(user, 'Support')
    if not allowed:
        # Lanza excepción que el middleware puede capturar o manejar directamente
        raise PermissionDenied(_("You must belong to the Revenue or Support team to access this function."))
    return True # Necesario para user_passes_test

def user_belongs_to_compliance(user):
    allowed = user_in_group(user, 'Compliance')
    if not allowed:
         raise PermissionDenied(_("You must belong to the Compliance team to access this function."))
    return True

def user_belongs_to_accounting(user):
    allowed = user_in_group(user, 'Accounting')
    if not allowed:
         raise PermissionDenied(_("You must belong to the Accounting team to access this function."))
    return True

# --- Vistas ---

@login_required
def home(request):
    return render(request, 'tasks/home.html')

@login_required
def profile(request):
    # (Código de la vista profile como estaba antes)
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        user_form_valid = user_form.is_valid()
        password_change_attempted = bool(request.POST.get('new_password1') or request.POST.get('new_password2'))
        password_form_valid = password_form.is_valid() if password_change_attempted else True
        if user_form_valid and password_form_valid:
            user = user_form.save()
            if password_change_attempted:
                password_form.save()
                messages.success(request, _('Your profile and password have been updated successfully!'))
            else:
                 messages.success(request, _('Your profile has been updated successfully!'))
            return redirect('tasks:profile')
        else:
            messages.error(request, _('Please correct the errors below.'))
            if not password_form_valid:
                 password_form = CustomPasswordChangeForm(request.user, request.POST)
            else:
                 password_form = CustomPasswordChangeForm(request.user)
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'tasks/profile.html', {'form': user_form, 'password_form': password_form})


@login_required
def choose_request_type(request):
    return render(request, 'tasks/choose_request_type.html')

# --- Vistas de Creación ---
@login_required
def user_records_request(request):
    UserGroupFormSet = formset_factory(UserGroupForm, extra=1, min_num=1, can_delete=False)
    user = request.user
    is_in_revenue = user_in_group(user, TEAM_REVENUE)
    is_in_support = user_in_group(user, TEAM_SUPPORT)

    if is_in_revenue and is_in_support:
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:portal_dashboard')

    if request.method == 'POST':
        # Pasar user al form principal
        user_records_form = UserRecordsRequestForm(request.POST, request.FILES, user=user)
        user_group_formset = UserGroupFormSet(request.POST, prefix='groups')

        # Validar AMBOS formularios/formsets
        # Nota: La validación del formset es un poco más compleja si depende de user_file/link
        is_main_form_valid = user_records_form.is_valid()
        user_file = user_records_form.cleaned_data.get('user_file') if is_main_form_valid else None
        user_link = user_records_form.cleaned_data.get('user_link') if is_main_form_valid else None
        is_formset_required = not (user_file or user_link)
        is_formset_valid = True # Asumir válido si no es requerido
        group_data = []

        if is_formset_required:
            if user_group_formset.is_valid():
                for form in user_group_formset:
                     # Lógica para extraer group_data (como estaba antes)
                     if form.has_changed() and form.is_valid():
                         cleaned_emails = form.cleaned_data.get('user_email_addresses', [])
                         cleaned_properties = form.cleaned_data.get('properties', [])
                         if cleaned_emails or cleaned_properties:
                             group_data.append({
                                 'type_of_request': form.cleaned_data.get('type_of_request'),
                                 'user_email_addresses': cleaned_emails,
                                 'access_level': form.cleaned_data.get('access_level'),
                                 'properties': cleaned_properties,
                             })
            else:
                is_formset_valid = False
                messages.error(request, _('Please correct the errors in the User Details section.'))

        # Proceder solo si ambos son válidos (o el formset no era requerido)
        if is_main_form_valid and is_formset_valid:
            if is_formset_required and not group_data:
                 messages.error(request, _("Please provide user details via manual input, file upload, or link."))
                 # Re-renderizar ambos formularios
                 return render(request, 'tasks/user_records_request.html', {'user_records_form': user_records_form, 'user_group_formset': user_group_formset})

            try:
                # Crear instancia sin commit
                creation_timestamp = timezone.now()
                req_instance = UserRecordsRequest(
                    requested_by=user,
                    partner_name=user_records_form.cleaned_data['partner_name'],
                    priority=user_records_form.cleaned_data['priority'],
                    special_instructions=user_records_form.cleaned_data['special_instructions'],
                    user_file=user_file,
                    user_link=user_link,
                    user_groups_data=group_data if group_data else None, # Guardar si hay datos
                    type_of_process='user_records',
                    timestamp=creation_timestamp
                )

                schedule_request_flag = user_records_form.cleaned_data.get('schedule_request')
                scheduled_date_value = user_records_form.cleaned_data.get('scheduled_date')

                if schedule_request_flag and scheduled_date_value:
                    req_instance.status = 'scheduled'
                    req_instance.scheduled_date = scheduled_date_value
                    req_instance.effective_start_time_for_tat = None
                else:
                    req_instance.status = 'pending'
                    req_instance.scheduled_date = None
                    req_instance.effective_start_time_for_tat = creation_timestamp

                # --- ASIGNAR EQUIPO ---
                if is_in_revenue:
                    req_instance.team = TEAM_REVENUE
                elif is_in_support:
                    req_instance.team = TEAM_SUPPORT
                else:
                    pass

                req_instance.save() # Guardar ahora que tiene equipo

                if req_instance.status == 'scheduled':
                    messages.success(request,
                                     _('User Records Request ({code}) has been scheduled for {date} for {team} team!').format(
                                         code=req_instance.unique_code,
                                         date=req_instance.scheduled_date.strftime('%Y-%m-%d'),
                                         team=req_instance.get_team_display() or "Unassigned"))
                else:
                    messages.success(request,
                                     _('User Records Request ({code}) created successfully for {team} team!').format(
                                         code=req_instance.unique_code,
                                         team=req_instance.get_team_display() or "Unassigned"))
                return redirect('tasks:portal_dashboard')
            except ValueError as ve:  # Para el error de team_selection
                messages.error(request, str(ve))
            except Exception as e:
                logger.error(f"Error saving UserRecordsRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
            # En caso de error, volver a renderizar con los datos actuales
            return render(request, 'tasks/user_records_request.html',
                          {'user_records_form': user_records_form, 'user_group_formset': user_group_formset})
        else:  # Formulario principal o formset no son válidos
            return render(request, 'tasks/user_records_request.html',
                          {'user_records_form': user_records_form, 'user_group_formset': user_group_formset})
    else:  # GET request
        user_records_form = UserRecordsRequestForm(user=user)
        user_group_formset = UserGroupFormSet(prefix='groups')
    return render(request, 'tasks/user_records_request.html',
                  {'user_records_form': user_records_form, 'user_group_formset': user_group_formset})


@login_required
@user_passes_test(user_belongs_to_revenue_or_support) # Permiso
def deactivation_toggle_request(request):
    user = request.user
    is_in_revenue = user_in_group(user, TEAM_REVENUE)
    is_in_support = user_in_group(user, TEAM_SUPPORT)
    is_leader = user_in_group(user, TEAM_LEADERSHIPS)

    if is_in_revenue and is_in_support:
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:portal_dashboard')

    if request.method == 'POST':
         # Pasar user al form
        form = DeactivationToggleRequestForm(request.POST, user=user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()
                deact_toggle_request = form.save(commit=False)
                deact_toggle_request.requested_by = user
                deact_toggle_request.type_of_process = 'deactivation_toggle'
                deact_toggle_request.timestamp = creation_timestamp

                # Lógica de estado inicial (Pending for Approval o Pending) y Programación
                schedule_request_flag = form.cleaned_data.get('schedule_request')
                scheduled_date_value = form.cleaned_data.get('scheduled_date')

                # --- Lógica de Estado (como estaba antes) ---
                types_requiring_approval = [
                    'partner_deactivation', 'property_deactivation',
                    'toggle_off_invites', 'toggle_off_homepage_signups',
                ]
                requires_approval = form.cleaned_data.get('deactivation_toggle_type') in types_requiring_approval

                if schedule_request_flag and scheduled_date_value:
                    deact_toggle_request.scheduled_date = scheduled_date_value
                    if requires_approval and not is_leader:
                        deact_toggle_request.status = 'pending_approval'
                        deact_toggle_request.effective_start_time_for_tat = None  # TAT no inicia
                        logger.info(f"DeactivationRequest by {user.email} scheduled for {scheduled_date_value} and is PENDING APPROVAL.")
                    else:
                        deact_toggle_request.status = 'scheduled'
                        deact_toggle_request.effective_start_time_for_tat = None  # TAT no inicia
                        logger.info(f"DeactivationRequest by {user.email} scheduled for {scheduled_date_value}.")
                else:  # No se programa
                    deact_toggle_request.scheduled_date = None
                    if requires_approval and not is_leader:
                        deact_toggle_request.status = 'pending_approval'
                        deact_toggle_request.effective_start_time_for_tat = None  # TAT no inicia
                        logger.info(f"DeactivationRequest by {user.email} created as PENDING APPROVAL.")
                    else:
                        deact_toggle_request.status = 'pending'
                        deact_toggle_request.effective_start_time_for_tat = creation_timestamp  # TAT inicia
                        logger.info(f"DeactivationRequest by {user.email} created as PENDING. TAT start: {creation_timestamp}")

                # Asignación de equipo (ajusta esta lógica si Deactivation/Toggle tiene reglas diferentes)
                if is_in_revenue:
                    deact_toggle_request.team = TEAM_REVENUE
                elif is_in_support:
                    deact_toggle_request.team = TEAM_SUPPORT
                else:
                    pass

                if not deact_toggle_request.team:
                    messages.error(request,_('Failed to assign team. Ensure your user belongs to a valid operational team or a default is set.'))
                    return render(request, 'tasks/deactivation_toggle_request.html', {'form': form})

                deact_toggle_request.save()

                # Mensaje de éxito
                success_message = _('Deactivation/Toggle Request ({code}) for {team} team ').format(
                    code=deact_toggle_request.unique_code,
                    team=deact_toggle_request.get_team_display() or "Unassigned"
                )
                if deact_toggle_request.status == 'scheduled':
                    success_message += _('has been scheduled for {date}!').format(date=deact_toggle_request.scheduled_date.strftime('%Y-%m-%d'))
                elif deact_toggle_request.status == 'pending_approval':
                    success_message += _('is now pending approval')
                    if deact_toggle_request.scheduled_date:
                        success_message += _(' and is scheduled for {date}.').format(date=deact_toggle_request.scheduled_date.strftime('%Y-%m-%d'))
                    else:
                        success_message += "."
                else:  # pending
                    success_message += _('created successfully!')

                messages.success(request, success_message)
                return redirect('tasks:portal_dashboard')
            except Exception as e:
                logger.error(f"Error saving DeactivationToggleRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
        else:  # form.is_valid() es False
            logger.warning(f"DeactivationToggleRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            messages.error(request, _('Please correct the errors below.'))
    else:  # GET request
        form = DeactivationToggleRequestForm(user=user)

    return render(request, 'tasks/deactivation_toggle_request.html', {'form': form})

@login_required
@user_passes_test(user_belongs_to_revenue_or_support) # Permiso
def unit_transfer_request(request):
    user = request.user
    is_in_revenue = user_in_group(user, TEAM_REVENUE)
    is_in_support = user_in_group(user, TEAM_SUPPORT)

    if is_in_revenue and is_in_support:
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:portal_dashboard')

    if request.method == 'POST':
        # Pasar user y FILES
        form = UnitTransferRequestForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()
                unit_transfer_request = form.save(commit=False)
                unit_transfer_request.requested_by = user
                unit_transfer_request.type_of_process = 'unit_transfer'
                unit_transfer_request.timestamp = creation_timestamp

                schedule_request_flag = form.cleaned_data.get('schedule_request')
                scheduled_date_value = form.cleaned_data.get('scheduled_date')

                if schedule_request_flag and scheduled_date_value:
                    unit_transfer_request.status = 'scheduled'
                    unit_transfer_request.scheduled_date = scheduled_date_value
                    unit_transfer_request.effective_start_time_for_tat = None
                else:
                    unit_transfer_request.status = 'pending'
                    unit_transfer_request.scheduled_date = None
                    unit_transfer_request.effective_start_time_for_tat = creation_timestamp

                # --- ASIGNAR EQUIPO ---
                if is_in_revenue:
                    unit_transfer_request.team = TEAM_REVENUE
                elif is_in_support:
                    unit_transfer_request.team = TEAM_SUPPORT
                else:
                    pass

                if not unit_transfer_request.team:
                    messages.error(request,_('Failed to assign team. Ensure your user belongs to a valid operational team or a default is set.'))
                    return render(request, 'tasks/unit_transfer_request.html', {'form': form})

                unit_transfer_request.save()

                if unit_transfer_request.status == 'scheduled':
                    messages.success(request,_('Unit Transfer Request ({code}) has been scheduled for {date} for {team} team!').format(
                        code=unit_transfer_request.unique_code,
                        date=unit_transfer_request.scheduled_date.strftime('%Y-%m-%d'),
                        team=unit_transfer_request.get_team_display() or "Unassigned"))
                else:
                    messages.success(request,_('Unit Transfer Request ({code}) created successfully for {team} team!').format(
                                     code=unit_transfer_request.unique_code,
                                     team=unit_transfer_request.get_team_display() or "Unassigned"))
                return redirect('tasks:portal_dashboard')
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                logger.error(f"Error saving UnitTransferRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
            return render(request, 'tasks/unit_transfer_request.html', {'form': form})
        else:
            logger.warning(f"UnitTransferRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            messages.error(request, _('Please correct the errors below.'))
            return render(request, 'tasks/unit_transfer_request.html', {'form': form})
    else:  # GET request
        form = UnitTransferRequestForm(user=user)
    return render(request, 'tasks/unit_transfer_request.html', {'form': form})

@login_required
@user_passes_test(user_belongs_to_compliance)
def generating_xml_request(request):
    # (Código de la vista generating_xml_request como estaba antes)
    if request.method == 'POST':
        form = GeneratingXmlRequestForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()
                xml_request = form.save(commit=False)
                xml_request.requested_by = request.user
                xml_request.type_of_process = 'generating_xml'
                xml_request.timestamp = creation_timestamp
                xml_request.status = 'pending'
                xml_request.priority = PRIORITY_NORMAL
                xml_request.team = TEAM_COMPLIANCE
                xml_request.scheduled_date = None
                xml_request.effective_start_time_for_tat = creation_timestamp

                xml_request.save()
                logger.info(f"Generating XML Request ({xml_request.unique_code}) created by {request.user.email} with priority '{xml_request.priority}' for team '{xml_request.team}'. TAT start: {creation_timestamp}")
                messages.success(request, _('Generating XML files Request ({code}) created successfully!').format(code=xml_request.unique_code))
                return redirect('tasks:portal_dashboard')
            except Exception as e:
                logger.error(f"Error saving GeneratingXmlRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
        else:
            logger.warning(f"GeneratingXmlRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = GeneratingXmlRequestForm()
    return render(request, 'tasks/generating_xml_request.html', {'form': form})


# --- Dashboard y Detalles ---
@login_required
def portal_operations_dashboard(request):
    user = request.user
    is_admin_user = is_admin(user)
    is_leadership_user = is_leadership(user)

    tipos_de_proceso_choices = TYPE_CHOICES
    statuses_choices = STATUS_CHOICES
    team_choices = TEAM_CHOICES # Para el filtro

    # Obtener valores de los filtros GET
    tipo_seleccionado = request.GET.get('type')
    status_seleccionado = request.GET.get('status')
    team_seleccionado = request.GET.get('team') # Nuevo filtro
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Query base: Selecciona todos los requests
    # Incluimos el team en select_related si lo vas a mostrar y ayuda al rendimiento
    requests_query = UserRecordsRequest.objects.select_related(
        'requested_by', 'operator', 'qa_agent', #'team' # Team es CharField, no necesita select_related
    ).all() # .all() es opcional aquí

    # --- Aplicar Filtros Opcionales ---

    # Filtrar por Tipo de Proceso
    valid_types = [choice[0] for choice in tipos_de_proceso_choices]
    if tipo_seleccionado and tipo_seleccionado in valid_types:
        requests_query = requests_query.filter(type_of_process=tipo_seleccionado)

    # Filtrar por Estado
    valid_statuses = [choice[0] for choice in statuses_choices]
    if status_seleccionado and status_seleccionado in valid_statuses:
        requests_query = requests_query.filter(status=status_seleccionado)

    # Filtrar por Equipo (NUEVO)
    valid_teams = [choice[0] for choice in team_choices]
    if team_seleccionado and team_seleccionado in valid_teams:
        requests_query = requests_query.filter(team=team_seleccionado)

    # Filtrar por Fechas (sin cambios)
    # ... (tu lógica existente para filtrar por start_date y end_date) ...
    user_timezone_str = request.user.timezone if request.user.timezone else 'UTC'
    try: user_timezone = pytz.timezone(user_timezone_str)
    except pytz.UnknownTimeZoneError: user_timezone = pytz.utc; messages.warning(request, _("Invalid timezone '{tz}'. Using UTC for date filters.").format(tz=user_timezone_str))
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            start_datetime_local = user_timezone.localize(datetime.combine(start_date, time.min))
            requests_query = requests_query.filter(timestamp__gte=start_datetime_local.astimezone(pytz.utc))
        except ValueError: messages.error(request, _("Invalid start date format."))
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            end_datetime_local = user_timezone.localize(datetime.combine(end_date, time.max))
            requests_query = requests_query.filter(timestamp__lte=end_datetime_local.astimezone(pytz.utc))
        except ValueError: messages.error(request, _("Invalid end date format."))


    # Orden y Paginación (sin cambios)
    requests_query = requests_query.order_by('-timestamp')
    paginator = Paginator(requests_query, 25) # O el número que prefieras
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'tipos_de_proceso_choices': tipos_de_proceso_choices,
        'statuses_choices': statuses_choices,
        'team_choices': team_choices, # Pasar choices de equipo al template
        # Pasar filtros actuales para mantenerlos en UI y paginación
        'current_type_filter': tipo_seleccionado,
        'current_status_filter': status_seleccionado,
        'current_team_filter': team_seleccionado, # Pasar filtro de equipo actual
        'start_date': start_date_str,
        'end_date': end_date_str,
        'is_admin_user': is_admin_user,
        'is_leadership_user': is_leadership_user,
    }
    return render(request, 'tasks/rhino_operations_dashboard.html', context)

@login_required
def request_detail(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user

    # Verificar permisos de visualización
    if not can_view_request(user, user_request):  # Reemplaza can_view_request con tu lógica si es diferente
        messages.error(request, _("You do not have permission to view this request."))
        return redirect('tasks:portal_dashboard')

    # Obtener datos para el contexto
    is_agent_user = is_agent(user)
    is_admin_user = is_admin(user)
    is_leadership_user = is_leadership(user)
    blocked_history = user_request.blocked_messages.select_related('blocked_by').order_by('-blocked_at')
    resolved_history = user_request.resolved_messages.select_related('resolved_by').order_by('-resolved_at')
    rejected_history = user_request.rejected_messages.select_related('rejected_by').order_by('-rejected_at')
    processed_group_data = [] # Para User Records
    address_files = None      # Para Address Validation
    request_files = None      # Podríamos usar esto para otros tipos si unificamos
    total_user_records_emails = 0
    unit_transfer_email_count = 0
    prefill_user_count = None
    if user_request.type_of_process == 'user_records' and user_request.user_groups_data:
        access_level_dict = dict(ACCESS_LEVEL_CHOICES)
        emails_found_in_groups = False
        try:
            for group in user_request.user_groups_data:
                 processed_group = group.copy()
                 access_level_key = group.get('access_level')
                 processed_group['access_level_display'] = access_level_dict.get(access_level_key, access_level_key or "N/A")
                 processed_group_data.append(processed_group) # noqa: E701

                 # --- CONTAR EMAILS ---
                 email_list = group.get('user_email_addresses', [])  # Obtener la lista de emails
                 if isinstance(email_list, list):  # Asegurarse que es una lista
                    count_in_group = len(email_list)
                    total_user_records_emails += count_in_group
                    if count_in_group > 0:
                        emails_found_in_groups = True

            if not user_request.user_file and emails_found_in_groups:
                prefill_user_count = total_user_records_emails
        except Exception as e:
            logger.error(f"Error processing groups data or counting emails for request {pk}: {e}")
            # Resetear en caso de error
            processed_group_data = []
            total_user_records_emails = 0
            prefill_user_count = None  # Asegurar que sea None si hay error

    elif user_request.type_of_process == 'unit_transfer':
        email_string = user_request.unit_transfer_user_email_addresses or ""
        # Dividir por coma o nueva línea, quitar espacios y contar elementos no vacíos
        emails = [e.strip() for e in re.split('[,\n]', email_string) if e.strip()]
        unit_transfer_email_count = len(emails)
        # Pre-llenar si hay emails en el campo específico de unit transfer
        if unit_transfer_email_count > 0:
            prefill_user_count = unit_transfer_email_count

    elif user_request.type_of_process == 'address_validation':
        logger.info(f"Fetching address validation files for request PK: {user_request.pk}")
        address_files = user_request.address_validation_files.all()
        try:
            # Usar el related_name correcto definido en el modelo AddressValidationFile
            address_files = user_request.address_validation_files.all()
            logger.info(f"Found {address_files.count()} address validation file(s) in view.")
        except Exception as e:
            logger.error(f"Error fetching address validation files for request PK {user_request.pk}: {e}", exc_info=True)
            address_files = None # Asegurar que es None si hay error

    can_reject_request = False
    # Define en qué estados se puede rechazar
    rejectable_statuses = ['qa_in_progress', 'completed']  # Ajusta si necesitas otros estados

    if user_request.status in rejectable_statuses:
        # Verifica si el usuario actual es el QA asignado
        is_qa_agent_match = (is_agent_user and user_request.qa_agent == user)
        # Verifica si el usuario actual es el creador
        is_requester = (user == user_request.requested_by)

        # Comprueba si el usuario cumple *alguna* condición
        can_reject_request = (
                is_admin(user)  # Llama helper directamente
                or is_leadership_user  # Usa variable del contexto
                or is_qa_agent_match
                or is_requester  # <-- Añadida condición del creador
        )
    # --- *** INICIO CÁLCULOS NUEVOS BOTONES UPDATE *** ---
    can_request_update_action = False
    can_clear_update_flag_action = False

    # Estados activos (no finalizados) donde se puede pedir/proveer update
    active_statuses = [st[0] for st in STATUS_CHOICES if st[0] not in ['completed', 'cancelled']]

    if user_request.status in active_statuses:
        # ¿Puede el usuario actual pedir update? (Team/Admin/Leader Y flag está apagada)
        user_can_trigger_flag = (
                (user_request.team and user_in_group(user, user_request.team)) or
                is_admin(user) or
                is_leadership_user
        )
        if user_can_trigger_flag and not user_request.update_needed_flag:
            can_request_update_action = True

        # ¿Puede el usuario actual (agente) marcar el update como provisto? (Agente Y flag está prendida)
        if is_agent_user and user_request.update_needed_flag:
            can_clear_update_flag_action = True

    can_cancel_request = False
    can_uncancel_request = False

    # Determinar permiso base (Team/Admin/Leader)
    user_is_privileged_or_team = (
            (user_request.team and user_in_group(user, user_request.team)) or
            is_admin(user) or
            is_leadership_user
    )

    # Puede cancelar si tiene permiso Y el estado NO es final
    non_cancellable_statuses = ['completed', 'cancelled']
    if user_is_privileged_or_team and user_request.status not in non_cancellable_statuses:
        can_cancel_request = True

    # Puede descancelar si tiene permiso Y el estado ES cancelado
    if user_is_privileged_or_team and user_request.status == 'cancelled':
        can_uncancel_request = True

    template_map = {
        'user_records': 'tasks/user_records_detail.html',
        'deactivation_toggle': 'tasks/deactivation_toggle_detail.html',
        'unit_transfer': 'tasks/unit_transfer_detail.html',
        'generating_xml': 'tasks/generating_xml_detail.html',
        'address_validation': 'tasks/address_validation_detail.html',
        'stripe_disputes': 'tasks/stripe_disputes_detail.html',
        'property_records': 'tasks/property_records_detail.html',
    }
    detail_template = template_map.get(user_request.type_of_process, 'tasks/user_records_detail.html')

    # Construir el contexto
    context = {
        'user_request': user_request,
        'is_agent_user': is_agent_user,
        'is_leadership_user': is_leadership_user,
        'blocked_history': blocked_history,
        'resolved_history': resolved_history,
        'rejected_history': rejected_history,
        'processed_user_groups': processed_group_data,
        'address_files': address_files,
        'request_files': request_files,
        'total_user_records_emails': total_user_records_emails,
        'unit_transfer_email_count': unit_transfer_email_count,
        'prefill_user_count': prefill_user_count,
        'can_reject_request': can_reject_request,
        'can_request_update_action': can_request_update_action,
        'can_clear_update_flag_action': can_clear_update_flag_action,
        'update_needed': user_request.update_needed_flag,
        'can_cancel_request': can_cancel_request,
        'can_uncancel_request': can_uncancel_request,
    }

    if user_request.type_of_process == 'generating_xml':
        form_instance_for_modal = GeneratingXmlOperateForm(instance=user_request)
        context['form_for_modal'] = form_instance_for_modal
        logger.debug(f"Added GeneratingXmlOperateForm to context for GXML request {pk}. Fields: {list(form_instance_for_modal.fields.keys())}")

    logger.debug(f"Rendering template '{detail_template}' with context keys: {list(context.keys())}")
    if address_files is not None:
        logger.debug(f"  Context['address_files'] QuerySet: {address_files}")

    return render(request, detail_template, context)

# --- Vistas de Acción ---
# (Código para operate_request, block_request, resolve_request, etc., como estaba antes)
@login_required
def operate_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    if not is_agent(request.user): messages.error(request, _("You do not have permission to perform this operation.")); return redirect('tasks:request_detail', pk=pk)

    if user_request.status == 'scheduled':
        messages.warning(request, _("This request is scheduled and cannot be operated on yet."))
        return redirect('tasks:request_detail', pk=pk)

    allowed_statuses = ['pending', 'completed']
    if user_request.status in allowed_statuses:
        if request.method == 'POST':
            if user_request.status == 'pending' and user_request.uncanceled_by is not None:
                user_request.uncanceled_by = None
                user_request.uncanceled_at = None
            user_request.status = 'in_progress'
            user_request.operator = request.user
            user_request.operated_at = timezone.now()
            user_request.qa_agent = None
            user_request.qa_pending_at = None
            user_request.qa_in_progress_at = None
            user_request.completed_at = None
            user_request.save()
            messages.success(request, _('Request status set to "In Progress". You are assigned as the operator.'))
        else: messages.warning(request, _("Use the 'Operate' button to start processing this request."))
    else: messages.warning(request, _('This request cannot be operated from its current status ({status}).').format(status=user_request.get_status_display()))
    return redirect('tasks:request_detail', pk=pk)

@login_required
def block_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    # Asegúrate que la lógica de permisos para bloquear sea la que necesitas
    if not is_agent(request.user):
        messages.error(request, _("You do not have permission to block requests."))
        return redirect('tasks:request_detail', pk=pk)

    allowed_statuses = ['pending', 'in_progress']
    if user_request.status not in allowed_statuses:
        messages.error(request, _('This request cannot be blocked from its current status ({status}).').format(
            status=user_request.get_status_display()))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        form = BlockForm(request.POST)
        if form.is_valid():
            block_reason = form.cleaned_data['reason']
            django_update_successful = False
            try:
                # 1. Bloquear la solicitud en Django (esto siempre se intenta primero)
                with transaction.atomic():  # Usar transacción por si algo falla con el mensaje
                    BlockedMessage.objects.create(
                        request=user_request,
                        blocked_by=request.user,
                        reason=block_reason,
                        blocked_at=timezone.now()
                    )
                    user_request.status = 'blocked'
                    user_request.save(update_fields=['status'])
                django_update_successful = True
                logger.info(f"Request {user_request.unique_code} blocked in Portal by {request.user.email}.")

            except Exception as e_django:
                logger.error(f"Error blocking request {pk} in Django: {e_django}", exc_info=True)
                messages.error(request, _("An error occurred while blocking the request in Django."))
                # Si falla el bloqueo en Django, no continuamos a Salesforce
                return render(request, 'tasks/block_form.html', {'form': form, 'user_request': user_request})

            if django_update_successful:
                # 2. Intentar actualizar Salesforce CONDICIONALMENTE
                #    Solo para 'address_validation' Y si tiene 'salesforce_standard_opp_id'
                if user_request.type_of_process == 'address_validation' and user_request.salesforce_standard_opp_id:
                    logger.info(
                        f"Attempting to update Salesforce Opportunity {user_request.salesforce_standard_opp_id} for blocked request {user_request.unique_code}")
                    try:
                        sf = Salesforce(
                            username=settings.SF_USERNAME,
                            password=settings.SF_PASSWORD,
                            security_token=settings.SF_SECURITY_TOKEN,
                            consumer_key=settings.SF_CONSUMER_KEY,
                            consumer_secret=settings.SF_CONSUMER_SECRET,
                            domain=settings.SF_DOMAIN,
                            version=settings.SF_VERSION
                        )

                        sf_update_data = {
                            'Invisible_Status__c': 'Escalated',
                            'Invisible_Comments__c': f"Request {user_request.unique_code} blocked by {request.user.email}. Reason: {block_reason}"
                        }

                        sf.Opportunity.update(user_request.salesforce_standard_opp_id, sf_update_data)
                        logger.info(
                            f"Successfully updated Salesforce Opportunity {user_request.salesforce_standard_opp_id}: Status to Escalated, Comments added.")
                        messages.success(request,
                                         _('Request blocked successfully and Salesforce Opportunity updated to "Escalated".'))

                    except SalesforceError as e_sf:
                        logger.error(
                            f"Salesforce API Error updating Opportunity {user_request.salesforce_standard_opp_id} for request {pk}: {str(e_sf)} - Content: {e_sf.content if hasattr(e_sf, 'content') else 'N/A'}",
                            exc_info=True)
                        messages.warning(request,
                                         _('Request blocked in Django, but FAILED to update Salesforce. Please check Salesforce manually. Error: {error_type}').format(
                                             error_type=type(e_sf).__name__))
                    except Exception as e_conn_sf:
                        logger.error(
                            f"Unexpected error connecting or updating Salesforce Opportunity {user_request.salesforce_standard_opp_id} for request {pk}: {e_conn_sf}",
                            exc_info=True)
                        messages.warning(request,
                                         _('Request blocked in Django, but an UNEXPECTED error occurred trying to update Salesforce. Please check Salesforce manually.'))
                else:
                    # No es un request de Address Validation originado en SF, o no tiene el ID de SF.
                    logger.info(
                        f"Request {user_request.unique_code} (Type: {user_request.get_type_of_process_display()}) blocked in Django. No Salesforce update attempted as it's not an AV request from SF or missing SF Opp ID.")
                    messages.success(request, _('Request blocked successfully.'))

                return redirect('tasks:request_detail', pk=pk)
        else:
            # El formulario de bloqueo (BlockForm) no es válido
            messages.error(request, _("The reason for blocking was not provided or was invalid."))
            return render(request, 'tasks/block_form.html', {'form': form, 'user_request': user_request})
    else:  # GET
        form = BlockForm()
    # El modal se encarga de mostrar el form, pero si se accede a la URL directa:
    return render(request, 'tasks/block_form.html', {'form': form, 'user_request': user_request})


@login_required
def resolve_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    # Lógica de permisos para resolver (puedes ajustarla según tus necesidades)
    can_resolve = (
            is_agent(request.user) or
            user_in_group(user_request.requested_by, TEAM_REVENUE) or
            user_in_group(user_request.requested_by, TEAM_SUPPORT) or
            is_admin(request.user) or
            is_leadership(request.user)  # Añadido Leadership por consistencia si pueden resolver
    )
    if not can_resolve:
        messages.error(request, _("You do not have permission to resolve this request."))
        return redirect('tasks:request_detail', pk=pk)

    if user_request.status != 'blocked':
        messages.error(request, _('This request is not currently blocked and cannot be resolved.'))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        form = ResolveForm(request.POST, request.FILES)
        if form.is_valid():
            resolve_message_text = form.cleaned_data['message']
            django_update_successful = False
            try:
                # 1. Resolver la solicitud en Django
                with transaction.atomic():
                    current_time = timezone.now()
                    ResolvedMessage.objects.create(
                        request=user_request,
                        resolved_by=request.user,
                        message=resolve_message_text,
                        resolved_file=form.cleaned_data.get('resolved_file'),
                        resolved_link=form.cleaned_data.get('resolved_link'),
                        resolved_at=current_time,
                    )
                    user_request.status = 'pending'  # Vuelve a 'Pending' después de resolverse
                    user_request.effective_start_time_for_tat = current_time  # Reiniciar TAT
                    user_request.save(update_fields=['status', 'effective_start_time_for_tat'])
                django_update_successful = True
                logger.info(
                    f"Request {user_request.unique_code} resolved in Portal by {request.user.email}. TAT reset.")

            except Exception as e_django:
                logger.error(f"Error resolving request {pk} in Django: {e_django}", exc_info=True)
                messages.error(request, _("An error occurred while resolving the request in Django."))
                return render(request, 'tasks/resolve_form.html', {'form': form, 'user_request': user_request})

            if django_update_successful:
                salesforce_updated_or_not_attempted = True

                # 2. Intentar actualizar Salesforce CONDICIONALMENTE
                if user_request.type_of_process == 'address_validation' and user_request.salesforce_standard_opp_id:
                    logger.info(
                        f"Attempting to update Salesforce Opportunity {user_request.salesforce_standard_opp_id} for resolved request {user_request.unique_code}")
                    try:
                        sf = Salesforce(
                            username=settings.SF_USERNAME,
                            password=settings.SF_PASSWORD,
                            security_token=settings.SF_SECURITY_TOKEN,
                            consumer_key=settings.SF_CONSUMER_KEY,
                            consumer_secret=settings.SF_CONSUMER_SECRET,
                            domain=settings.SF_DOMAIN,
                            version=settings.SF_VERSION
                        )

                        # Datos para Salesforce: Cambiar estado y opcionalmente añadir comentario de resolución
                        sf_update_data = {
                            'Invisible_Status__c': 'In Progress',  # Volver a 'In Progress'
                            # Opcional: Actualizar Invisible_Comments__c
                            'Invisible_Comments__c': f"Request {user_request.unique_code} resolved in Django by {request.user.email}. Message: {resolve_message_text[:200]}"
                            # Truncar mensaje si es muy largo para el campo de SF
                        }

                        sf.Opportunity.update(user_request.salesforce_standard_opp_id, sf_update_data)
                        logger.info(
                            f"Successfully updated Salesforce Opportunity {user_request.salesforce_standard_opp_id}: Status to In Progress, Comments updated.")
                        messages.success(request,
                                         _('Request resolved successfully and Salesforce Opportunity status updated to "In Progress".'))

                    except SalesforceError as e_sf:
                        salesforce_updated_or_not_attempted = False
                        logger.error(
                            f"Salesforce API Error updating Opportunity {user_request.salesforce_standard_opp_id} for resolved request {pk}: {str(e_sf)} - Content: {e_sf.content if hasattr(e_sf, 'content') else 'N/A'}",
                            exc_info=True)
                        messages.warning(request,
                                         _('Request resolved in Django, but FAILED to update Salesforce. Please check Salesforce manually. Error: {error_type}').format(
                                             error_type=type(e_sf).__name__))
                    except Exception as e_conn_sf:
                        salesforce_updated_or_not_attempted = False
                        logger.error(
                            f"Unexpected error connecting or updating Salesforce Opportunity {user_request.salesforce_standard_opp_id} for resolved request {pk}: {e_conn_sf}",
                            exc_info=True)
                        messages.warning(request,
                                         _('Request resolved in Django, but an UNEXPECTED error occurred trying to update Salesforce. Please check Salesforce manually.'))
                else:
                    logger.info(
                        f"Request {user_request.unique_code} (Type: {user_request.get_type_of_process_display()}) resolved in Django. No Salesforce update attempted.")
                    messages.success(request, _('Request resolved successfully.'))

                return redirect('tasks:request_detail', pk=pk)
        else:  # form not valid
            messages.error(request, _("Please correct the errors in the resolution form."))
            return render(request, 'tasks/resolve_form.html', {'form': form, 'user_request': user_request})
    else:  # GET
        form = ResolveForm()
    return render(request, 'tasks/resolve_form.html', {'form': form, 'user_request': user_request})

@login_required
def send_to_qa_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    if not is_agent(request.user) or user_request.operator != request.user:
        messages.error(request, _("Only the assigned operator can send this request to QA."))
        return redirect('tasks:request_detail', pk=pk)
    if user_request.status != 'in_progress':
        messages.error(request, _('This request must be "In Progress" to be sent to QA.'))
        return redirect('tasks:request_detail', pk=pk)

    CurrentFormClass = OperateForm
    if user_request.type_of_process == 'generating_xml':
        CurrentFormClass = GeneratingXmlOperateForm

    if request.method == 'POST':
        form = CurrentFormClass(request.POST, request.FILES, instance=user_request)
        if isinstance(form, GeneratingXmlOperateForm):
            if 'qa_needs_file_correction' in form.fields:
                form.fields['qa_needs_file_correction'].widget = forms.HiddenInput()
                form.fields['qa_needs_file_correction'].required = False

        if form.is_valid():
            try:
                with transaction.atomic():
                    saved_instance = form.save()  # Llama al save() personalizado de GeneratingXmlOperateForm si aplica

                    saved_instance.status = 'qa_pending'
                    saved_instance.qa_pending_at = timezone.now()
                    saved_instance.is_rejected_previously = False

                    # Solo actualizamos campos de estado y fecha; form.save() ya guardó los otros
                    saved_instance.save(update_fields=['status', 'qa_pending_at', 'is_rejected_previously'])

                logger.info(f"Request {pk} ({user_request.type_of_process}) sent to QA by {request.user.email}.")
                messages.success(request, _('Request sent to QA pending queue.'))
                return redirect('tasks:request_detail', pk=pk)
            except Exception as e:
                logger.error(f"Error sending request {pk} to QA: {e}", exc_info=True)
                messages.error(request, _("An error occurred while sending the request to QA."))
        else:
            logger.warning(f"Form ({CurrentFormClass.__name__}) for request {pk} is not valid on send_to_qa: {form.errors.as_json(escape_html=True)}")
        return redirect('tasks:request_detail', pk=pk)
    else:
        return redirect('tasks:request_detail', pk=pk)  # GET no debería llegar aquí desde el modal

@login_required
def qa_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    if not is_agent(request.user): messages.error(request, _("You do not have permission to perform QA.")); return redirect('tasks:request_detail', pk=pk)
    if user_request.status != 'qa_pending': messages.error(request, _('This request is not pending QA.')); return redirect('tasks:request_detail', pk=pk)
    if request.method == 'POST':
        user_request.status = 'qa_in_progress'; user_request.qa_agent = request.user; user_request.qa_in_progress_at = timezone.now()
        user_request.save(update_fields=['status', 'qa_agent', 'qa_in_progress_at'])
        messages.success(request, _('Request QA is now in progress by you.'))
    else: messages.warning(request, _("Use the 'QA' button to start the quality assurance process."))
    return redirect('tasks:request_detail', pk=pk)

@login_required
def complete_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    can_complete = is_agent(request.user) and (user_request.status == 'qa_in_progress' and user_request.qa_agent == request.user)
    if not can_complete:
        messages.error(request, _("You do not have permission to complete this request or it's not in the correct state."))
        return redirect('tasks:request_detail', pk=pk)

    CurrentFormClass = OperateForm
    template_to_render = 'tasks/complete_form.html'

    if user_request.type_of_process == 'generating_xml':
        CurrentFormClass = GeneratingXmlOperateForm

    if request.method == 'POST':
        form = CurrentFormClass(request.POST, request.FILES, instance=user_request)
        if form.is_valid():
            django_save_successful = False
            try:
                with transaction.atomic():
                    updated_instance = form.save(commit=False)
                    updated_instance.status = 'completed'
                    updated_instance.completed_at = timezone.now()
                    try:
                        prices = OperationPrice.objects.first()
                        if prices:
                            updated_instance.subtotal_user_update_client_price_completed = (Decimal(updated_instance.num_updated_users or 0) * prices.user_update_price)
                            updated_instance.subtotal_property_update_client_price_completed = (Decimal(updated_instance.num_updated_properties or 0) * prices.property_update_price)
                            updated_instance.subtotal_bulk_update_client_price_completed = (Decimal(updated_instance.bulk_updates or 0) * prices.bulk_update_price)
                            updated_instance.subtotal_manual_property_update_client_price_completed = (Decimal(updated_instance.manual_updated_properties or 0) * prices.manual_property_update_price)
                            updated_instance.subtotal_csv_update_client_price_completed = (Decimal(updated_instance.update_by_csv_rows or 0) * prices.csv_update_price)
                            updated_instance.subtotal_processing_report_client_price_completed = (Decimal(updated_instance.processing_reports_rows or 0) * prices.processing_report_price)
                            updated_instance.subtotal_manual_unit_update_client_price_completed = (Decimal(updated_instance.manual_updated_units or 0) * prices.manual_unit_update_price)
                            updated_instance.subtotal_address_validation_unit_client_price_completed = (Decimal(updated_instance.av_number_of_units or 0) * prices.address_validation_unit_price)
                            stripe_total_disputes = (updated_instance.stripe_premium_disputes or 0) + (updated_instance.stripe_ri_disputes or 0)
                            updated_instance.subtotal_stripe_dispute_client_price_completed = (Decimal(stripe_total_disputes) * prices.stripe_dispute_price)

                            xml_carrier_count = 0
                            if updated_instance.xml_carrier_rvic: xml_carrier_count += 1
                            if updated_instance.xml_carrier_ssic: xml_carrier_count += 1
                            updated_instance.subtotal_xml_file_client_price_completed = (Decimal(xml_carrier_count) * prices.xml_file_price)

                            updated_instance.grand_total_client_price_completed = (
                                    updated_instance.subtotal_user_update_client_price_completed +
                                    updated_instance.subtotal_property_update_client_price_completed +
                                    updated_instance.subtotal_bulk_update_client_price_completed +
                                    updated_instance.subtotal_manual_property_update_client_price_completed +
                                    updated_instance.subtotal_csv_update_client_price_completed +
                                    updated_instance.subtotal_processing_report_client_price_completed +
                                    updated_instance.subtotal_manual_unit_update_client_price_completed +
                                    updated_instance.subtotal_address_validation_unit_client_price_completed +
                                    updated_instance.subtotal_stripe_dispute_client_price_completed +
                                    updated_instance.subtotal_xml_file_client_price_completed
                            )

                            # Operate Costs Calculation
                            updated_instance.subtotal_user_update_operate_cost_completed = (Decimal(updated_instance.num_updated_users or 0) * prices.user_update_operate_cost)
                            updated_instance.subtotal_property_update_operate_cost_completed = (Decimal(updated_instance.num_updated_properties or 0) * prices.property_update_operate_cost)
                            updated_instance.subtotal_bulk_update_operate_cost_completed = (Decimal(updated_instance.bulk_updates or 0) * prices.bulk_update_operate_cost)
                            updated_instance.subtotal_manual_property_update_operate_cost_completed = (Decimal(updated_instance.manual_updated_properties or 0) * prices.manual_property_update_operate_cost)
                            updated_instance.subtotal_csv_update_operate_cost_completed = (Decimal(updated_instance.update_by_csv_rows or 0) * prices.csv_update_operate_cost)
                            updated_instance.subtotal_processing_report_operate_cost_completed = (Decimal(updated_instance.processing_reports_rows or 0) * prices.processing_report_operate_cost)
                            updated_instance.subtotal_manual_unit_update_operate_cost_completed = (Decimal(updated_instance.manual_updated_units or 0) * prices.manual_unit_update_operate_cost)
                            updated_instance.subtotal_address_validation_unit_operate_cost_completed = (Decimal(updated_instance.av_number_of_units or 0) * prices.address_validation_unit_operate_cost)
                            updated_instance.subtotal_stripe_dispute_operate_cost_completed = (Decimal(stripe_total_disputes) * prices.stripe_dispute_operate_cost)
                            updated_instance.subtotal_xml_file_operate_cost_completed = (Decimal(xml_carrier_count) * prices.xml_file_operate_cost)

                            updated_instance.grand_total_operate_cost_completed = (
                                    updated_instance.subtotal_user_update_operate_cost_completed +
                                    updated_instance.subtotal_property_update_operate_cost_completed +
                                    updated_instance.subtotal_bulk_update_operate_cost_completed +
                                    updated_instance.subtotal_manual_property_update_operate_cost_completed +
                                    updated_instance.subtotal_csv_update_operate_cost_completed +
                                    updated_instance.subtotal_processing_report_operate_cost_completed +
                                    updated_instance.subtotal_manual_unit_update_operate_cost_completed +
                                    updated_instance.subtotal_address_validation_unit_operate_cost_completed +
                                    updated_instance.subtotal_stripe_dispute_operate_cost_completed +
                                    updated_instance.subtotal_xml_file_operate_cost_completed
                            )

                            # QA Costs Calculation
                            updated_instance.subtotal_user_update_qa_cost_completed = (Decimal(updated_instance.num_updated_users or 0) * prices.user_update_qa_cost)
                            updated_instance.subtotal_property_update_qa_cost_completed = (Decimal(updated_instance.num_updated_properties or 0) * prices.property_update_qa_cost)
                            updated_instance.subtotal_bulk_update_qa_cost_completed = (Decimal(updated_instance.bulk_updates or 0) * prices.bulk_update_qa_cost)
                            updated_instance.subtotal_manual_property_update_qa_cost_completed = (Decimal(updated_instance.manual_updated_properties or 0) * prices.manual_property_update_qa_cost)
                            updated_instance.subtotal_csv_update_qa_cost_completed = (Decimal(updated_instance.update_by_csv_rows or 0) * prices.csv_update_qa_cost)
                            updated_instance.subtotal_processing_report_qa_cost_completed = (Decimal(updated_instance.processing_reports_rows or 0) * prices.processing_report_qa_cost)
                            updated_instance.subtotal_manual_unit_update_qa_cost_completed = (Decimal(updated_instance.manual_updated_units or 0) * prices.manual_unit_update_qa_cost)
                            updated_instance.subtotal_address_validation_unit_qa_cost_completed = (Decimal(updated_instance.av_number_of_units or 0) * prices.address_validation_unit_qa_cost)
                            updated_instance.subtotal_stripe_dispute_qa_cost_completed = (Decimal(stripe_total_disputes) * prices.stripe_dispute_qa_cost)
                            updated_instance.subtotal_xml_file_qa_cost_completed = (Decimal(xml_carrier_count) * prices.xml_file_qa_cost)

                            updated_instance.grand_total_qa_cost_completed = (
                                    updated_instance.subtotal_user_update_qa_cost_completed +
                                    updated_instance.subtotal_property_update_qa_cost_completed +
                                    updated_instance.subtotal_bulk_update_qa_cost_completed +
                                    updated_instance.subtotal_manual_property_update_qa_cost_completed +
                                    updated_instance.subtotal_csv_update_qa_cost_completed +
                                    updated_instance.subtotal_processing_report_qa_cost_completed +
                                    updated_instance.subtotal_manual_unit_update_qa_cost_completed +
                                    updated_instance.subtotal_address_validation_unit_qa_cost_completed +
                                    updated_instance.subtotal_stripe_dispute_qa_cost_completed +
                                    updated_instance.subtotal_xml_file_qa_cost_completed
                            )
                        else:
                            logger.warning(_("OperationPrice instance not found. Costs will not be calculated for request %(request_code)s.") % {'request_code': user_request.unique_code})
                    except Exception as e_cost:
                        logger.error(_("Error calculating costs for request %(request_code)s: %(error)s") % {'request_code': user_request.unique_code, 'error': e_cost}, exc_info=True)

                    fields_to_update_django = ['status', 'completed_at']

                    cost_fields_to_update = [
                        f.name for f in UserRecordsRequest._meta.get_fields()
                        if f.name.endswith('_client_price_completed') or
                           f.name.endswith('_operate_cost_completed') or
                           f.name.endswith('_qa_cost_completed')
                    ]

                    fields_to_update_django.extend(cost_fields_to_update)

                    if isinstance(form, GeneratingXmlOperateForm):
                        fields_to_update_django.extend(form.Meta.fields)
                    elif isinstance(form, OperateForm):
                        for field_name in form.cleaned_data:
                            if hasattr(updated_instance, field_name):
                                fields_to_update_django.append(field_name)

                    updated_instance.save(update_fields=list(set(fields_to_update_django)))
                django_save_successful = True
                logger.info(_("Request %(request_code)s marked as 'completed' in Django by %(user_email)s. Costs calculated and saved.") % {'request_code': user_request.unique_code, 'user_email': request.user.email})

            except Exception as e_django:
                logger.error(_("Error completing request %(pk)s in Django: %(error)s") % {'pk': pk, 'error': e_django}, exc_info=True)
                messages.error(request, _("An error occurred while completing the request in Django."))
                return redirect('tasks:request_detail', pk=pk)

            if django_save_successful:
                if user_request.type_of_process == 'address_validation' and user_request.salesforce_standard_opp_id:
                    logger.info(f"Attempting to update Salesforce Opportunity {user_request.salesforce_standard_opp_id} for completed AV request {user_request.unique_code}")
                    try:
                        sf = Salesforce(
                            username=settings.SF_USERNAME,
                            password=settings.SF_PASSWORD,
                            security_token=settings.SF_SECURITY_TOKEN,
                            consumer_key=settings.SF_CONSUMER_KEY,
                            consumer_secret=settings.SF_CONSUMER_SECRET,
                            domain=settings.SF_DOMAIN,
                            version=settings.SF_VERSION
                        )

                        assets_uploaded_date_sf = None
                        if user_request.assets_uploaded and user_request.completed_at:
                            assets_uploaded_date_sf = user_request.completed_at.date().isoformat()

                        sf_update_data = {
                            'Assets_Uploaded__c': user_request.assets_uploaded if user_request.assets_uploaded is not None else False,
                            'Number_of_Units__c': user_request.av_number_of_units if user_request.av_number_of_units is not None else 0,
                            'Number_of_Invalid_Units__c': user_request.av_number_of_invalid_units if user_request.av_number_of_invalid_units is not None else 0,
                            # SF espera un número
                            'Link_to_Assets__c': user_request.link_to_assets,
                            'Invisible_Success_Output_Link__c': user_request.success_output_link,
                            'Invisible_Failed_Output_Link__c': user_request.failed_output_link,
                            'Rhino_Accounts_Created__c': user_request.rhino_accounts_created if user_request.rhino_accounts_created is not None else False,
                            'Invisible_Comments__c': user_request.operating_notes,
                            # Ya es obligatorio para AV en el form
                            'Invisible_Status__c': 'Completed',  # Estado final en SF
                        }
                        # Solo añadir Assets_Uploaded_Date__c si tiene valor
                        if assets_uploaded_date_sf:
                            sf_update_data['Assets_Uploaded_Date__c'] = assets_uploaded_date_sf

                        logger.debug(f"Salesforce update payload for Opp {user_request.salesforce_standard_opp_id}: {sf_update_data}")
                        sf.Opportunity.update(user_request.salesforce_standard_opp_id, sf_update_data)
                        logger.info(f"Successfully updated Salesforce Opportunity {user_request.salesforce_standard_opp_id} upon request completion.")
                        messages.success(request,'Request marked as completed and Salesforce Opportunity updated successfully.')

                    except SalesforceError as e_sf:
                        logger.error(f"Salesforce API Error updating Opportunity {user_request.salesforce_standard_opp_id} for completed request {pk}: {str(e_sf)} - Content: {e_sf.content if hasattr(e_sf, 'content') else 'N/A'}",exc_info=True)
                        messages.warning(request,'Request completed in Django, but FAILED to update Salesforce. Please check Salesforce manually. Error: {error_type}').format(error_type=type(e_sf).__name__)
                    except Exception as e_conn_sf:
                        logger.error(f"Unexpected error connecting or updating Salesforce Opportunity {user_request.salesforce_standard_opp_id} for completed request {pk}: {e_conn_sf}",exc_info=True)
                        messages.warning(request,'Request completed in Django, but an UNEXPECTED error occurred trying to update Salesforce. Please check Salesforce manually.')
                else:
                    logger.info(f"Request {user_request.unique_code} (Type: {user_request.get_type_of_process_display()}) completed in Django. No Salesforce update attempted.")
                    messages.success(request, _('Request marked as completed successfully.'))
                return redirect('tasks:request_detail', pk=pk)
            return redirect('tasks:request_detail', pk=pk) #no se si deba ir
        else:  # form no es válido
            logger.warning(f"Form ({CurrentFormClass.__name__}) for request {pk} on complete is not valid: {form.errors.as_json(escape_html=True)}")
            error_list = []
            for field, errors in form.errors.items():
                error_list.append(f"{field}: {', '.join(errors)}")
            error_message_detail = "; ".join(error_list)
            messages.error(request, _('Please correct the errors: {details}').format(details=error_message_detail))
            return redirect('tasks:request_detail', pk=pk)  # Simplificado por ahora
    else:  # GET
        return redirect('tasks:request_detail', pk=pk)  # Simplificado

@login_required
def cancel_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user

    if not can_cancel_request(user, user_request):
        messages.error(request,_("You do not have permission to cancel this request or it's not in a cancellable state."))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        try:
            user_request.cancelled = True
            user_request.cancelled_by = request.user
            user_request.status = 'cancelled' # Usar constante
            user_request.cancelled_at = timezone.now()
            # Limpiar scheduled_date si se cancela una solicitud programada
            if user_request.scheduled_date:
                user_request.scheduled_date = None
            fields_to_update = ['status', 'cancelled', 'cancelled_by', 'cancelled_at']
            user_request.save(update_fields=fields_to_update)
            logger.info(f"User {user.email} cancelled request {pk}.")
            messages.success(request, _(f"Request cancelled by {user.email}."))
            return redirect('tasks:request_detail', pk=pk)
        except Exception as e:
            logger.error(f"Error cancelling request {pk}: {e}", exc_info=True)
            messages.error(request, _("An error occurred while cancelling the request."))
            return redirect('tasks:request_detail', pk=pk)
    else:
        # El GET no debería ser accesible si se usa el botón con confirm JS
        messages.error(request, _("Invalid request method for cancel."))
        return redirect('tasks:request_detail', pk=pk)

@login_required
def reject_request(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user # Definir user
    can_reject = False
    rejectable_statuses = ['qa_in_progress', 'completed'] # Mismos estados que en request_detail

    if user_request.status in rejectable_statuses:
        is_qa_agent_match = (is_agent(user) and user_request.qa_agent == user)
        is_requester_or_admin_leader = (user == user_request.requested_by or is_admin(user) or is_leadership(user))
        can_reject = (is_qa_agent_match or is_requester_or_admin_leader)

    if not can_reject:
        messages.error(request, _("You do not have permission to reject this request or it's not in a rejectable state."))
        return redirect('tasks:request_detail', pk=pk)

    # --- Resto de la lógica de la vista (sin cambios) ---
    if request.method == 'POST':
        form = RejectForm(request.POST)
        if form.is_valid():
            try:
                RejectedMessage.objects.create(
                    request=user_request,
                    rejected_by=request.user,
                    reason=form.cleaned_data['reason'],
                    is_resolved_qa=False,
                    rejected_at=timezone.now()
                )
                # Decide a qué estado volver (ej. 'in_progress' o 'pending')
                user_request.status = 'in_progress'
                # Limpiar campos de QA/Completado
                user_request.qa_agent = None
                user_request.qa_pending_at = None
                user_request.qa_in_progress_at = None
                user_request.completed_at = None
                user_request.is_rejected_previously = True
                fields_to_update = ['status', 'qa_agent', 'qa_pending_at',
                                    'qa_in_progress_at', 'completed_at',
                                    'is_rejected_previously']
                user_request.save(update_fields=fields_to_update)
                logger.info(f"Request {pk} rejected by {user.email}. Flag 'is_rejected_previously' set to True.")
                messages.warning(request, _('Request rejected and returned for correction.'))
                return redirect('tasks:request_detail', pk=pk)
            except Exception as e:
                logger.error(f"Error rejecting request {pk}: {e}", exc_info=True)
                messages.error(request, _("An error occurred while rejecting the request."))
                return render(request, 'tasks/reject_form.html', {'form': form, 'user_request': user_request})
        else:
            return render(request, 'tasks/reject_form.html', {'form': form, 'user_request': user_request})
    else: # GET
        form = RejectForm()
    return render(request, 'tasks/reject_form.html', {'form': form, 'user_request': user_request})

@login_required
@user_passes_test(is_leadership)
def approve_deactivation_toggle(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    if user_request.type_of_process != 'deactivation_toggle':
        messages.error(request, _("This action is only valid for Deactivation/Toggle requests."))
        return redirect('tasks:request_detail', pk=pk)
    if user_request.status != 'pending_approval':
        messages.error(request, _("This request is not pending approval."))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        try:
            approval_time = timezone.now()

            if user_request.scheduled_date:
                # Comprobar si la fecha programada ya pasó o es hoy (en UTC)
                today_utc = timezone.now().date()
                if user_request.scheduled_date <= today_utc:
                    # Ya pasó o es hoy, mover a 'pending' e iniciar TAT
                    user_request.status = 'pending'
                    user_request.effective_start_time_for_tat = approval_time
                    logger.info(f"Deactivation/Toggle Request {user_request.unique_code} approved (scheduled date {user_request.scheduled_date} is today/past). Moved to PENDING. TAT start: {approval_time}")
                else:
                    # Fecha programada es futura, mover a 'scheduled'
                    user_request.status = 'scheduled'
                    # effective_start_time_for_tat permanece None (o como estuviera), la tarea de Q lo establecerá
                    logger.info(f"Deactivation/Toggle Request {user_request.unique_code} approved. Moved to SCHEDULED for {user_request.scheduled_date}.")
            else:
                # No hay fecha programada, mover a 'pending' e iniciar TAT
                user_request.status = 'pending'
                user_request.effective_start_time_for_tat = approval_time
                logger.info(f"Deactivation/Toggle Request {user_request.unique_code} approved (no schedule date). Moved to PENDING. TAT start: {approval_time}")

                # Limpiar deactivation_toggle_leadership_approval si este campo se usaba para rastrear quién aprobó
                # Opcional: registrar quién aprobó en un campo de historial o en un log.
                # user_request.deactivation_toggle_leadership_approval = request.user.get_full_name() # Ejemplo

            user_request.save(update_fields=['status', 'effective_start_time_for_tat'])  # Añadir 'scheduled_date' si se modifica

            messages.success(request, _('Deactivation/Toggle Request approved. New status: {status}.').format(status=user_request.get_status_display()))
        except Exception as e:
            logger.error(f"Error approving request {pk}: {e}", exc_info=True)
            messages.error(request, _("An error occurred while approving the request."))

    else:
        messages.error(request, _("Invalid request method for approval."))
    return redirect('tasks:request_detail', pk=pk)


# --- Vista de Administración ---
@login_required
@user_passes_test(is_admin)
def manage_prices(request):
    price_instance, created = OperationPrice.objects.get_or_create(pk=1)
    if created: logger.info("Created initial OperationPrice instance.")
    if request.method == 'POST':
        form = OperationPriceForm(request.POST, instance=price_instance)
        if form.is_valid():
            try: form.save(); messages.success(request, _('Prices and costs updated successfully!')); return redirect('tasks:manage_prices')
            except Exception as e: logger.error(f"Error saving OperationPrice: {e}", exc_info=True); messages.error(request, _("An error occurred while saving the prices."))
        else: messages.error(request, _('Please correct the errors below.'))
    else: form = OperationPriceForm(instance=price_instance)
    return render(request, 'tasks/manage_prices.html', {'form': form})

@login_required
@user_passes_test(user_belongs_to_revenue_or_support)
def address_validation_request(request):
    user = request.user
    is_in_revenue = user_in_group(user, 'Revenue')
    is_in_support = user_in_group(user, 'Support')

    if is_in_revenue and is_in_support:
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:portal_dashboard')

    if request.method == 'POST':
        form = AddressValidationRequestForm(request.POST, request.FILES, user=user)
        uploaded_files = request.FILES.getlist('request_files')
        opportunity_id_from_form = form.data.get('address_validation_opportunity_id', '').strip()
        user_link_from_form = form.data.get('user_link', '').strip()

        if not uploaded_files and not user_link_from_form and not opportunity_id_from_form:
            messages.error(request, _('Please provide either file(s) to upload, a link, or an Opportunity ID.'))
            form.add_error(None, _('File(s), link, or Opportunity ID is required.'))

        if form.is_valid():
            logger.info("AddressValidationRequestForm is valid.")
            av_request = None
            try:
                creation_timestamp = timezone.now()
                av_request = form.save(commit=False)
                av_request.requested_by = user
                av_request.type_of_process = 'address_validation'
                av_request.timestamp = creation_timestamp
                # Importante: No intentar asignar user_file aquí

                schedule_request_flag = form.cleaned_data.get('schedule_request')
                scheduled_date_value = form.cleaned_data.get('scheduled_date')

                if schedule_request_flag and scheduled_date_value:
                    av_request.status = 'scheduled'
                    av_request.scheduled_date = scheduled_date_value
                    av_request.effective_start_time_for_tat = None
                    logger.info(
                        f"AddressValidationRequest by {user.email} will be scheduled for {scheduled_date_value}.")
                else:
                    av_request.status = 'pending'
                    av_request.scheduled_date = None
                    av_request.effective_start_time_for_tat = creation_timestamp
                    logger.info(f"AddressValidationRequest by {user.email} created with status 'pending'. TAT start: {creation_timestamp}")

                    # Asignación de equipo (similar a otros forms, ajustar si AV tiene reglas diferentes)
                if is_in_revenue:
                    av_request.team = TEAM_REVENUE
                elif is_in_support:
                    av_request.team = TEAM_SUPPORT
                else:
                    pass

                if not av_request.team:
                    messages.error(request,_('Failed to assign team. Ensure your user belongs to a valid operational team or a default is set.'))
                    return render(request, 'tasks/address_validation_request.html', {'form': form})

                with transaction.atomic():  # Usar transacción para guardar el request y sus archivos
                    av_request.save()
                    logger.info(f"Saved UserRecordsRequest (Address Validation) PK: {av_request.pk} code: {av_request.unique_code} Team: {av_request.team}")

                    # Guardar los múltiples archivos si se subieron
                    # Esta lógica ya la tenías, la integramos aquí:
                    if uploaded_files:
                        logger.info(f"Processing {len(uploaded_files)} uploaded file(s) for request {av_request.unique_code}.")
                        for file_to_upload in uploaded_files:
                            AddressValidationFile.objects.create(request=av_request, uploaded_file=file_to_upload)
                        logger.info(f"Finished saving {len(uploaded_files)} associated files for {av_request.unique_code}.")
                    else:
                        logger.info(f"No 'request_files' uploaded for {av_request.unique_code}.")

                # Mensaje de éxito
                if av_request.status == 'scheduled':
                    messages.success(request,_('Address Validation Request ({code}) has been scheduled for {date} for {team} team!').format(
                        code=av_request.unique_code,
                        date=av_request.scheduled_date.strftime('%Y-%m-%d'),
                        team=av_request.get_team_display() or "Unassigned"))
                else:
                    messages.success(request,_('Address Validation Request ({code}) created successfully for {team} team!').format(
                        code=av_request.unique_code,
                        team=av_request.get_team_display() or "Unassigned"))
                return redirect('tasks:portal_dashboard')
            except Exception as e:
                logger.error(f"Error saving AddressValidationRequest or files (PK might be {av_request.pk if av_request and hasattr(av_request, 'pk') else 'N/A'}): {e}",exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request or processing files."))
        else:  # form.is_valid() es False
            logger.warning(f"AddressValidationRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            # El mensaje de error ya lo añade el form.clean o la validación de campo
            # Solo re-renderizamos.
    else:  # GET request
        form = AddressValidationRequestForm(user=user)

    return render(request, 'tasks/address_validation_request.html', {'form': form})

@login_required
@user_passes_test(user_belongs_to_accounting)
def stripe_disputes_request(request):
    """Vista para crear una solicitud de Stripe Disputes."""
    if request.method == 'POST':
        form = StripeDisputesRequestForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()
                dispute_request = form.save(commit=False)
                dispute_request.requested_by = request.user
                dispute_request.type_of_process = 'stripe_disputes'
                dispute_request.timestamp = creation_timestamp
                dispute_request.status = 'pending'
                dispute_request.priority = PRIORITY_NORMAL
                dispute_request.team = TEAM_ACCOUNTING
                dispute_request.scheduled_date = None
                dispute_request.effective_start_time_for_tat = creation_timestamp

                dispute_request.save()
                logger.info(f"Stripe Disputes Request ({dispute_request.unique_code}) created by {request.user.email} with priority '{dispute_request.priority}' for team '{dispute_request.team}'. TAT start: {creation_timestamp}")
                messages.success(request, _('Stripe Disputes Request ({code}) created successfully!').format(code=dispute_request.unique_code))
                return redirect('tasks:portal_dashboard')
            except Exception as e:
                logger.error(f"Error saving StripeDisputesRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
        else:
            logger.warning(f"StripeDisputesRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            messages.error(request, _('Please correct the errors below.'))
    else: # GET request
        form = StripeDisputesRequestForm()
    return render(request, 'tasks/stripe_disputes_request.html', {'form': form})

@login_required
@user_passes_test(user_belongs_to_revenue_or_support) # Permiso
def property_records_request(request):
    user = request.user
    is_in_revenue = user_in_group(user, TEAM_REVENUE)
    is_in_support = user_in_group(user, TEAM_SUPPORT)

    if is_in_revenue and is_in_support:
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:portal_dashboard')

    if request.method == 'POST':
        # Pasar user y FILES al form
        form = PropertyRecordsRequestForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()
                prop_request = form.save(commit=False)
                prop_request.requested_by = user
                prop_request.type_of_process = 'property_records'
                prop_request.timestamp = creation_timestamp

                schedule_request_flag = form.cleaned_data.get('schedule_request')
                scheduled_date_value = form.cleaned_data.get('scheduled_date')

                if schedule_request_flag and scheduled_date_value:
                    prop_request.status = 'scheduled'
                    prop_request.scheduled_date = scheduled_date_value
                    prop_request.effective_start_time_for_tat = None
                    logger.info(f"PropertyRecordsRequest by {user.email} will be scheduled for {scheduled_date_value}.")
                else:
                    prop_request.status = 'pending'
                    prop_request.scheduled_date = None
                    prop_request.effective_start_time_for_tat = creation_timestamp
                    logger.info(f"PropertyRecordsRequest by {user.email} created with status 'pending'. TAT start: {creation_timestamp}")

                # --- ASIGNAR EQUIPO ---
                if is_in_revenue:
                    prop_request.team = TEAM_REVENUE
                elif is_in_support:
                    prop_request.team = TEAM_SUPPORT
                else:
                    pass

                if not prop_request.team:  # Fallback si es mandatorio y no se pudo asignar
                    messages.error(request,_('Failed to assign team. Ensure your user belongs to a valid operational team or a default is set for this request type.'))
                    return render(request, 'tasks/property_records_request.html', {'form': form})

                prop_request.save() # Guardar instancia
                form.save_m2m()

                if prop_request.status == 'scheduled':
                    messages.success(request,_('Property Records Request ({code}) has been scheduled for {date} for {team} team!').format(
                        code=prop_request.unique_code,
                        date=prop_request.scheduled_date.strftime('%Y-%m-%d'),
                        team=prop_request.get_team_display() or "Unassigned"))
                else:
                    messages.success(request,_('Property Records Request ({code}) created successfully for {team} team!').format(
                        code=prop_request.unique_code,
                        team=prop_request.get_team_display() or "Unassigned"))
                return redirect('tasks:portal_dashboard')
            except Exception as e:
                logger.error(f"Error saving PropertyRecordsRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
        else:  # form.is_valid() es False
            logger.warning(f"PropertyRecordsRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            messages.error(request, _('Please correct the errors below.'))
    else:  # GET request
        form = PropertyRecordsRequestForm(user=user)

    return render(request, 'tasks/property_records_request.html', {'form': form})


@login_required
def set_update_needed_flag(request, pk):
    """Activa la bandera 'update_needed_flag'."""
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user

    # Permiso: Miembro del equipo O Admin O Leadership
    is_permitted = (
        (user_request.team and user_in_group(user, user_request.team)) or
        is_admin(user) or
        is_leadership(user)
    )

    # No permitir si ya está completado o cancelado, o si la bandera ya está activa
    if user_request.status in ['completed','cancelled', 'scheduled'] or user_request.update_needed_flag:
        is_permitted = False

    if not is_permitted:
        messages.error(request, _("You do not have permission to request an update at this time."))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        try:
            user_request.update_needed_flag = True
            user_request.update_requested_by = request.user
            user_request.update_requested_at = timezone.now()
            user_request.save(update_fields=['update_needed_flag', 'update_requested_by', 'update_requested_at'])
            logger.info(f"User {user.email} set update_needed_flag=True for request {pk}.")
            messages.success(request, _(f"Update requested. The assigned agent will be notified (via the visible flag)."))
        except Exception as e:
            logger.error(f"Error setting update_needed_flag=True for request {pk}: {e}", exc_info=True)
            messages.error(request, _("An error occurred while requesting the update."))
    else:
        messages.warning(request, _("Please use the button to request an update."))

    return redirect('tasks:request_detail', pk=pk)


@login_required
def clear_update_needed_flag(request, pk):
    """Desactiva la bandera 'update_needed_flag'."""
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user

    # Permiso: Solo Agentes
    is_permitted = is_agent(user)

    # Solo permitir si la bandera está activa
    if not user_request.update_needed_flag or user_request.status == 'scheduled':  # <--- No limpiar si está programada
        is_permitted = False

    if not is_permitted:
        messages.error(request, _("You do not have permission to mark this update as provided, or it's not needed."))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        try:
            user_request.update_needed_flag = False
            user_request.save(update_fields=['update_needed_flag'])
            logger.info(f"User {user.email} set update_needed_flag=False for request {pk}.")
            messages.success(request, _("Update flag cleared."))
        except Exception as e:
            logger.error(f"Error setting update_needed_flag=False for request {pk}: {e}", exc_info=True)
            messages.error(request, _("An error occurred while clearing the update flag."))
    else:
        messages.warning(request, _("Please use the button to mark the update as provided."))

    return redirect('tasks:request_detail', pk=pk)

@login_required
def uncancel_request(request, pk):
    """Cambia el estado de 'Cancelled' a 'Pending'."""
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user

    # --- Verificación de Permiso y Estado ---
    can_uncancel = False
    if user_request.status == 'cancelled': # Solo si está cancelado
        # Permiso: Miembro del equipo O Admin O Leadership
        is_permitted = (
            (user_request.team and user_in_group(user, user_request.team)) or
            is_admin(user) or
            is_leadership(user)
        )
        if is_permitted:
            can_uncancel = True

    if not can_uncancel:
        messages.error(request, _("You do not have permission to uncancel this request or it's not in a cancellable state."))
        return redirect('tasks:request_detail', pk=pk)
    # --- Fin Verificación ---

    if request.method == 'POST':
        try:
            user_request.cancelled = False
            user_request.cancelled_by = None
            user_request.cancelled_at = None
            user_request.uncanceled_by = request.user
            user_request.uncanceled_at = timezone.now()
            user_request.status = 'pending'
            user_request.cancelled_at = None
            user_request.cancel_reason = None
            fields_to_update = ['cancelled', 'cancelled_by', 'cancelled_at', 'uncanceled_by', 'uncanceled_at', 'status']
            user_request.save(update_fields=fields_to_update)
            logger.info(f"User {user.email} uncancelled request {pk}. Status set to {'pending'}.")
            messages.success(request, _(f"Request has been uncancelled by {user.email} and returned to Pending status."))
        except Exception as e:
            logger.error(f"Error uncancelling request {pk}: {e}", exc_info=True)
            messages.error(request, _("An error occurred while uncancelling the request."))
    else:
        messages.warning(request, _("Please use the button to uncancel the request."))

    return redirect('tasks:request_detail', pk=pk)

@login_required
@user_passes_test(user_is_admin_or_leader)
def client_cost_summary_view(request):
    today = timezone.localdate()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request,"Invalid start date format. Using default.")
            start_date = today.replace(day=1)
    else:
        start_date = today.replace(day=1)

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request,"Invalid end date format. Using default.")
            _, last_day_of_month = calendar.monthrange(today.year, today.month)
            end_date = today.replace(day=last_day_of_month)
    else:
        _, last_day_of_month = calendar.monthrange(today.year, today.month)
        end_date = today.replace(day=last_day_of_month)

    start_datetime_utc = timezone.make_aware(datetime.combine(start_date, time.min), pytz.utc)
    end_datetime_utc = timezone.make_aware(datetime.combine(end_date, time.max), pytz.utc)

    completed_requests_in_period = UserRecordsRequest.objects.filter(
        status='completed',
        completed_at__gte=start_datetime_utc,
        completed_at__lte=end_datetime_utc
    ).select_related('requested_by')

    grand_total_dict = completed_requests_in_period.aggregate(
        total=Coalesce(Sum('grand_total_client_price_completed'), Value(Decimal('0.00'), output_field=DecimalField()))
    )
    grand_total_cost = grand_total_dict['total']

    team_summary_from_db = completed_requests_in_period.values('team').annotate(
        subtotal=Coalesce(Sum('grand_total_client_price_completed'),
                          Value(Decimal('0.00'), output_field=DecimalField()))
    )
    team_subtotals_map = {item['team']: item['subtotal'] for item in team_summary_from_db}
    team_subtotals_list_ordered = []
    team_chart_labels = []
    team_chart_data = []
    for team_key, team_display_name in TEAM_CHOICES:
        subtotal = team_subtotals_map.get(team_key, Decimal('0.00'))
        team_subtotals_list_ordered.append({'name': team_display_name, 'subtotal': subtotal})
        if subtotal > 0:
            team_chart_labels.append(team_display_name)
            team_chart_data.append(float(subtotal))

    process_summary_from_db = completed_requests_in_period.values('type_of_process').annotate(
        subtotal=Coalesce(Sum('grand_total_client_price_completed'),
                          Value(Decimal('0.00'), output_field=DecimalField()))
    )
    process_subtotals_map = {item['type_of_process']: item['subtotal'] for item in process_summary_from_db}
    process_subtotals_list_ordered = []
    process_chart_labels = []
    process_chart_data = []
    for process_key, process_display_name in TYPE_CHOICES:
        subtotal = process_subtotals_map.get(process_key, Decimal('0.00'))
        process_subtotals_list_ordered.append({'name': process_display_name, 'subtotal': subtotal})
        if subtotal > 0:
            process_chart_labels.append(process_display_name)
            process_chart_data.append(float(subtotal))

    target_processes_for_scatter = [
        'address_validation', 'user_records', 'property_records',
        'unit_transfer', 'deactivation_toggle'
    ]
    target_teams_for_scatter = [TEAM_REVENUE, TEAM_SUPPORT]

    scatter_charts_data = {}
    type_choices_dict_scatter = dict(TYPE_CHOICES)

    for process_key in target_processes_for_scatter:
        process_name_display = type_choices_dict_scatter.get(process_key, process_key.replace("_", " ").title())
        process_specific_requests = completed_requests_in_period.filter(type_of_process=process_key)
        current_process_datasets = []

        for team_key in target_teams_for_scatter:
            team_name_display = dict(TEAM_CHOICES).get(team_key, team_key)
            team_specific_requests = process_specific_requests.filter(team=team_key).order_by('completed_at')

            data_points = []
            for req in team_specific_requests:
                if req.completed_at and req.grand_total_client_price_completed is not None:
                    data_points.append({
                        'x': req.completed_at.isoformat(),
                        'y': float(req.grand_total_client_price_completed),
                        'pk': req.pk  # <--- AÑADIR PK DE LA SOLICITUD
                    })

            if data_points:
                border_color = 'rgba(255, 99, 132, 1)' if team_key == TEAM_REVENUE else 'rgba(54, 162, 235, 1)'
                bg_color = 'rgba(255, 99, 132, 0.2)' if team_key == TEAM_REVENUE else 'rgba(54, 162, 235, 0.2)'
                current_process_datasets.append({
                    'label': team_name_display,
                    'data': data_points,
                    'borderColor': border_color,
                    'backgroundColor': bg_color,
                    'tension': 0.3,
                    'fill': False,
                    'pointRadius': 3,
                    'pointBackgroundColor': border_color
                })

        if current_process_datasets:
            scatter_charts_data[process_key] = {
                'chart_title': f'Cost Trend for {process_name_display}',
                'datasets': current_process_datasets
            }

    try:
        request_detail_url_template = reverse('tasks:request_detail', args=[0]).replace('/0/', '/REPLACE_PK/')
    except Exception as e:
        logger.error(f"Could not generate URL template for request_detail: {e}")
        request_detail_url_template = "/rhino/request/REPLACE_PK/"  # Fallback manual
        messages.error(request,"Error generating URL template for chart links.")

    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'grand_total_cost': grand_total_cost,
        'team_subtotals': team_subtotals_list_ordered,
        'process_subtotals': process_subtotals_list_ordered,
        'team_chart_labels': team_chart_labels,
        'team_chart_data': team_chart_data,
        'process_chart_labels': process_chart_labels,
        'process_chart_data': process_chart_data,
        'scatter_charts_data': scatter_charts_data,
        'request_detail_url_template': request_detail_url_template,
        'page_title': 'Cost Summary Report'
    }
    return render(request, 'tasks/cost_summary.html', context)