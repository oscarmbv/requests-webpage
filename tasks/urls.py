# tasks/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'tasks'

urlpatterns = [
    # URLs movidas desde el archivo principal, relativas a 'portal/'
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.portal_operations_dashboard, name='rhino_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('manage_prices/', views.manage_prices, name='manage_prices'),
    path('cost_summary/', views.client_cost_summary_view, name='client_cost_summary'),

    # Creación de Requests
    path('create/', views.choose_request_type, name='choose_request_type'),
    path('create/user_records/', views.user_records_request, name='user_records_request'),
    path('create/deactivation_toggle/', views.deactivation_toggle_request, name='deactivation_toggle_request'),
    path('create/unit_transfer/', views.unit_transfer_request, name='unit_transfer_request'),
    path('create/generating_xml/', views.generating_xml_request, name='generating_xml_request'),
    path('create/address_validation/', views.address_validation_request, name='address_validation_request'),
    path('create/stripe_disputes/', views.stripe_disputes_request, name='stripe_disputes_request'),
    path('create/property_records/', views.property_records_request, name='property_records_request'),

    # --- NUEVAS URLs PARA REPORTES ---
    path('reports/revenue_support/', views.generate_revenue_support_report_view, name='revenue_support_report'),
    path('reports/compliance_xml/', views.generate_compliance_xml_report_view, name='compliance_xml_report'),
    path('reports/accounting_stripe/', views.generate_accounting_stripe_report_view, name='accounting_stripe_report'),

    # Detalles y Acciones de Request
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/<int:pk>/operate/', views.operate_request, name='operate_request'),
    path('request/<int:pk>/block/', views.block_request, name='block_request'),
    path('request/<int:pk>/send_to_qa/', views.send_to_qa_request, name='send_to_qa_request'),
    path('request/<int:pk>/qa/', views.qa_request, name='qa_request'),
    path('request/<int:pk>/complete/', views.complete_request, name='complete_request'),
    path('request/<int:pk>/cancel/', views.cancel_request, name='cancel_request'),
    path('request/<int:pk>/resolve/', views.resolve_request, name='resolve_request'),
    path('request/<int:pk>/reject/', views.reject_request, name='reject_request'),
    path('request/<int:pk>/approve_deactivation_toggle/', views.approve_deactivation_toggle, name='approve_deactivation_toggle'),
    path('request/<int:pk>/set_update_flag/', views.set_update_needed_flag, name='set_update_flag'),
    path('request/<int:pk>/clear_update_flag/', views.clear_update_needed_flag, name='clear_update_flag'),
    path('request/<int:pk>/uncancel/', views.uncancel_request, name='uncancel_request'),
    path('request/<int:pk>/unassign/', views.unassign_agent, name='unassign_agent'),
]