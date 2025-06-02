# tasks/choices.py

"""
Este archivo centraliza las constantes utilizadas para las opciones
en los campos CharField de los modelos (atributo `choices`).
Esto mejora la mantenibilidad y la consistencia.
"""

# Tipos de procesos principales manejados por UserRecordsRequest
TYPE_CHOICES = [
    ('address_validation', 'Address Validation'),
    ('user_records', 'User Records'),
    ('property_records', 'Property Records'),
    ('unit_transfer', 'Unit Transfer'),
    ('deactivation_toggle', 'Deactivation and Toggle'),
    ('generating_xml', 'Generating XML files'),
    ('stripe_disputes', 'Stripe Disputes'),
]

TEAM_REVENUE = 'Revenue'
TEAM_SUPPORT = 'Support'
TEAM_COMPLIANCE = 'Compliance'
TEAM_ACCOUNTING = 'Accounting'
TEAM_LEADERSHIPS = 'Leaderships'

TEAM_CHOICES = [
    (TEAM_REVENUE, 'Revenue'),
    (TEAM_SUPPORT, 'Support'),
    (TEAM_COMPLIANCE, 'Compliance'),
    (TEAM_ACCOUNTING, 'Accounting'),
]
PRIORITY_LOW = 'low'
PRIORITY_NORMAL = 'normal'
PRIORITY_HIGH = 'high'

