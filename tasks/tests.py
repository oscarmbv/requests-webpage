# tasks/tests.py

from django.test import TestCase, Client # Client para probar vistas
from django.urls import reverse # Para obtener URLs por su nombre
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserRecordsRequest, BlockedMessage, CustomUser, OperationPrice # Importa tus modelos
from .forms import UserRecordsRequestForm, UserGroupForm, BlockForm # Importa tus formularios
from django.contrib.auth.models import Group

# Obtiene el modelo de usuario personalizado
User = get_user_model()

class TaskModelTests(TestCase):
    """Pruebas para los modelos de la aplicación tasks."""

    def setUp(self):
        """Configuración inicial para las pruebas de modelos."""
        # Crear usuarios de prueba
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='password123'
        )
        # Podrías crear más usuarios con diferentes roles si es necesario

    def test_user_creation(self):
        """Verifica que el CustomUser se crea correctamente."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_records_request_creation(self):
        """Verifica la creación de UserRecordsRequest y la generación de unique_code."""
        request_obj = UserRecordsRequest.objects.create(
            requested_by=self.user,
            partner_name="Test Partner",
            type_of_process='user_records',
            # Añade otros campos necesarios si los hay
        )
        self.assertIsNotNone(request_obj.unique_code)
        self.assertTrue(request_obj.unique_code.startswith('User-')) # Verifica el prefijo
        self.assertEqual(request_obj.status, 'pending') # Verifica estado inicial

    def test_unique_code_increment(self):
        """Verifica que los unique_code se incrementen correctamente."""
        req1 = UserRecordsRequest.objects.create(requested_by=self.user, partner_name="P1", type_of_process='user_records')
        req2 = UserRecordsRequest.objects.create(requested_by=self.user, partner_name="P2", type_of_process='user_records')
        # Extraer números de secuencia y comparar (requiere parseo cuidadoso)
        try:
            seq1 = int(req1.unique_code.split('Q')[-1])
            seq2 = int(req2.unique_code.split('Q')[-1])
            self.assertEqual(seq2, seq1 + 1)
        except (ValueError, IndexError):
            self.fail("Could not parse sequence number from unique_code")

    # --- Añade más pruebas para otros modelos ---
    # test_blocked_message_creation(...)
    # test_operation_price_singleton(...)


class TaskViewTests(TestCase):
    """Pruebas para las vistas de la aplicación tasks."""

    def setUp(self):
        """Configuración para pruebas de vistas."""
        # Crea usuarios con diferentes roles
        self.client = Client()
        self.user_regular = User.objects.create_user(username='regular', email='regular@example.com', password='password')
        self.agent_user = User.objects.create_user(username='agent', email='agent@example.com', password='password')
        self.leadership_user = User.objects.create_user(username='leader', email='leader@example.com', password='password')
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')

        # Crea grupos si no existen y añade usuarios
        agent_group, _ = Group.objects.get_or_create(name='Agents')
        leadership_group, _ = Group.objects.get_or_create(name='Leaderships')
        self.agent_user.groups.add(agent_group)
        self.leadership_user.groups.add(leadership_group)

        # Crear un request de ejemplo
        self.test_request = UserRecordsRequest.objects.create(
            requested_by=self.user_regular, partner_name="ViewTestPartner", type_of_process='user_records'
        )

    def test_dashboard_unauthenticated(self):
        """Verifica que el dashboard redirija al login si no está autenticado."""
        response = self.client.get(reverse('tasks:portal_dashboard'))
        self.assertEqual(response.status_code, 302) # 302 Found (redirección)
        self.assertIn(reverse('login'), response.url) # Verifica que redirija a login

    def test_dashboard_authenticated(self):
        """Verifica que un usuario autenticado pueda ver el dashboard."""
        self.client.login(email='regular@example.com', password='password')
        response = self.client.get(reverse('tasks:portal_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/portal_operations_dashboard.html')

    def test_request_detail_permission(self):
        """Verifica los permisos para ver detalles de un request."""
        # Usuario regular (creador) sí puede ver
        self.client.login(email='regular@example.com', password='password')
        response = self.client.get(reverse('tasks:request_detail', args=[self.test_request.pk]))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Otro usuario regular no puede ver
        other_user = User.objects.create_user(username='other', email='other@example.com', password='password')
        self.client.login(email='other@example.com', password='password')
        response = self.client.get(reverse('tasks:request_detail', args=[self.test_request.pk]))
        self.assertEqual(response.status_code, 302) # Redirige porque no tiene permiso
        self.assertRedirects(response, reverse('tasks:portal_dashboard')) # O a donde redirija el error de permiso
        self.client.logout()

        # Agente sí puede ver
        self.client.login(email='agent@example.com', password='password')
        response = self.client.get(reverse('tasks:request_detail', args=[self.test_request.pk]))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_user_records_create_view_post(self):
        """Prueba la creación de un User Records Request vía POST."""
        self.client.login(email='regular@example.com', password='password')
        form_data = {
            'partner_name': 'New Partner From Test',
            'special_instructions': 'Test instructions',
            # Datos del formset (requiere manejo especial del prefijo 'groups')
            'groups-TOTAL_FORMS': '1',
            'groups-INITIAL_FORMS': '0',
            'groups-MIN_NUM_FORMS': '1',
            'groups-MAX_NUM_FORMS': '1000',
            'groups-0-type_of_request': 'add',
            'groups-0-user_email_addresses': 'newuser@test.com',
            'groups-0-access_level': 'property_manager',
            'groups-0-properties': 'TestProp1',
        }
        response = self.client.post(reverse('tasks:user_records_request'), data=form_data)
        # Verificar redirección exitosa
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks:portal_dashboard'))
        # Verificar que el objeto se creó en la BD
        self.assertTrue(UserRecordsRequest.objects.filter(partner_name='New Partner From Test').exists())
        new_request = UserRecordsRequest.objects.get(partner_name='New Partner From Test')
        self.assertEqual(new_request.requested_by, self.user_regular)
        self.assertEqual(new_request.user_groups_data[0]['user_email_addresses'], ['newuser@test.com'])

    # --- Añade más pruebas para otras vistas ---
    # test_deactivation_create_view(...)
    # test_operate_action(...)
    # test_block_action(...)
    # test_resolve_action(...)
    # test_qa_flow(...)
    # test_cancel_action_permissions(...)
    # test_reject_action_permissions(...)
    # test_approve_action_permissions(...)
    # test_manage_prices_access(...)

class TaskFormTests(TestCase):
    """Pruebas para los formularios de la aplicación tasks."""

    def test_user_group_form_valid(self):
        """Prueba un caso válido del UserGroupForm."""
        form_data = {
            'type_of_request': 'add',
            'user_email_addresses': 'test1@example.com, test2@example.com',
            'access_level': 'property_manager',
            'properties': 'PropA, PropB',
        }
        form = UserGroupForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Verifica la limpieza de emails/properties
        self.assertEqual(form.cleaned_data['user_email_addresses'], ['test1@example.com', 'test2@example.com'])
        self.assertEqual(form.cleaned_data['properties'], ['PropA', 'PropB'])

    def test_user_group_form_remove_no_access_level(self):
        """Prueba que access_level no sea requerido para 'remove'."""
        form_data = {
            'type_of_request': 'remove',
            'user_email_addresses': 'remove@example.com',
            'properties': 'PropC',
            # No access_level
        }
        form = UserGroupForm(data=form_data)
        # Nota: La lógica required está en __init__, is_valid la considera
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data.get('access_level')) # No debería estar o ser None/vacío

    def test_user_group_form_invalid_email(self):
        """Prueba un email inválido en UserGroupForm."""
        form_data = {
            'type_of_request': 'add',
            'user_email_addresses': 'invalid-email',
            'access_level': 'property_manager',
            'properties': 'PropD',
        }
        form = UserGroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('user_email_addresses', form.errors)

    # --- Añade más pruebas para otros formularios y casos ---
    # test_user_records_request_form_file_or_link(...)
    # test_deactivation_form_conditional_required(...)
    # test_unit_transfer_form_conditional_required(...)
    # test_generating_xml_form_conditional_required(...)
    # test_resolve_form_file_and_link_error(...)