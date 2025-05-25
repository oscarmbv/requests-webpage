# tasks/choices.py

"""
Este archivo centraliza las constantes utilizadas para las opciones
en los campos CharField de los modelos (atributo `choices`).
Esto mejora la mantenibilidad y la consistencia.
"""

# Tipos de procesos principales manejados por UserRecordsRequest
TYPE_CHOICES = [
    ('user_records', 'User Records'),
    ('deactivation_toggle', 'Deactivation and Toggle'),
    ('unit_transfer', 'Unit Transfer'),
    ('generating_xml', 'Generating XML files'),
    ('address_validation', 'Address Validation'),
    ('stripe_disputes', 'Stripe Disputes'),
    ('property_records', 'Property Records'),
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
    ('pending', 'Pending'),                 # Solicitud creada, esperando acción
    ('scheduled', 'Scheduled'),             # Solicitud programada para una fecha/hora futura
    ('in_progress', 'In Progress'),         # Agente ha comenzado a trabajar
    ('completed', 'Completed'),             # Proceso finalizado exitosamente
    ('cancelled', 'Cancelled'),             # Solicitud cancelada
    ('blocked', 'Blocked'),                 # Bloqueada, esperando resolución
    ('pending_approval', 'Pending for Approval'), # Específico para Deactivation/Toggle, esperando aprobación de Leadership
    ('qa_pending', 'QA Pending'),           # Enviado a QA, esperando que un agente QA lo tome
    ('qa_in_progress', 'QA In Progress'),   # Agente QA está revisando
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