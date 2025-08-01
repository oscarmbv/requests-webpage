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
from django.db.models import Q, Sum, Value, CharField, DecimalField, Count, Avg, ExpressionWrapper, F, fields
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import formset_factory
from django.http import HttpResponse
import csv
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
from django.db.models.functions import Coalesce, Cast
import json
import os
from django_q.tasks import async_task
from .forms import ProvideUpdateForm
from django.utils.html import strip_tags
from .notifications import ( notify_request_blocked, notify_update_provided, notify_update_requested,
                             notify_request_approved, notify_new_request_created, notify_pending_approval_request,
                             notify_request_sent_to_qa, notify_request_rejected, notify_request_cancelled,
                             notify_request_uncancelled, notify_request_completed)

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
@user_passes_test(user_belongs_to_revenue_or_support)
def user_records_request(request):
    UserGroupFormSet = formset_factory(UserGroupForm, extra=1, min_num=1, can_delete=False)
    user = request.user

    if user_in_group(user, TEAM_REVENUE) and user_in_group(user, TEAM_SUPPORT):
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:rhino_dashboard')

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
                                 'deactivate_user': form.cleaned_data.get('deactivate_user', False),
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

                on_behalf_of_user = user_records_form.cleaned_data.get('submit_on_behalf_of')
                effective_requester = user

                if user.is_staff and on_behalf_of_user:
                    effective_requester = on_behalf_of_user
                    logger.info(f"Admin '{user.email}' está creando un request en nombre de '{on_behalf_of_user.email}'.")

                req_instance = UserRecordsRequest(
                    requested_by=effective_requester,
                    partner_name=user_records_form.cleaned_data['partner_name'],
                    priority=user_records_form.cleaned_data['priority'],
                    special_instructions=user_records_form.cleaned_data['special_instructions'],
                    user_file=user_file,
                    user_link=user_link,
                    user_groups_data=group_data if group_data else None,
                    deactivate_user=user_records_form.cleaned_data.get('deactivate_user', False),
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

                is_in_revenue = user_in_group(effective_requester, TEAM_REVENUE)
                is_in_support = user_in_group(effective_requester, TEAM_SUPPORT)

                # --- ASIGNAR EQUIPO ---
                if is_in_revenue:
                    req_instance.team = TEAM_REVENUE
                elif is_in_support:
                    req_instance.team = TEAM_SUPPORT
                else:
                    pass

                req_instance.save()

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_new_request_created',
                        req_instance.pk,  # Pasa el PK de la instancia guardada
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyNewRequest-{req_instance.unique_code}",
                        # Nombre opcional para la tarea en Django Q
                        hook='tasks.hooks.print_task_result'
                        # Opcional: una función para loguear el resultado de la tarea
                    )
                    logger.info(f"Tarea de notificación para nueva solicitud {req_instance.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea de notificación para {req_instance.unique_code}: {e_async}",
                        exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
                return redirect('tasks:rhino_dashboard')
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

    if user_in_group(user, TEAM_REVENUE) and user_in_group(user, TEAM_SUPPORT):
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:rhino_dashboard')

    if request.method == 'POST':
         # Pasar user al form
        form = DeactivationToggleRequestForm(request.POST, user=user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()

                on_behalf_of_user = form.cleaned_data.get('submit_on_behalf_of')
                effective_requester = user

                if user.is_staff and on_behalf_of_user:
                    effective_requester = on_behalf_of_user
                    logger.info(f"Admin '{user.email}' está creando un request en nombre de '{on_behalf_of_user.email}'.")

                deact_toggle_request = form.save(commit=False)
                deact_toggle_request.requested_by = effective_requester
                deact_toggle_request.type_of_process = 'deactivation_toggle'
                deact_toggle_request.timestamp = creation_timestamp

                is_in_revenue = user_in_group(effective_requester, TEAM_REVENUE)
                is_in_support = user_in_group(effective_requester, TEAM_SUPPORT)
                is_leader = user_in_group(effective_requester, TEAM_LEADERSHIPS)

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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme

                    if deact_toggle_request.status == 'pending_approval':

                        async_task(
                            'tasks.notifications.notify_new_request_created',
                            deact_toggle_request.pk,
                            http_request_host=current_host,
                            http_request_scheme=current_scheme,
                            task_name=f"NotifyNewRequest-{deact_toggle_request.unique_code}"
                        )
                        logger.info(
                            f"Tarea de notificación 'New Request' para {deact_toggle_request.unique_code} encolada.")

                        async_task(
                            'tasks.notifications.notify_pending_approval_request',
                            deact_toggle_request.pk,
                            http_request_host=current_host,
                            http_request_scheme=current_scheme,
                            task_name=f"NotifyPendingApproval-{deact_toggle_request.unique_code}"
                        )
                        logger.info(
                            f"Tarea de notificación 'Pending Approval' para {deact_toggle_request.unique_code} tambien encolada.")

                    else:
                        async_task(
                            'tasks.notifications.notify_new_request_created',
                            deact_toggle_request.pk,
                            http_request_host=current_host,
                            http_request_scheme=current_scheme,
                            task_name=f"NotifyNewRequest-{deact_toggle_request.unique_code}"
                        )
                        logger.info(
                            f"Tarea de notificación 'New Request' para {deact_toggle_request.unique_code} encolada.")

                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea de notificación para {deact_toggle_request.unique_code}: {e_async}",
                        exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
                return redirect('tasks:rhino_dashboard')
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

    if user_in_group(user, TEAM_REVENUE) and user_in_group(user, TEAM_SUPPORT):
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:rhino_dashboard')

    if request.method == 'POST':
        # Pasar user y FILES
        form = UnitTransferRequestForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()

                on_behalf_of_user = form.cleaned_data.get('submit_on_behalf_of')
                effective_requester = user

                if user.is_staff and on_behalf_of_user:
                    effective_requester = on_behalf_of_user
                    logger.info(f"Admin '{user.email}' está creando un request en nombre de '{on_behalf_of_user.email}'.")

                unit_transfer_request = form.save(commit=False)
                unit_transfer_request.requested_by = effective_requester
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
                is_in_revenue = user_in_group(effective_requester, TEAM_REVENUE)
                is_in_support = user_in_group(effective_requester, TEAM_SUPPORT)

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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_new_request_created',
                        unit_transfer_request.pk,
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyNewRequest-{unit_transfer_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(
                        f"Tarea de notificación para nueva solicitud {unit_transfer_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea de notificación para {unit_transfer_request.unique_code}: {e_async}", exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

                if unit_transfer_request.status == 'scheduled':
                    messages.success(request,_('Unit Transfer Request ({code}) has been scheduled for {date} for {team} team!').format(
                        code=unit_transfer_request.unique_code,
                        date=unit_transfer_request.scheduled_date.strftime('%Y-%m-%d'),
                        team=unit_transfer_request.get_team_display() or "Unassigned"))
                else:
                    messages.success(request,_('Unit Transfer Request ({code}) created successfully for {team} team!').format(
                                     code=unit_transfer_request.unique_code,
                                     team=unit_transfer_request.get_team_display() or "Unassigned"))
                return redirect('tasks:rhino_dashboard')
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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_new_request_created',
                        xml_request.pk,
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyNewRequest-{xml_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(f"Tarea de notificación para nueva solicitud XML {xml_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea de notificación para XML {xml_request.unique_code}: {e_async}",
                        exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

                logger.info(f"Generating XML Request ({xml_request.unique_code}) created by {request.user.email} with priority '{xml_request.priority}' for team '{xml_request.team}'. TAT start: {creation_timestamp}")
                messages.success(request, _('Generating XML files Request ({code}) created successfully!').format(code=xml_request.unique_code))
                return redirect('tasks:rhino_dashboard')
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
        return redirect('tasks:rhino_dashboard')

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

    can_unassign = False

    if user_request.status == 'in_progress' and (user == user_request.operator or is_admin_user):
        can_unassign = True
    elif user_request.status == 'qa_in_progress' and (user == user_request.qa_agent or is_admin_user):
        can_unassign = True


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

    # Estados activos (no finalizados) donde se puede pedir/proveer update
    active_statuses = [st[0] for st in STATUS_CHOICES if st[0] not in ['completed', 'cancelled']]

    can_provide_update = False

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
        can_provide_update = False

        if user_request.status == 'in_progress' and (user == user_request.operator or is_admin_user):
            can_provide_update = True

        elif user_request.status == 'qa_in_progress' and (user == user_request.qa_agent or is_admin_user):
            can_provide_update = True

        elif user_request.status == 'pending' and user_request.team and (
                user_in_group(user, user_request.team) or is_admin_user):
            can_provide_update = True

        elif user_request.status == 'qa_pending' and (is_agent(user) or is_admin_user):
            can_provide_update = True

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

    block_form = BlockForm()
    operate_form = OperateForm(instance=user_request)
    generating_xml_form = GeneratingXmlOperateForm(instance=user_request)

    # Construir el contexto
    context = {
        'user_request': user_request,
        'is_agent_user': is_agent_user,
        'block_form': block_form,
        'operate_form': operate_form,
        'generating_xml_form': generating_xml_form,
        'tinymce_js_url': settings.TINYMCE_JS_URL,
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
        'can_provide_update': can_provide_update,
        'update_needed': user_request.update_needed_flag,
        'can_cancel_request': can_cancel_request,
        'can_uncancel_request': can_uncancel_request,
        'can_unassign': can_unassign,
    }

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
            plain_text_reason = strip_tags(block_reason).replace('&nbsp;', ' ').strip()
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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_request_blocked',
                        user_request.pk,  # PK de la solicitud
                        request.user.pk,  # PK del usuario que bloqueó
                        block_reason,  # El motivo del bloqueo
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyRequestBlocked-{user_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(f"Tarea de notificación 'Request Blocked' para {user_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea 'Request Blocked' para {user_request.unique_code}: {e_async}",
                        exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
                            'Invisible_Comments__c': f"Request {user_request.unique_code} blocked by {request.user.email}. Reason: {plain_text_reason}"
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
                logger.info(f"Request {user_request.unique_code} resolved in Portal by {request.user.email}. TAT reset.")

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_request_resolved',
                        user_request.pk,  # PK de la solicitud
                        request.user.pk,  # PK del usuario que resolvió
                        resolve_message_text,  # El mensaje de resolución
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyRequestResolved-{user_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(f"Tarea de notificación 'Request Resolved' para {user_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea 'Request Resolved' para {user_request.unique_code}: {e_async}",
                        exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_request_sent_to_qa',
                        saved_instance.pk,  # PK de la solicitud
                        request.user.pk,  # PK del operador que envía a QA
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifySentToQA-{saved_instance.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(f"Tarea de notificación 'Sent to QA' para {saved_instance.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea 'Sent to QA' para {saved_instance.unique_code}: {e_async}", exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
            updated_instance = None
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
                            total_av_units = (updated_instance.av_number_of_units or 0) + (updated_instance.av_number_of_invalid_units or 0)
                            updated_instance.subtotal_address_validation_unit_client_price_completed = (Decimal(total_av_units) * prices.address_validation_unit_price)
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
                            updated_instance.subtotal_address_validation_unit_operate_cost_completed = (Decimal(total_av_units) * prices.address_validation_unit_operate_cost)
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
                            updated_instance.subtotal_address_validation_unit_qa_cost_completed = (Decimal(total_av_units) * prices.address_validation_unit_qa_cost)
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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_request_completed',
                        updated_instance.pk,  # PK de la solicitud completada
                        request.user.pk,  # PK del agente de QA que completó
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyRequestCompleted-{updated_instance.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(
                        f"Tarea de notificación 'Request Completed' para {updated_instance.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea 'Request Completed' para {updated_instance.unique_code}: {e_async}",
                        exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
                            'Invisible_Comments__c': strip_tags(user_request.operating_notes).replace('&nbsp;', ' ').strip(),
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

            # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
            try:
                current_host = request.get_host()
                current_scheme = request.scheme
                async_task(
                    'tasks.notifications.notify_request_cancelled',
                    user_request.pk,  # PK de la solicitud
                    user.pk,  # PK del usuario que canceló
                    http_request_host=current_host,
                    http_request_scheme=current_scheme,
                    task_name=f"NotifyRequestCancelled-{user_request.unique_code}",
                    hook='tasks.hooks.print_task_result'
                )
                logger.info(f"Tarea de notificación 'Request Cancelled' para {user_request.unique_code} encolada.")
            except Exception as e_async:
                logger.error(f"Error al encolar la tarea 'Request Cancelled' para {user_request.unique_code}: {e_async}", exc_info=True)
            # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
            rejection_reason = form.cleaned_data['reason']
            try:
                RejectedMessage.objects.create(
                    request=user_request,
                    rejected_by=request.user,
                    reason=rejection_reason,
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

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_request_rejected',
                        user_request.pk,  # PK de la solicitud
                        user.pk,  # PK del usuario que rechazó
                        rejection_reason,  # El motivo del rechazo
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyRequestRejected-{user_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(f"Tarea de notificación 'Request Rejected' para {user_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea 'Request Rejected' para {user_request.unique_code}: {e_async}", exc_info=True)

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

            user_request.save(update_fields=['status', 'effective_start_time_for_tat'])

            # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
            try:
                current_host = request.get_host()
                current_scheme = request.scheme
                async_task(
                    'tasks.notifications.notify_request_approved',
                    user_request.pk,
                    request.user.pk,
                    http_request_host=current_host,
                    http_request_scheme=current_scheme,
                    task_name=f"NotifyRequestApproved-{user_request.unique_code}",
                    hook='tasks.hooks.print_task_result'
                )
                logger.info(f"Tarea de notificación 'Request Approved' para {user_request.unique_code} encolada.")
            except Exception as e_async:
                logger.error(
                    f"Error al encolar la tarea de notificación 'Request Approved' para {user_request.unique_code}: {e_async}",
                    exc_info=True)
            # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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

    if user_in_group(user, TEAM_REVENUE) and user_in_group(user, TEAM_SUPPORT):
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:rhino_dashboard')

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

                on_behalf_of_user = form.cleaned_data.get('submit_on_behalf_of')
                effective_requester = user

                if user.is_staff and on_behalf_of_user:
                    effective_requester = on_behalf_of_user
                    logger.info(f"Admin '{user.email}' está creando un request en nombre de '{on_behalf_of_user.email}'.")

                av_request = form.save(commit=False)
                av_request.requested_by = effective_requester
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
                is_in_revenue = user_in_group(effective_requester, TEAM_REVENUE)
                is_in_support = user_in_group(effective_requester, TEAM_SUPPORT)
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

                    # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                    try:
                        current_host = request.get_host()
                        current_scheme = request.scheme
                        async_task(
                            'tasks.notifications.notify_new_request_created',
                            av_request.pk,
                            http_request_host=current_host,
                            http_request_scheme=current_scheme,
                            task_name=f"NotifyNewRequest-{av_request.unique_code}",
                            hook='tasks.hooks.print_task_result'
                        )
                        logger.info(
                            f"Tarea de notificación para nueva solicitud {av_request.unique_code} encolada.")
                    except Exception as e_async:
                        logger.error(
                            f"Error al encolar la tarea de notificación para {av_request.unique_code}: {e_async}", exc_info=True)

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
                return redirect('tasks:rhino_dashboard')
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
        form = StripeDisputesRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()
                dispute_request = form.save(commit=False)

                on_behalf_of_user = form.cleaned_data.get('submit_on_behalf_of')
                effective_requester = request.user

                if request.user.is_staff and on_behalf_of_user:
                    effective_requester = on_behalf_of_user
                    logger.info(f"Admin '{request.user.email}' está creando un request en nombre de '{on_behalf_of_user.email}'.")

                dispute_request.requested_by = effective_requester
                dispute_request.type_of_process = 'stripe_disputes'
                dispute_request.timestamp = creation_timestamp
                dispute_request.status = 'pending'
                dispute_request.priority = PRIORITY_NORMAL
                dispute_request.team = TEAM_ACCOUNTING
                dispute_request.scheduled_date = None
                dispute_request.effective_start_time_for_tat = creation_timestamp

                dispute_request.save()

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_new_request_created',
                        dispute_request.pk,
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyNewRequest-{dispute_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(
                        f"Tarea de notificación para nueva solicitud {dispute_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea de notificación para {dispute_request.unique_code}: {e_async}", exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

                logger.info(f"Stripe Disputes Request ({dispute_request.unique_code}) created by {request.user.email} with priority '{dispute_request.priority}' for team '{dispute_request.team}'. TAT start: {creation_timestamp}")
                messages.success(request, _('Stripe Disputes Request ({code}) created successfully!').format(code=dispute_request.unique_code))
                return redirect('tasks:rhino_dashboard')
            except Exception as e:
                logger.error(f"Error saving StripeDisputesRequest: {e}", exc_info=True)
                messages.error(request, _("An unexpected error occurred while saving the request."))
        else:
            logger.warning(f"StripeDisputesRequestForm is NOT valid. Errors: {form.errors.as_json()}")
            messages.error(request, _('Please correct the errors below.'))
    else: # GET request
        form = StripeDisputesRequestForm(user=request.user)
    return render(request, 'tasks/stripe_disputes_request.html', {'form': form})

@login_required
@user_passes_test(user_belongs_to_revenue_or_support) # Permiso
def property_records_request(request):
    user = request.user

    if user_in_group(user, TEAM_REVENUE) and user_in_group(user, TEAM_SUPPORT):
        messages.error(request, _("You have to be in only one of the groups Revenue or Support to create a request."))
        return redirect('tasks:rhino_dashboard')

    if request.method == 'POST':
        # Pasar user y FILES al form
        form = PropertyRecordsRequestForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            try:
                creation_timestamp = timezone.now()

                on_behalf_of_user = form.cleaned_data.get('submit_on_behalf_of')
                effective_requester = user

                if user.is_staff and on_behalf_of_user:
                    effective_requester = on_behalf_of_user
                    logger.info(f"Admin '{user.email}' está creando un request en nombre de '{on_behalf_of_user.email}'.")

                prop_request = form.save(commit=False)
                prop_request.requested_by = effective_requester
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
                is_in_revenue = user_in_group(effective_requester, TEAM_REVENUE)
                is_in_support = user_in_group(effective_requester, TEAM_SUPPORT)

                if is_in_revenue:
                    prop_request.team = TEAM_REVENUE
                elif is_in_support:
                    prop_request.team = TEAM_SUPPORT
                else:
                    pass

                if not prop_request.team:  # Fallback si es mandatorio y no se pudo asignar
                    messages.error(request,_('Failed to assign team. Ensure your user belongs to a valid operational team or a default is set for this request type.'))
                    return render(request, 'tasks/property_records_request.html', {'form': form})

                prop_request.save()
                form.save_m2m()

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_new_request_created',
                        prop_request.pk,
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyNewRequest-{prop_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(
                        f"Tarea de notificación para nueva solicitud {prop_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea de notificación para {prop_request.unique_code}: {e_async}", exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

                if prop_request.status == 'scheduled':
                    messages.success(request,_('Property Records Request ({code}) has been scheduled for {date} for {team} team!').format(
                        code=prop_request.unique_code,
                        date=prop_request.scheduled_date.strftime('%Y-%m-%d'),
                        team=prop_request.get_team_display() or "Unassigned"))
                else:
                    messages.success(request,_('Property Records Request ({code}) created successfully for {team} team!').format(
                        code=prop_request.unique_code,
                        team=prop_request.get_team_display() or "Unassigned"))
                return redirect('tasks:rhino_dashboard')
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

            # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
            try:
                current_host = request.get_host()
                current_scheme = request.scheme
                async_task(
                    'tasks.notifications.notify_update_requested',
                    user_request.pk,  # PK de la solicitud
                    user.pk,  # PK del usuario que solicitó la actualización
                    http_request_host=current_host,
                    http_request_scheme=current_scheme,
                    task_name=f"NotifyUpdateRequested-{user_request.unique_code}",
                    hook='tasks.hooks.print_task_result'
                )
                logger.info(f"Tarea de notificación 'Update Requested' para {user_request.unique_code} encolada.")
            except Exception as e_async:
                logger.error(
                    f"Error al encolar la tarea de notificación 'Update Requested' para {user_request.unique_code}: {e_async}",
                    exc_info=True)
            # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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

    is_permitted = False
    active_statuses_for_update = ['pending', 'in_progress', 'qa_pending', 'qa_in_progress']
    if user_request.status in active_statuses_for_update:
        if (user == user_request.operator) or (user == user_request.qa_agent) or is_admin(user):
            is_permitted = True

    if not is_permitted:
        messages.error(request, _("You do not have permission to provide an update for this request at this time."))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        form = ProvideUpdateForm(request.POST)
        if form.is_valid():
            update_message_text = form.cleaned_data['update_message']
            try:
                if user_request.update_needed_flag:
                    user_request.update_needed_flag = False
                    user_request.save(update_fields=['update_needed_flag'])
                    logger.info(f"User {user.email} set update_needed_flag=False for request {pk}.")
                else:
                    logger.info(f"User {user.email} provided a proactive update for request {pk}.")

                # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
                try:
                    current_host = request.get_host()
                    current_scheme = request.scheme
                    async_task(
                        'tasks.notifications.notify_update_provided',
                        user_request.pk,
                        user.pk,  # PK del usuario que está proveyendo la actualización
                        update_message_text,  # El mensaje del formulario
                        http_request_host=current_host,
                        http_request_scheme=current_scheme,
                        task_name=f"NotifyUpdateProvided-{user_request.unique_code}",
                        hook='tasks.hooks.print_task_result'
                    )
                    logger.info(f"Tarea de notificación 'Update Provided' para {user_request.unique_code} encolada.")
                except Exception as e_async:
                    logger.error(
                        f"Error al encolar la tarea 'Update Provided' para {user_request.unique_code}: {e_async}", exc_info=True)
                # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

                messages.success(request, _("Update provided and notifications sent."))
            except Exception as e:
                logger.error(f"Error setting update_needed_flag=False for request {pk}: {e}", exc_info=True)
                messages.error(request, _("An error occurred while clearing the update flag."))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in update message: {error}")

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
            original_cancelled_by_user_pk = user_request.cancelled_by.pk if user_request.cancelled_by else None
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

            # ----> INICIO: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----
            try:
                current_host = request.get_host()
                current_scheme = request.scheme
                async_task(
                    'tasks.notifications.notify_request_uncancelled',
                    user_request.pk,  # PK de la solicitud
                    user.pk,  # PK del usuario que descanceló
                    original_cancelled_by_user_pk,  # PK de quien canceló originalmente
                    http_request_host=current_host,
                    http_request_scheme=current_scheme,
                    task_name=f"NotifyRequestUncancelled-{user_request.unique_code}",
                    hook='tasks.hooks.print_task_result'
                )
                logger.info(f"Tarea de notificación 'Request Uncancelled' para {user_request.unique_code} encolada.")
            except Exception as e_async:
                logger.error(
                    f"Error al encolar la tarea 'Request Uncancelled' para {user_request.unique_code}: {e_async}",
                    exc_info=True)
            # ----> FIN: LLAMADA A LA NOTIFICACIÓN ASÍNCRONA <----

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
    display_timezone_pref = request.GET.get('timezone_display', 'local')
    today = timezone.localdate()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid start date format. Using default.")
            start_date = today.replace(day=1)
    else:
        start_date = today.replace(day=1)

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid end date format. Using default.")
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
    )

    requests_with_final_price = completed_requests_in_period.annotate(
        calculated_discount=ExpressionWrapper(
            F('grand_total_client_price_completed') * (
                        Cast(F('discount_percentage'), DecimalField(max_digits=5, decimal_places=2)) / Decimal(
                    '100.0')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).annotate(
        final_price=ExpressionWrapper(
            F('grand_total_client_price_completed') - F('calculated_discount'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    duration_expression = ExpressionWrapper(F('completed_at') - F('effective_start_time_for_tat'),
                                            output_field=fields.DurationField())

    overall_summary = requests_with_final_price.aggregate(
        total_requests=Count('pk'),
        grand_total_cost=Coalesce(Sum('final_price'), Value(Decimal('0.00'))),
        overall_average_tat=Avg(duration_expression)
    )
    total_requests_count = overall_summary.get('total_requests', 0)
    grand_total_cost = overall_summary.get('grand_total_cost', Decimal('0.00'))
    overall_average_tat = overall_summary.get('overall_average_tat')
    average_cost_per_request = grand_total_cost / total_requests_count if total_requests_count > 0 else Decimal('0.00')

    team_summary_from_db = requests_with_final_price.values('team').annotate(
        subtotal=Coalesce(Sum('final_price'), Value(Decimal('0.00'))),
        request_count=Count('pk'),
        avg_cost=Avg('final_price'),
        avg_tat=Avg(duration_expression)
    ).order_by('-subtotal')

    team_summary_list = []
    team_choices_dict = dict(TEAM_CHOICES)
    for team_data in team_summary_from_db:
        team_display_name = team_choices_dict.get(team_data['team'], team_data['team'] or "Unassigned")
        team_summary_list.append(
            {'name': team_display_name, 'subtotal': team_data['subtotal'], 'request_count': team_data['request_count'],
             'avg_cost': team_data['avg_cost'], 'avg_tat': team_data['avg_tat']})

    process_summary_from_db = requests_with_final_price.values('type_of_process').annotate(
        subtotal=Coalesce(Sum('final_price'), Value(Decimal('0.00'))),
        request_count=Count('pk'),
        avg_cost=Avg('final_price'),
        avg_tat=Avg(duration_expression)
    ).order_by('-subtotal')

    process_summary_list = []
    process_choices_dict = dict(TYPE_CHOICES)
    for process_data in process_summary_from_db:
        process_display_name = process_choices_dict.get(process_data['type_of_process'],
                                                        process_data['type_of_process'])
        process_summary_list.append({'name': process_display_name, 'subtotal': process_data['subtotal'],
                                     'request_count': process_data['request_count'],
                                     'avg_cost': process_data['avg_cost'], 'avg_tat': process_data['avg_tat']})
    team_chart_labels = [item.get('name') for item in team_summary_list if item.get('subtotal', 0) > 0]
    team_chart_data = [float(item.get('subtotal')) for item in team_summary_list if item.get('subtotal', 0) > 0]
    process_chart_labels = [item.get('name') for item in process_summary_list if item.get('subtotal', 0) > 0]
    process_chart_data = [float(item.get('subtotal')) for item in process_summary_list if item.get('subtotal', 0) > 0]

    target_processes_for_scatter = ['address_validation', 'user_records', 'property_records', 'unit_transfer',
                                    'deactivation_toggle']
    target_teams_for_scatter = [TEAM_REVENUE, TEAM_SUPPORT]
    scatter_charts_data = {}
    type_choices_dict_scatter = dict(TYPE_CHOICES)
    for process_key in target_processes_for_scatter:
        process_specific_requests = requests_with_final_price.filter(type_of_process=process_key)
        current_process_datasets = []
        for team_key in target_teams_for_scatter:
            team_specific_requests = process_specific_requests.filter(team=team_key).order_by('completed_at')
            data_points = []
            for req in team_specific_requests:
                if req.completed_at and req.final_price is not None:
                    data_points.append({
                        'x': req.completed_at.isoformat(),
                        'y': float(req.final_price),
                        'pk': req.pk
                    })
            if data_points:
                border_color = 'rgba(255, 99, 132, 1)' if team_key == TEAM_REVENUE else 'rgba(54, 162, 235, 1)'
                bg_color = 'rgba(255, 99, 132, 0.2)' if team_key == TEAM_REVENUE else 'rgba(54, 162, 235, 0.2)'
                current_process_datasets.append(
                    {'label': dict(TEAM_CHOICES).get(team_key, team_key), 'data': data_points,
                     'borderColor': border_color, 'backgroundColor': bg_color, 'tension': 0.3, 'fill': False,
                     'pointRadius': 3, 'pointBackgroundColor': border_color, 'showLine': False})
        if current_process_datasets:
            scatter_charts_data[process_key] = {
                'chart_title': f'Cost Trend for {type_choices_dict_scatter.get(process_key, process_key)}',
                'datasets': current_process_datasets}

    try:
        request_detail_url_template = reverse('tasks:request_detail', args=[0]).replace('/0/', '/REPLACE_PK/')
    except Exception as e:
        logger.error(f"Could not generate URL template for request_detail: {e}")
        request_detail_url_template = "/request/REPLACE_PK/"
        messages.error(request, "Error generating URL template for chart links.")

    user_timezone_name = request.user.timezone if request.user.is_authenticated and request.user.timezone else 'UTC'

    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_requests_count': total_requests_count,
        'grand_total_cost': grand_total_cost,
        'average_cost_per_request': average_cost_per_request,
        'overall_average_tat': overall_average_tat,
        'team_summary': team_summary_list,
        'process_summary': process_summary_list,
        'team_chart_labels': team_chart_labels,
        'team_chart_data': team_chart_data,
        'process_chart_labels': process_chart_labels,
        'process_chart_data': process_chart_data,
        'scatter_charts_data': scatter_charts_data,
        'request_detail_url_template': request_detail_url_template,
        'display_timezone': display_timezone_pref,
        'user_timezone_name': user_timezone_name,
        'page_title': 'Cost & Performance Summary'
    }
    return render(request, 'tasks/cost_summary.html', context)


def _generate_address_validation_csv(request_items, filename="address_validation_report.csv"):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Encabezados para Address Validation
    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Team', 'Priority',
        'Partner Name', 'Status', 'Date Completed', 'TAT',
        'Submitted Main File', 'Submitted Main Link', 'Special Instructions',
        'Operator', 'Operated At', 'QA Agent', 'QA Pending At', 'QA In Progress At',
        # Campos de Operación Comunes
        'Users Updated', 'Properties Updated (Count)', 'Bulk Updates',
        'Manual Properties Updated (Count)', 'Manual Units Updated',
        'CSV Rows Updated', 'Processing Reports Rows',
        'Operator Spreadsheet Link', 'Operating Notes',
        # Campos Específicos de Address Validation (Submisión Manual)
        'AV - Policyholders (Manual)',
        'AV - Opportunity ID (Manual/Custom)',
        'AV - User Email Addresses (Manual)',
        # Campos de Integración con Salesforce (Info de la Opportunity)
        'SF - Standard Opp ID', 'SF - Opportunity Name', 'SF - Number of Units',
        'SF - Opportunity Link', 'SF - Account Manager', 'SF - Closed Won Date',
        'SF - Leasing Integration Software', 'SF - Information Needed For Assets',
        # Campos de Salida de Operación para Address Validation (muchos son de SF)
        'AV - Assets Uploaded to SF?', 'AV - Number of Units Processed',
        'AV - Number of Invalid Units', 'AV - Link to Assets (Output)',
        'AV - Success Output Link', 'AV - Failed Output Link',
        'AV - Rhino Accounts Created?',
        # Archivos Adjuntos
        'Uploaded Address Validation Files',  # Lista de nombres de archivo
        'Salesforce Attachment Names',  # Lista de nombres de archivo
        # Campos de Costos (Cliente)
        'Subtotal Address Validation Unit Price',
        'Subtotal Bulk Update Price', 'Subtotal Manual Property Update Price', 'Subtotal CSV Update Price',
        'Subtotal Processing Report Price', 'Subtotal Manual Unit Update Price', 'Total Price'
    ]
    writer.writerow(headers)

    for req in request_items:
        # Formatear fechas y otros campos
        timestamp_str = req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else ''
        completed_at_str = req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else ''
        operated_at_str = req.operated_at.strftime('%Y-%m-%d %H:%M:%S') if req.operated_at else ''
        qa_pending_at_str = req.qa_pending_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_pending_at else ''
        qa_in_progress_at_str = req.qa_in_progress_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_in_progress_at else ''
        sf_closed_won_date_str = req.salesforce_closed_won_date.strftime(
            '%Y-%m-%d') if req.salesforce_closed_won_date else ''
        tat_str = str(req.calculated_turn_around_time) if req.calculated_turn_around_time else ''
        user_file_name = req.user_file.name.split('/')[-1] if req.user_file else ''

        # Listar nombres de archivos adjuntos de AddressValidationFile
        av_files_list = [os.path.basename(f.uploaded_file.name) for f in req.address_validation_files.all()]
        av_files_str = ", ".join(av_files_list) if av_files_list else ''

        # Listar nombres de archivos adjuntos de SalesforceAttachmentLog
        sf_attachments_list = [att.file_name for att in req.salesforce_attachments.all()]
        sf_attachments_str = ", ".join(sf_attachments_list) if sf_attachments_list else ''

        assets_uploaded_str = 'Yes' if req.assets_uploaded else ('No' if req.assets_uploaded is False else '')
        rhino_accounts_created_str = 'Yes' if req.rhino_accounts_created else (
            'No' if req.rhino_accounts_created is False else '')

        row = [
            req.unique_code,
            timestamp_str,
            req.requested_by.email if req.requested_by else '',
            req.get_team_display(),
            req.get_priority_display(),
            req.partner_name,
            req.get_status_display(),
            completed_at_str,
            tat_str,
            user_file_name,  # El campo user_file genérico
            req.user_link,  # El campo user_link genérico
            req.special_instructions,
            req.operator.email if req.operator else '',
            operated_at_str,
            req.qa_agent.email if req.qa_agent else '',
            qa_pending_at_str,
            qa_in_progress_at_str,
            # Campos de Operación
            req.num_updated_users, req.num_updated_properties, req.bulk_updates,
            req.manual_updated_properties, req.manual_updated_units,
            req.update_by_csv_rows, req.processing_reports_rows,
            req.operator_spreadsheet_link, req.operating_notes,
            # Campos Específicos de Address Validation (Submisión Manual)
            req.address_validation_policyholders,
            req.address_validation_opportunity_id,  # El ID de Opp. custom
            req.address_validation_user_email_addresses,
            # Campos de Integración con Salesforce
            req.salesforce_standard_opp_id,
            req.salesforce_opportunity_name,
            req.salesforce_number_of_units,
            req.salesforce_link,
            req.salesforce_account_manager,
            sf_closed_won_date_str,
            req.salesforce_leasing_integration_software,
            req.salesforce_information_needed_for_assets,
            # Campos de Salida de Operación para AV
            assets_uploaded_str,
            req.av_number_of_units,
            req.av_number_of_invalid_units,
            req.link_to_assets,
            req.success_output_link,
            req.failed_output_link,
            rhino_accounts_created_str,
            # Archivos Adjuntos
            av_files_str,
            sf_attachments_str,
            # Costos
            req.subtotal_address_validation_unit_client_price_completed if req.status == 'completed' else '',
            req.subtotal_bulk_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_property_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_csv_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_processing_report_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_unit_update_client_price_completed if req.status == 'completed' else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

def _generate_user_records_csv(request_items, filename="user_records_report.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Team', 'Priority',
        'Partner Name', 'Status', 'Date Completed', 'TAT',
        'User Groups Data (JSON)', 'Submitted File', 'Submitted Link', 'Special Instructions',
        'Operator', 'Operated At', 'QA Agent', 'QA Pending At', 'QA In Progress At',
        # Campos de operación comunes
        'Users Updated', 'Properties Updated', 'Bulk Updates', 'Manual Properties Updated',
        'Manual Units Updated', 'CSV Rows Updated', 'Processing Reports Rows',
        'Operator Spreadsheet Link', 'Operating Notes',
        # Campos de costos (Cliente)
        'Subtotal Bulk Update Price', 'Subtotal Manual Property Update Price', 'Subtotal CSV Update Price',
        'Subtotal Processing Report Price', 'Subtotal Manual Unit Update Price', 'Total Price'
    ]
    writer.writerow(headers)

    for req in request_items:
        # Formatear user_groups_data
        user_groups_str = ""
        if req.user_groups_data:
            try:
                user_groups_str = json.dumps(req.user_groups_data)
            except TypeError:
                user_groups_str = str(req.user_groups_data)

        row = [
            req.unique_code,
            req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else '',
            req.requested_by.email if req.requested_by else '',
            req.get_team_display(),
            req.get_priority_display(),
            req.partner_name,
            req.get_status_display(),
            req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else '',
            str(req.calculated_turn_around_time) if req.calculated_turn_around_time else '',
            user_groups_str,
            req.user_file.name.split('/')[-1] if req.user_file else '',
            req.user_link,
            req.special_instructions,
            req.operator.email if req.operator else '',
            req.operated_at.strftime('%Y-%m-%d %H:%M:%S') if req.operated_at else '',
            req.qa_agent.email if req.qa_agent else '',
            req.qa_pending_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_pending_at else '',
            req.qa_in_progress_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_in_progress_at else '',
            req.num_updated_users,
            req.num_updated_properties,
            req.bulk_updates,
            req.manual_updated_properties,
            req.manual_updated_units,
            req.update_by_csv_rows,
            req.processing_reports_rows,
            req.operator_spreadsheet_link,
            req.operating_notes,
            # Costos del Cliente (si está completada)
            req.subtotal_bulk_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_property_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_csv_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_processing_report_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_unit_update_client_price_completed if req.status == 'completed' else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

def _generate_property_records_csv(request_items, filename="property_records_report.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Encabezados para Property Records
    # Incluye campos generales, de operación, costos y TODOS los específicos de Property Records
    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Team', 'Priority',
        'Partner Name', 'Properties Affected (General)', 'Status', 'Date Completed', 'TAT',
        'Submitted File', 'Submitted Link', 'Special Instructions',
        'Operator', 'Operated At', 'QA Agent', 'QA Pending At', 'QA In Progress At',
        # Campos de Operación Comunes
        'Users Updated', 'Properties Updated (Count)', 'Bulk Updates',
        'Manual Properties Updated (Count)', 'Manual Units Updated',
        'CSV Rows Updated', 'Processing Reports Rows',
        'Operator Spreadsheet Link', 'Operating Notes',
        # Campos Específicos de Property Records
        'Property Record Type',
        'New Property Names', 'New PMC', 'New Policyholder (Legal Entity)',
        'Corrected Address', 'Updated Property Type', 'Property Units (New/Updated)',
        'Coverage Type', 'Coverage Multiplier', 'Coverage Amount',
        'Integration Type', 'Integration Codes', 'Bank Details',
        # Campos de Costos (Cliente)
        'Subtotal Bulk Update Price', 'Subtotal Manual Property Update Price', 'Subtotal CSV Update Price',
        'Subtotal Processing Report Price', 'Subtotal Manual Unit Update Price', 'Total Price'
    ]
    writer.writerow(headers)

    for req in request_items:
        # Formatear fechas y otros campos
        timestamp_str = req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else ''
        completed_at_str = req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else ''
        operated_at_str = req.operated_at.strftime('%Y-%m-%d %H:%M:%S') if req.operated_at else ''
        qa_pending_at_str = req.qa_pending_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_pending_at else ''
        qa_in_progress_at_str = req.qa_in_progress_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_in_progress_at else ''
        tat_str = str(req.calculated_turn_around_time) if req.calculated_turn_around_time else ''
        user_file_name = req.user_file.name.split('/')[-1] if req.user_file else ''

        row = [
            req.unique_code,
            timestamp_str,
            req.requested_by.email if req.requested_by else '',
            req.get_team_display(),
            req.get_priority_display(),
            req.partner_name,
            req.properties, # El campo genérico 'properties'
            req.get_status_display(),
            completed_at_str,
            tat_str,
            user_file_name,
            req.user_link,
            req.special_instructions,
            req.operator.email if req.operator else '',
            operated_at_str,
            req.qa_agent.email if req.qa_agent else '',
            qa_pending_at_str,
            qa_in_progress_at_str,
            # Campos de Operación
            req.num_updated_users,
            req.num_updated_properties,
            req.bulk_updates,
            req.manual_updated_properties,
            req.manual_updated_units,
            req.update_by_csv_rows,
            req.processing_reports_rows,
            req.operator_spreadsheet_link,
            req.operating_notes,
            # Campos Específicos de Property Records
            req.get_property_records_type_display() if req.property_records_type else '',
            req.property_records_new_names,
            req.property_records_new_pmc,
            req.property_records_new_policyholder,
            req.property_records_corrected_address,
            req.get_property_records_updated_type_display() if req.property_records_updated_type else '',
            req.property_records_units,
            req.get_property_records_coverage_type_display() if req.property_records_coverage_type else '',
            req.get_property_records_coverage_multiplier_display() if req.property_records_coverage_multiplier else '',
            req.property_records_coverage_amount,
            req.get_property_records_integration_type_display() if req.property_records_integration_type else '',
            req.property_records_integration_codes,
            req.property_records_bank_details,
            # Costos del Cliente (si está completada)
            req.subtotal_bulk_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_property_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_csv_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_processing_report_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_unit_update_client_price_completed if req.status == 'completed' else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

def _generate_unit_transfer_csv(request_items, filename="unit_transfer_report.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Encabezados para Unit Transfer
    # Incluye campos generales, de operación, costos y TODOS los específicos de Unit Transfer
    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Team', 'Priority',
        'Partner Name (Origin)', 'Status', 'Date Completed', 'TAT',
        'Submitted File', 'Submitted Link', 'Special Instructions',
        'Operator', 'Operated At', 'QA Agent', 'QA Pending At', 'QA In Progress At',
        # Campos de Operación Comunes
        'Users Updated', 'Properties Updated (Count)', 'Bulk Updates',
        'Manual Properties Updated (Count)', 'Manual Units Updated',
        'CSV Rows Updated', 'Processing Reports Rows',
        'Operator Spreadsheet Link', 'Operating Notes',
        # Campos Específicos de Unit Transfer
        'Unit Transfer Type',
        'New Partner/Prospect Name (Destination)',
        'Receiving Partner PSM',
        'Properties to Transfer (from general field)',
        'New Policyholders (if provided)',
        'User Email Addresses for New Partner (if provided)',
        'Prospect Portfolio Size',
        'Prospect Landlord Type',
        'Proof of Sale (Link)',
        # Campos de Costos (Cliente)
        'Subtotal Bulk Update Price', 'Subtotal Manual Property Update Price', 'Subtotal CSV Update Price',
        'Subtotal Processing Report Price', 'Subtotal Manual Unit Update Price', 'Total Price'
    ]
    writer.writerow(headers)

    for req in request_items:
        # Formatear fechas y otros campos
        timestamp_str = req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else ''
        completed_at_str = req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else ''
        operated_at_str = req.operated_at.strftime('%Y-%m-%d %H:%M:%S') if req.operated_at else ''
        qa_pending_at_str = req.qa_pending_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_pending_at else ''
        qa_in_progress_at_str = req.qa_in_progress_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_in_progress_at else ''
        tat_str = str(req.calculated_turn_around_time) if req.calculated_turn_around_time else ''
        user_file_name = req.user_file.name.split('/')[-1] if req.user_file else ''

        row = [
            req.unique_code,
            timestamp_str,
            req.requested_by.email if req.requested_by else '',
            req.get_team_display(),
            req.get_priority_display(),
            req.partner_name, # Este es el Partner Name (Origin)
            req.get_status_display(),
            completed_at_str,
            tat_str,
            user_file_name,
            req.user_link,
            req.special_instructions,
            req.operator.email if req.operator else '',
            operated_at_str,
            req.qa_agent.email if req.qa_agent else '',
            qa_pending_at_str,
            qa_in_progress_at_str,
            # Campos de Operación
            req.num_updated_users,
            req.num_updated_properties,
            req.bulk_updates,
            req.manual_updated_properties,
            req.manual_updated_units,
            req.update_by_csv_rows,
            req.processing_reports_rows,
            req.operator_spreadsheet_link,
            req.operating_notes,
            # Campos Específicos de Unit Transfer
            req.get_unit_transfer_type_display() if req.unit_transfer_type else '',
            req.unit_transfer_new_partner_prospect_name,
            req.unit_transfer_receiving_partner_psm,
            req.properties, # El campo genérico 'properties' se usa para "Properties to Transfer"
            req.unit_transfer_new_policyholders,
            req.unit_transfer_user_email_addresses,
            req.unit_transfer_prospect_portfolio_size,
            req.get_unit_transfer_prospect_landlord_type_display() if req.unit_transfer_prospect_landlord_type else '',
            req.unit_transfer_proof_of_sale,
            # Costos del Cliente (si está completada)
            req.subtotal_bulk_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_property_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_csv_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_processing_report_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_unit_update_client_price_completed if req.status == 'completed' else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

def _generate_deactivation_toggle_csv(request_items, filename="deactivation_toggle_report.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Encabezados para Deactivation and Toggle
    # Incluye campos generales, de operación, costos y TODOS los específicos de Deactivation/Toggle
    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Team', 'Priority',
        'Partner Name', 'Properties Affected (General)', 'Status', 'Date Completed', 'TAT',
        'Submitted File', 'Submitted Link', 'Special Instructions',
        'Operator', 'Operated At', 'QA Agent', 'QA Pending At', 'QA In Progress At',
        # Campos de Operación Comunes (si aplican y se registran para este tipo)
        'Users Updated', 'Properties Updated (Count)', 'Bulk Updates',
        'Manual Properties Updated (Count)', 'Manual Units Updated',
        'CSV Rows Updated', 'Processing Reports Rows',
        'Operator Spreadsheet Link', 'Operating Notes',
        # Campos Específicos de Deactivation and Toggle
        'Deactivation/Toggle Type',
        'Active Policies on Properties?',
        'Properties with Active Policies',
        'Context/Justification',
        'Leadership Approval By', # Si está aprobado, mostrará quién. Si no, estará vacío.
        'Marked as Churned in SF?',
        # Campos de Costos (Cliente)
        'Subtotal Bulk Update Price', 'Subtotal Manual Property Update Price', 'Subtotal CSV Update Price',
        'Subtotal Processing Report Price', 'Subtotal Manual Unit Update Price', 'Total Price'
    ]
    writer.writerow(headers)

    for req in request_items:
        # Formatear fechas y otros campos
        timestamp_str = req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else ''
        completed_at_str = req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else ''
        operated_at_str = req.operated_at.strftime('%Y-%m-%d %H:%M:%S') if req.operated_at else ''
        qa_pending_at_str = req.qa_pending_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_pending_at else ''
        qa_in_progress_at_str = req.qa_in_progress_at.strftime('%Y-%m-%d %H:%M:%S') if req.qa_in_progress_at else ''
        tat_str = str(req.calculated_turn_around_time) if req.calculated_turn_around_time else ''
        user_file_name = req.user_file.name.split('/')[-1] if req.user_file else ''

        active_policies_str = 'Yes' if req.deactivation_toggle_active_policies else ('No' if req.deactivation_toggle_active_policies is False else '')
        marked_as_churned_str = 'Yes' if req.deactivation_toggle_marked_as_churned else ('No' if req.deactivation_toggle_marked_as_churned is False else '')

        row = [
            req.unique_code,
            timestamp_str,
            req.requested_by.email if req.requested_by else '',
            req.get_team_display(),
            req.get_priority_display(),
            req.partner_name,
            req.properties, # El campo genérico 'properties'
            req.get_status_display(),
            completed_at_str,
            tat_str,
            user_file_name,
            req.user_link,
            req.special_instructions,
            req.operator.email if req.operator else '',
            operated_at_str,
            req.qa_agent.email if req.qa_agent else '',
            qa_pending_at_str,
            qa_in_progress_at_str,
            # Campos de Operación (pueden estar vacíos para este tipo de request)
            req.num_updated_users,
            req.num_updated_properties,
            req.bulk_updates,
            req.manual_updated_properties,
            req.manual_updated_units,
            req.update_by_csv_rows,
            req.processing_reports_rows,
            req.operator_spreadsheet_link,
            req.operating_notes,
            # Campos Específicos de Deactivation and Toggle
            req.get_deactivation_toggle_type_display() if req.deactivation_toggle_type else '',
            active_policies_str,
            req.deactivation_toggle_properties_with_policies,
            req.deactivation_toggle_context,
            req.get_deactivation_toggle_leadership_approval_display() if req.deactivation_toggle_leadership_approval else '',
            marked_as_churned_str,
            # Costos
            req.subtotal_bulk_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_property_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_csv_update_client_price_completed if req.status == 'completed' else '',
            req.subtotal_processing_report_client_price_completed if req.status == 'completed' else '',
            req.subtotal_manual_unit_update_client_price_completed if req.status == 'completed' else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

def _generate_stripe_disputes_csv(request_items, filename="stripe_disputes_report.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Encabezados específicos para Stripe Disputes
    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Status', 'Date Completed', 'TAT',
        'Stripe Premium Disputes (Count)', 'Stripe RI Disputes (Count)',
        'Submitted File', 'Special Instructions', 'Operating Notes',
        'Operator', 'QA Agent',
        'Grand Total Client Price',
    ]
    writer.writerow(headers)

    for req in request_items:
        # Formatear datos para el CSV
        timestamp_str = req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else ''
        completed_at_str = req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else ''
        tat_str = str(req.calculated_turn_around_time) if req.calculated_turn_around_time else ''
        user_file_name = req.user_file.name.split('/')[-1] if req.user_file else ''

        row = [
            req.unique_code,
            timestamp_str,
            req.requested_by.email if req.requested_by else '',
            req.get_status_display(),
            completed_at_str,
            tat_str,
            req.stripe_premium_disputes,
            req.stripe_ri_disputes,
            user_file_name,
            req.special_instructions,
            req.operating_notes,
            req.operator.email if req.operator else '',
            req.qa_agent.email if req.qa_agent else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

def _generate_generating_xml_csv(request_items, filename="generating_xml_report.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    # Encabezados específicos para Generating XML
    headers = [
        'Request ID', 'Date Requested', 'Requested By', 'Status', 'Date Completed', 'TAT',
        'XML State', 'Carrier RVIC Selected', 'Carrier SSIC Selected',
        'Submitted Spreadsheet', 'Submitted RVIC ZIP', 'Submitted SSIC ZIP',
        'Operator Notes', 'Operator', 'QA Agent',
        'Operator RVIC File 1', 'Operator RVIC File 2 (UT ZIP)',
        'Operator SSIC File 1', 'Operator SSIC File 2 (UT ZIP)',
        # Costos
        'Grand Total Client Price',
    ]
    writer.writerow(headers)

    for req in request_items:
        row = [
            req.unique_code,
            req.timestamp.strftime('%Y-%m-%d %H:%M:%S') if req.timestamp else '',
            req.requested_by.email if req.requested_by else '',
            req.get_status_display(),
            req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else '',
            str(req.calculated_turn_around_time) if req.calculated_turn_around_time else '',
            req.get_xml_state_display() if req.xml_state else '',
            'Yes' if req.xml_carrier_rvic else 'No',
            'Yes' if req.xml_carrier_ssic else 'No',
            req.user_file.name.split('/')[-1] if req.user_file else '',
            req.xml_rvic_zip_file.name.split('/')[-1] if req.xml_rvic_zip_file else '',
            req.xml_ssic_zip_file.name.split('/')[-1] if req.xml_ssic_zip_file else '',
            req.operating_notes,
            req.operator.email if req.operator else '',
            req.qa_agent.email if req.qa_agent else '',
            req.operator_rvic_file_slot1.name.split('/')[-1] if req.operator_rvic_file_slot1 else '',
            req.operator_rvic_file_slot2.name.split('/')[-1] if req.operator_rvic_file_slot2 else '',
            req.operator_ssic_file_slot1.name.split('/')[-1] if req.operator_ssic_file_slot1 else '',
            req.operator_ssic_file_slot2.name.split('/')[-1] if req.operator_ssic_file_slot2 else '',
            req.final_price_after_discount if req.status == 'completed' else '',
        ]
        writer.writerow(row)
    return response

@login_required
@user_passes_test(user_is_admin_or_leader)
def generate_accounting_stripe_report_view(request):
    today = timezone.localdate()
    default_start_date = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    default_end_date = today.replace(day=last_day)

    # Definir los estados relevantes para Stripe Disputes y su orden/agrupación para el filtro
    # Estos son los valores que se usarán para construir las opciones en el formulario
    STATUS_OPTIONS_FOR_STRIPE_FILTER_ORDER = [
        'pending',
        'in_progress_group',  # Valor especial para representar el grupo
        'blocked',
        'completed',
        'cancelled'
    ]

    # Mapeo de los valores del formulario a los valores reales de la base de datos
    STATUS_GROUP_MAPPING = {
        'in_progress_group': ['in_progress', 'qa_pending', 'qa_in_progress']
    }

    # Obtener los display names de STATUS_CHOICES
    status_display_dict = dict(STATUS_CHOICES)

    # Construir las opciones para el formulario
    status_filter_options_for_template = []
    for status_key in STATUS_OPTIONS_FOR_STRIPE_FILTER_ORDER:
        if status_key == 'in_progress_group':
            display_name = "In Progress (includes QA stages)"
        else:
            display_name = status_display_dict.get(status_key, status_key.title())
        status_filter_options_for_template.append({
            'value': status_key,
            'display': display_name
        })

    selected_statuses_from_form = request.GET.getlist('status')

    if not selected_statuses_from_form and 'generate_csv' in request.GET:
        pass
    elif not selected_statuses_from_form:  # Para la carga inicial del formulario
        selected_statuses_from_form = [opt['value'] for opt in status_filter_options_for_template]

    if request.method == 'GET' and 'generate_csv' in request.GET:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else default_start_date
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else default_end_date
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            context = {
                'status_filter_options': status_filter_options_for_template,
                'selected_statuses': selected_statuses_from_form,
                'default_start_date': default_start_date.strftime('%Y-%m-%d'),
                'default_end_date': default_end_date.strftime('%Y-%m-%d'),
                'page_title': 'Accounting Report - Stripe Disputes'
            }
            return render(request, 'tasks/accounting_stripe_report_form.html', context)

        start_datetime_utc = timezone.make_aware(datetime.combine(start_date, time.min), pytz.utc)
        end_datetime_utc = timezone.make_aware(datetime.combine(end_date, time.max), pytz.utc)

        queryset = UserRecordsRequest.objects.filter(
            type_of_process='stripe_disputes',
            timestamp__gte=start_datetime_utc,  # o completed_at si prefieres
            timestamp__lte=end_datetime_utc
        ).select_related('requested_by', 'operator', 'qa_agent').order_by('-timestamp')

        # Lógica de filtrado de estado actualizada
        final_status_filter_values = []
        if selected_statuses_from_form:  # Solo filtrar si hay selecciones
            for status_val in selected_statuses_from_form:
                if status_val in STATUS_GROUP_MAPPING:
                    final_status_filter_values.extend(STATUS_GROUP_MAPPING[status_val])
                else:
                    # Asegurarse de que solo se añadan claves de estado válidas y no agrupadores
                    if status_val in status_display_dict:  # status_display_dict tiene las claves reales
                        final_status_filter_values.append(status_val)

            if final_status_filter_values:  # Si después de procesar hay valores, filtrar
                queryset = queryset.filter(
                    status__in=list(set(final_status_filter_values)))  # Usar set para evitar duplicados

        return _generate_stripe_disputes_csv(queryset,
                                             filename=f"stripe_disputes_report_{start_date_str}_to_{end_date_str}.csv")

    else:  # Solicitud GET inicial
        context = {
            'status_filter_options': status_filter_options_for_template,  # Opciones para el form
            'selected_statuses': selected_statuses_from_form,  # Los que deben estar marcados
            'default_start_date': default_start_date.strftime('%Y-%m-%d'),
            'default_end_date': default_end_date.strftime('%Y-%m-%d'),
            'page_title': 'Accounting Report - Stripe Disputes'
        }
        return render(request, 'tasks/accounting_stripe_report.html', context)

@login_required
@user_passes_test(user_is_admin_or_leader)
def generate_compliance_xml_report_view(request):
    today = timezone.localdate()
    default_start_date = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    default_end_date = today.replace(day=last_day)

    # Preparar opciones de status para el filtro (como en Stripe Disputes)
    STATUS_OPTIONS_FOR_XML_FILTER_ORDER = ['pending', 'in_progress_group', 'blocked', 'completed', 'cancelled']
    STATUS_GROUP_MAPPING = {'in_progress_group': ['in_progress', 'qa_pending', 'qa_in_progress']}
    status_display_dict = dict(STATUS_CHOICES)
    status_filter_options_for_template = []
    for status_key in STATUS_OPTIONS_FOR_XML_FILTER_ORDER:
        display_name = "In Progress (includes QA stages)" if status_key == 'in_progress_group' else status_display_dict.get(
            status_key, status_key.title())
        status_filter_options_for_template.append({'value': status_key, 'display': display_name})

    # Estado inicial de los filtros para GET
    current_selected_statuses = request.GET.getlist('status')
    if not current_selected_statuses and not 'generate_csv' in request.GET:  # Carga inicial del form
        current_selected_statuses = [opt['value'] for opt in status_filter_options_for_template]

    current_selected_xml_states = request.GET.getlist('xml_state')
    if not current_selected_xml_states and not 'generate_csv' in request.GET:
        current_selected_xml_states = [s[0] for s in XML_STATE_CHOICES]

    current_selected_carrier_rvic = request.GET.get('carrier_rvic') == 'on'
    current_selected_carrier_ssic = request.GET.get('carrier_ssic') == 'on'
    # Si es la carga inicial y no se generan filtros, ambos carriers por defecto
    if not 'generate_csv' in request.GET and not request.GET.get('carrier_rvic') and not request.GET.get(
            'carrier_ssic'):
        current_selected_carrier_rvic = True
        current_selected_carrier_ssic = True

    if request.method == 'GET' and 'generate_csv' in request.GET:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        # selected_statuses ya está en current_selected_statuses
        # selected_xml_states ya está en current_selected_xml_states
        # selected_carrier_rvic/ssic ya están en current_selected_carrier_rvic/ssic

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else default_start_date
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else default_end_date
        except ValueError:
            messages.error(request, _("Invalid date format. Please use YYYY-MM-DD."))
            # Re-renderizar el formulario
            context = {
                'status_filter_options': status_filter_options_for_template,
                'selected_statuses': current_selected_statuses,
                'xml_state_choices': XML_STATE_CHOICES,
                'selected_xml_states': current_selected_xml_states,
                'selected_carrier_rvic': current_selected_carrier_rvic,
                'selected_carrier_ssic': current_selected_carrier_ssic,
                'default_start_date': default_start_date.strftime('%Y-%m-%d'),
                'default_end_date': default_end_date.strftime('%Y-%m-%d'),
                'page_title': 'Compliance Report - Generating XML'
            }
            return render(request, 'tasks/compliance_xml_report_form.html', context)

        start_datetime_utc = timezone.make_aware(datetime.combine(start_date, time.min), pytz.utc)
        end_datetime_utc = timezone.make_aware(datetime.combine(end_date, time.max), pytz.utc)

        queryset = UserRecordsRequest.objects.filter(
            type_of_process='generating_xml',
            timestamp__gte=start_datetime_utc,
            timestamp__lte=end_datetime_utc
        ).select_related('requested_by', 'operator', 'qa_agent').order_by('-timestamp')

        # Aplicar filtro de estado
        final_status_filter_values = []
        if current_selected_statuses:
            for status_val in current_selected_statuses:
                if status_val in STATUS_GROUP_MAPPING:
                    final_status_filter_values.extend(STATUS_GROUP_MAPPING[status_val])
                elif status_val in status_display_dict:
                    final_status_filter_values.append(status_val)
            if final_status_filter_values:
                queryset = queryset.filter(status__in=list(set(final_status_filter_values)))

        # Aplicar filtro de XML State
        if current_selected_xml_states:
            queryset = queryset.filter(xml_state__in=current_selected_xml_states)

        # Aplicar filtro de Carriers
        if current_selected_carrier_rvic and current_selected_carrier_ssic:
            queryset = queryset.filter(xml_carrier_rvic=True, xml_carrier_ssic=True)
        elif current_selected_carrier_rvic:
            queryset = queryset.filter(xml_carrier_rvic=True, xml_carrier_ssic=False)
        elif current_selected_carrier_ssic:
            queryset = queryset.filter(xml_carrier_rvic=False, xml_carrier_ssic=True)
        # Si ninguno está seleccionado, no se aplica filtro de carrier (se muestran todos los que pasen los otros filtros)
        # Esto es porque el default es ambos seleccionados. Si el usuario los deselecciona ambos,
        # es ambiguo si quiere "ninguno con esos flags" o "no me importa el flag de carrier".
        # Aquí asumimos "no me importa".

        return _generate_generating_xml_csv(queryset,
                                            filename=f"generating_xml_report_{start_date_str}_to_{end_date_str}.csv")

    else:  # GET inicial
        context = {
            'status_filter_options': status_filter_options_for_template,
            'selected_statuses': current_selected_statuses,
            'xml_state_choices': XML_STATE_CHOICES,
            'selected_xml_states': current_selected_xml_states,
            'selected_carrier_rvic': current_selected_carrier_rvic,
            'selected_carrier_ssic': current_selected_carrier_ssic,
            'default_start_date': default_start_date.strftime('%Y-%m-%d'),
            'default_end_date': default_end_date.strftime('%Y-%m-%d'),
            'page_title': 'Compliance Report - Generating XML'
        }
        return render(request, 'tasks/compliance_xml_report.html', context)

@login_required
@user_passes_test(user_is_admin_or_leader)
def generate_revenue_support_report_view(request):
    today = timezone.localdate()
    default_start_date = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    default_end_date = today.replace(day=last_day)

    # Tipos de proceso relevantes para este reporte
    RELEVANT_PROCESS_TYPES_FOR_RS = [
        'address_validation', 'user_records', 'property_records',
        'unit_transfer', 'deactivation_toggle'
    ]
    relevant_process_types_choices = [(val, disp) for val, disp in TYPE_CHOICES if val in RELEVANT_PROCESS_TYPES_FOR_RS]

    # Opciones de estado para el filtro
    STATUS_OPTIONS_FOR_RS_FILTER_ORDER = [
        'scheduled', 'pending_approval', 'pending',
        'in_progress_group', 'blocked', 'completed', 'cancelled'
    ]
    STATUS_GROUP_MAPPING = {'in_progress_group': ['in_progress', 'qa_pending', 'qa_in_progress']}
    status_display_dict = dict(STATUS_CHOICES)
    status_filter_options_for_template = []
    for status_key in STATUS_OPTIONS_FOR_RS_FILTER_ORDER:
        display_name = "In Progress (includes QA stages)" if status_key == 'in_progress_group' else status_display_dict.get(
            status_key, status_key.title())
        status_filter_options_for_template.append({'value': status_key, 'display': display_name})

    # Estado inicial de los filtros para GET
    current_selected_statuses = request.GET.getlist('status')
    if not current_selected_statuses and not 'generate_csv' in request.GET:
        current_selected_statuses = [opt['value'] for opt in status_filter_options_for_template]

    current_selected_process_type = request.GET.get('type_of_process')
    current_selected_team_filter = request.GET.get('team_filter', 'both')  # Default a 'both'

    if request.method == 'GET' and 'generate_csv' in request.GET:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        # selected_statuses ya está en current_selected_statuses
        # selected_process_type ya está en current_selected_process_type
        # selected_team_filter ya está en current_selected_team_filter

        if not current_selected_process_type:
            messages.error(request, _("Process Type is required to generate the report."))
            # Re-renderizar el formulario
            context = {
                'relevant_process_types': relevant_process_types_choices,
                'selected_process_type': current_selected_process_type,
                'status_filter_options': status_filter_options_for_template,
                'selected_statuses': current_selected_statuses,
                'selected_team_filter': current_selected_team_filter,
                'TEAM_REVENUE_KEY': TEAM_REVENUE, 'TEAM_SUPPORT_KEY': TEAM_SUPPORT,  # Para el select de equipo
                'default_start_date': default_start_date.strftime('%Y-%m-%d'),
                'default_end_date': default_end_date.strftime('%Y-%m-%d'),
                'page_title': 'Revenue/Support Process Reports',
                'form_errors': {'type_of_process': "This field is required."}
            }
            return render(request, 'tasks/revenue_support_report_form.html', context)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else default_start_date
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else default_end_date
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            # Re-renderizar el formulario
            context = {
                'relevant_process_types': relevant_process_types_choices,
                'selected_process_type': current_selected_process_type,
                'status_filter_options': status_filter_options_for_template,
                'selected_statuses': current_selected_statuses,
                'selected_team_filter': current_selected_team_filter,
                'TEAM_REVENUE_KEY': TEAM_REVENUE, 'TEAM_SUPPORT_KEY': TEAM_SUPPORT,
                'default_start_date': default_start_date.strftime('%Y-%m-%d'),
                'default_end_date': default_end_date.strftime('%Y-%m-%d'),
                'page_title': 'Revenue/Support Process Reports'
            }
            return render(request, 'tasks/revenue_support_report_form.html', context)

        start_datetime_utc = timezone.make_aware(datetime.combine(start_date, time.min), pytz.utc)
        end_datetime_utc = timezone.make_aware(datetime.combine(end_date, time.max), pytz.utc)

        queryset = UserRecordsRequest.objects.filter(
            type_of_process=current_selected_process_type,  # Filtrar por el proceso seleccionado
            timestamp__gte=start_datetime_utc,
            timestamp__lte=end_datetime_utc
        ).select_related('requested_by', 'operator', 'qa_agent').order_by('-timestamp')

        # Aplicar filtro de estado
        final_status_filter_values = []
        if current_selected_statuses:
            for status_val in current_selected_statuses:
                if status_val in STATUS_GROUP_MAPPING:
                    final_status_filter_values.extend(STATUS_GROUP_MAPPING[status_val])
                elif status_val in status_display_dict:  # Asegurar que es una clave válida
                    final_status_filter_values.append(status_val)
            if final_status_filter_values:
                queryset = queryset.filter(status__in=list(set(final_status_filter_values)))

        # Aplicar filtro de Equipo
        if current_selected_team_filter == TEAM_REVENUE:
            queryset = queryset.filter(team=TEAM_REVENUE)
        elif current_selected_team_filter == TEAM_SUPPORT:
            queryset = queryset.filter(team=TEAM_SUPPORT)
        elif current_selected_team_filter == 'both':  # 'both' significa Revenue o Support
            queryset = queryset.filter(team__in=[TEAM_REVENUE, TEAM_SUPPORT])

        # Despachar a la función helper CSV correcta
        report_filename = f"{current_selected_process_type}_report_{start_date_str}_to_{end_date_str}.csv"
        if current_selected_process_type == 'user_records':
            return _generate_user_records_csv(queryset, filename=report_filename)
        elif current_selected_process_type == 'property_records':
            return _generate_property_records_csv(queryset, filename=report_filename)
        elif current_selected_process_type == 'unit_transfer':
            return _generate_unit_transfer_csv(queryset, filename=report_filename)
        elif current_selected_process_type == 'deactivation_toggle':
            return _generate_deactivation_toggle_csv(queryset, filename=report_filename)
        elif current_selected_process_type == 'address_validation':
            return _generate_address_validation_csv(queryset, filename=report_filename)
        else:
            messages.error(request,"Report generation for the selected process type is not yet implemented.")
            return redirect('tasks:revenue_support_report')


    else:  # GET inicial
        context = {
            'relevant_process_types': relevant_process_types_choices,
            'selected_process_type': current_selected_process_type,
            'status_filter_options': status_filter_options_for_template,
            'selected_statuses': current_selected_statuses,
            'selected_team_filter': current_selected_team_filter,
            'TEAM_REVENUE_KEY': TEAM_REVENUE,  # Pasar claves para los values del select de equipo
            'TEAM_SUPPORT_KEY': TEAM_SUPPORT,
            'default_start_date': default_start_date.strftime('%Y-%m-%d'),
            'default_end_date': default_end_date.strftime('%Y-%m-%d'),
            'page_title': 'Revenue/Support Process Reports'
        }
        return render(request, 'tasks/revenue_support_report.html', context)


def unassign_agent(request, pk):
    user_request = get_object_or_404(UserRecordsRequest, pk=pk)
    user = request.user

    # --- Lógica de Permisos ---
    is_admin_user = is_admin(user)
    can_unassign = False

    # Los líderes no pueden usar esta función
    if user_request.status == 'in_progress' and (user == user_request.operator or is_admin_user):
        can_unassign = True
    elif user_request.status == 'qa_in_progress' and (user == user_request.qa_agent or is_admin_user):
        can_unassign = True

    if not can_unassign:
        messages.error(request, _("You do not have permission to perform this action."))
        return redirect('tasks:request_detail', pk=pk)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                if user_request.status == 'in_progress':
                    # Desasignar Operador
                    unassigned_user_email = user_request.operator.email if user_request.operator else 'N/A'
                    user_request.status = 'pending'
                    user_request.operator = None
                    user_request.operated_at = None
                    # No se resetea effective_start_time_for_tat
                    user_request.save(update_fields=['status', 'operator', 'operated_at'])
                    logger.info(
                        f"User {user.email} unassigned operator ({unassigned_user_email}) from request {pk}. Status set to 'pending'.")
                    messages.success(request,
                                     _('Operator unassigned successfully. The request has been returned to the "Pending" queue.'))

                elif user_request.status == 'qa_in_progress':
                    # Desasignar Agente de QA
                    unassigned_qa_email = user_request.qa_agent.email if user_request.qa_agent else 'N/A'
                    user_request.status = 'qa_pending'
                    user_request.qa_agent = None
                    user_request.qa_in_progress_at = None
                    user_request.save(update_fields=['status', 'qa_agent', 'qa_in_progress_at'])
                    logger.info(
                        f"User {user.email} unassigned QA agent ({unassigned_qa_email}) from request {pk}. Status set to 'QA Pending'.")
                    messages.success(request,
                                     _('QA Agent unassigned successfully. The request has been returned to the "QA Pending" queue.'))

        except Exception as e:
            logger.error(f"Error trying to unassign agent for request {pk}: {e}", exc_info=True)
            messages.error(request, _("An unexpected error occurred. Please try again."))

    return redirect('tasks:request_detail', pk=pk)