PRIORITY_CHOICES = [
    (PRIORITY_LOW, 'Low'),
    (PRIORITY_NORMAL, 'Normal'), # 'Normal' es el default
    (PRIORITY_HIGH, 'High'),
]
# Estados posibles para cualquier tipo de solicitud
STATUS_CHOICES = [
    ('scheduled', 'Scheduled'),
    ('pending_approval', 'Pending for Approval'),
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('qa_pending', 'QA Pending'),
    ('qa_in_progress', 'QA In Progress'),
    ('blocked', 'Blocked'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

# Opciones específicas para UserGroupForm (dentro de User Records)
REQUEST_TYPE_CHOICES = [
    ('add', 'Add User(s)'),
    ('edit', 'Edit Existing User(s)'),
    ('remove', 'Remove User(s)'),
]

# Niveles de acceso específicos para UserGroupForm
ACCESS_LEVEL_CHOICES = [
    ('property_manager', 'Property Manager'),
    ('property_manager_admin', 'Property Manager Admin'),
    ('listing_agent', 'Listing Agent'),
]

# Opciones específicas para Deactivation and Toggle Requests
DEACTIVATION_TOGGLE_CHOICES = [
    ('partner_deactivation', 'Partner Deactivation'),
    ('property_deactivation', 'Property Deactivation'),
    ('toggle_on_invites', 'Toggle on invites'),
    ('toggle_off_invites', 'Toggle off invites'),
    ('toggle_off_homepage_signups', 'Toggle off homepage sign-ups'),
    ('toggle_on_cash_deposits', 'Toggle on cash deposits'),
    ('toggle_off_cash_deposits', 'Toggle off cash deposits'),
]

# Opciones para la aprobación de Leadership en Deactivation/Toggle
LEADERSHIP_APPROVAL_CHOICES = [
    ('carolyn_walentisch', 'Carolyn Walentisch'),
    ('cristine_brown', 'Cristine Brown'),
    ('shay_chang', 'Shay Chang'),
    ('chelsea_strickland', 'Chelsea Strickland'),
]

# Opciones específicas para Unit Transfer Requests
UNIT_TRANSFER_TYPE_CHOICES = [
    ('partner_to_prospect', 'Partner to Prospect'),
    ('partner_to_partner', 'Partner to Partner'),
]

# Tipos de Landlord para Unit Transfer (Prospect)
UNIT_TRANSFER_LANDLORD_TYPE_CHOICES = [
    ('owner', 'Owner'),
    ('3rd_party_manager', '3rd Party Manager'),
    ('owner_manager', 'Owner-Manager'),
    ('broker', 'Broker'),
    ('vendor', 'Vendor'),
    ('reit', 'REIT'),
    ('other', 'Other'),
]

# Estados para la generación de XML
XML_STATE_CHOICES = [
    ('CA', 'CA'), ('CO', 'CO'), ('FL', 'FL'), ('GA', 'GA'), ('IL', 'IL'),
    ('MN', 'MN'), ('MS', 'MS'), ('NC', 'NC'), ('NJ', 'NJ'), ('OK', 'OK'),
    ('SC', 'SC'), ('TX', 'TX'), ('UT', 'UT'), ('WA', 'WA'),
]

PROPERTY_RECORDS_TYPE_CHOICES = [
    ('property_name', 'Property Name'),
    ('property_management_company', 'Property Management Company'),
    ('property_legal_entity', 'Property Legal Entity'),
    ('address', 'Address'),
    ('property_type', 'Property Type'),
    ('property_units', 'Property Units'),
    ('coverage_type_amount', 'Coverage Type/Amount'),
    ('integration_code', 'Integration Code'),
    ('banking_information', 'Banking Information'),
]

PROPERTY_TYPE_CHOICES = [
    ('single_family', 'Single-Family'),
    ('garden_community', 'Garden-Community'),
    ('multifamily', 'Multifamily'),
]

COVERAGE_TYPE_CHOICES = [
    ('multiplier', 'Multiplier'),
    ('amount', 'Amount'),
]

COVERAGE_MULTIPLIER_CHOICES = [
    ('0.5', '0.5x'),
    ('1.0', '1x'),
    ('1.5', '1.5x'),
    ('2.0', '2x'),
    ('2.5', '2.5x'),
    ('3.0', '3x'),
    ('4.0', '4x'),
    ('5.0', '5x'),
    ('6.0', '6x'),
]

INTEGRATION_TYPE_CHOICES = [
    ('yardi', 'Yardi'),
    ('realpage', 'RealPage'),
    ('udr', 'UDR'),
    ('rent_manager', 'Rent Manager'),
    ('mri', 'MRI'),
    ('entrata', 'Entrata'),
    ('eqr', 'EQR'),
]

EVENT_KEY_NEW_REQUEST_CREATED = 'new_request_created'
EVENT_KEY_REQUEST_PENDING_APPROVAL = 'request_pending_approval'
EVENT_KEY_REQUEST_APPROVED = 'request_approved'
EVENT_KEY_SCHEDULED_REQUEST_ACTIVATED = 'scheduled_request_activated'
EVENT_KEY_UPDATE_REQUESTED = 'update_requested'
EVENT_KEY_UPDATE_PROVIDED = 'update_provided'
EVENT_KEY_REQUEST_BLOCKED = 'request_blocked'
EVENT_KEY_REQUEST_RESOLVED = 'request_resolved'
EVENT_KEY_REQUEST_SENT_TO_QA = 'request_sent_to_qa'
EVENT_KEY_REQUEST_REJECTED = 'request_rejected'
EVENT_KEY_REQUEST_CANCELLED = 'request_cancelled'
EVENT_KEY_REQUEST_UNCANCELLED = 'request_uncancelled'
EVENT_KEY_REQUEST_COMPLETED = 'request_completed'

# El diccionario ALL_NOTIFICATION_EVENT_KEYS es útil para apps.py
ALL_NOTIFICATION_EVENT_KEYS = {
    EVENT_KEY_NEW_REQUEST_CREATED: '1. Nueva Solicitud Creada (Manual y Salesforce)',
    EVENT_KEY_REQUEST_PENDING_APPROVAL: '2. Solicitud (Deactivation) Pendiente de Aprobación',
    EVENT_KEY_REQUEST_APPROVED: '3. Solicitud (Deactivation) Aprobada',
    EVENT_KEY_SCHEDULED_REQUEST_ACTIVATED: '4. Solicitud Programada Activada (a Pendiente)',
    EVENT_KEY_UPDATE_REQUESTED: '5. Actualización Solicitada para una Tarea',
    EVENT_KEY_UPDATE_PROVIDED: '6. Actualización Provista para una Tarea',
    EVENT_KEY_REQUEST_BLOCKED: '7. Solicitud Bloqueada',
    EVENT_KEY_REQUEST_RESOLVED: '8. Solicitud Bloqueada Resuelta',
    EVENT_KEY_REQUEST_SENT_TO_QA: '9. Solicitud Enviada a QA',
    EVENT_KEY_REQUEST_REJECTED: '10. Solicitud Rechazada desde QA/Admin',
    EVENT_KEY_REQUEST_CANCELLED: '11. Solicitud Cancelada',
    EVENT_KEY_REQUEST_UNCANCELLED: '12. Solicitud Descancelada',
    EVENT_KEY_REQUEST_COMPLETED: '13. Solicitud Completada',
}