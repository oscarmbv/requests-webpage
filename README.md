# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** Analizado el 28 de mayo de 2025
**Fecha de Actualización del README:** 28 de mayo de 2025
**Documento de Referencia Principal:** "Descripción Detallada de la Plataforma de Gestión de Solicitudes (requests_webpage)" v2.3 (20 de mayo de 2025)

## Tabla de Contenidos
1.  [Introducción y Propósito](#1-introducción-y-propósito)
2.  [Estructura Detallada del Proyecto](#2-estructura-detallada-del-proyecto)
3.  [Configuración Central del Proyecto (`requests_webpage/settings.py`)](#3-configuración-central-del-proyecto-requests_webpagesettingspy)
    * [3.1. Variables Esenciales de Seguridad y Despliegue](#31-variables-esenciales-de-seguridad-y-despliegue)
    * [3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)](#32-aplicaciones-instaladas-installed_apps)
    * [3.3. Middleware](#33-middleware)
    * [3.4. Modelo de Usuario Personalizado (`AUTH_USER_MODEL`)](#34-modelo-de-usuario-personalizado-auth_user_model)
    * [3.5. Configuración de la Base de Datos (`DATABASES`)](#35-configuración-de-la-base-de-datos-databases)
    * [3.6. Gestión de Archivos Estáticos y Multimedia](#36-gestión-de-archivos-estáticos-y-multimedia)
    * [3.7. Internacionalización (i18n) y Localización (l10n)](#37-internacionalización-i18n-y-localización-l10n)
    * [3.8. Configuración de Tareas en Segundo Plano (Django-Q2)](#38-configuración-de-tareas-en-segundo-plano-django-q2)
    * [3.9. Configuración de Salesforce](#39-configuración-de-salesforce)
    * [3.10. Logging](#310-logging)
    * [3.11. Redirecciones y Otros Ajustes](#311-redirecciones-y-otros-ajustes)
4.  [Enrutamiento de URLs](#4-enrutamiento-de-urls)
    * [4.1. Enrutamiento Principal (`requests_webpage/urls.py`)](#41-enrutamiento-principal-requests_webpageurlspy)
    * [4.2. Enrutamiento de la Aplicación `tasks` (`tasks/urls.py`)](#42-enrutamiento-de-la-aplicación-tasks-tasksurlspy)
5.  [Modelo de Datos Detallado (`tasks/models.py`)](#5-modelo-de-datos-detallado-tasksmodelspy)
    * [5.1. `CustomUser(AbstractUser)`](#51-customuserabstractuser)
    * [5.2. `UserRecordsRequest(models.Model)`](#52-userrecordsrequestmodelsmodel)
        * [5.2.1. Campos Generales y de Identificación](#521-campos-generales-y-de-identificación)
        * [5.2.2. Campos de Flujo de Trabajo y Asignación](#522-campos-de-flujo-de-trabajo-y-asignación)
        * [5.2.3. Campos de Detalles de Operación/QA (Comunes)](#523-campos-de-detalles-de-operaciónqa-comunes)
        * [5.2.4. Campos Específicos por `type_of_process`](#524-campos-específicos-por-type_of_process)
        * [5.2.5. Campos para Integración con Salesforce](#525-campos-para-integración-con-salesforce)
        * [5.2.6. Campos para Costos Calculados en Finalización](#526-campos-para-costos-calculados-en-finalización)
        * [5.2.7. Métodos y Propiedades del Modelo](#527-métodos-y-propiedades-del-modelo)
        * [5.2.8. Clase Meta (UserRecordsRequest)](#528-clase-meta-userrecordsrequest)
    * [5.3. `AddressValidationFile(models.Model)`](#53-addressvalidationfilemodelsmodel)
    * [5.4. Modelos de Historial (`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`)](#54-modelos-de-historial-blockedmessage-resolvedmessage-rejectedmessage)
    * [5.5. `OperationPrice(models.Model)`](#55-operationpricemodelsmodel)
    * [5.6. `SalesforceAttachmentLog(models.Model)`](#56-salesforceattachmentlogmodelsmodel)
    * [5.7. `ScheduledTaskToggle(models.Model)`](#57-scheduledtasktogglemodelsmodel)
6.  [Archivo de Opciones (`tasks/choices.py`)](#6-archivo-de-opciones-taskschoicespy)
7.  [Validadores Personalizados (`tasks/validators.py`)](#7-validadores-personalizados-tasksvalidatorspy)
8.  [Formularios Detallados (`tasks/forms.py`)](#8-formularios-detallados-tasksformspy)
    * [8.1. Formularios de Usuario](#81-formularios-de-usuario)
    * [8.2. `UserGroupForm(forms.Form)`](#82-usergroupformformsform)
    * [8.3. `UserRecordsRequestForm(forms.Form)`](#83-userrecordsrequestformformsform)
    * [8.4. Formularios de Acción Simples (`BlockForm`, `ResolveForm`, `RejectForm`)](#84-formularios-de-acción-simples-blockform-resolveform-rejectform)
    * [8.5. `OperateForm(forms.ModelForm)`](#85-operateformformsmodelform)
    * [8.6. `OperationPriceForm(forms.ModelForm)`](#86-operationpriceformformsmodelform)
    * [8.7. Formularios Específicos por Tipo de Proceso](#87-formularios-específicos-por-tipo-de-proceso)
        * [8.7.1. `DeactivationToggleRequestForm`](#871-deactivationtogglerequestform)
        * [8.7.2. `UnitTransferRequestForm`](#872-unittransferrequestform)
        * [8.7.3. `GeneratingXmlRequestForm`](#873-generatingxmlrequestform)
        * [8.7.4. `AddressValidationRequestForm`](#874-addressvalidationrequestform)
        * [8.7.5. `StripeDisputesRequestForm`](#875-stripedisputesrequestform)
        * [8.7.6. `PropertyRecordsRequestForm`](#876-propertyrecordsrequestform)
        * [8.7.7. `GeneratingXmlOperateForm`](#877-generatingxmloperateform)
9.  [Vistas Detalladas (`tasks/views.py`)](#9-vistas-detalladas-tasksviewspy)
    * [9.1. Funciones Auxiliares de Permisos](#91-funciones-auxiliares-de-permisos)
    * [9.2. Vistas Generales y de Autenticación](#92-vistas-generales-y-de-autenticación)
    * [9.3. Vistas de Creación de Solicitudes](#93-vistas-de-creación-de-solicitudes)
    * [9.4. Vistas de Dashboard y Detalles de Solicitud](#94-vistas-de-dashboard-y-detalles-de-solicitud)
    * [9.5. Vistas de Acciones de Flujo de Trabajo](#95-vistas-de-acciones-de-flujo-de-trabajo)
    * [9.6. Vista de Administración de Precios](#96-vista-de-administración-de-precios)
10. [Plantillas Detalladas (`tasks/templates/tasks/`)](#10-plantillas-detalladas-taskstemplatestasks)
    * [10.1. Plantilla Base (`base.html`)](#101-plantilla-base-basehtml)
    * [10.2. Plantillas de Páginas Generales y Autenticación](#102-plantillas-de-páginas-generales-y-autenticación)
    * [10.3. Plantillas de Creación de Solicitudes](#103-plantillas-de-creación-de-solicitudes)
    * [10.4. Plantilla del Dashboard (`portal_operations_dashboard.html`)](#104-plantilla-del-dashboard-portal_operations_dashboardhtml)
    * [10.5. Plantillas de Detalle de Solicitud (Genéricas y Específicas)](#105-plantillas-de-detalle-de-solicitud-genéricas-y-específicas)
    * [10.6. Plantillas de Formularios de Acción Simples](#106-plantillas-de-formularios-de-acción-simples)
11. [Lógica de Tareas en Segundo Plano (Django-Q2)](#11-lógica-de-tareas-en-segundo-plano-django-q2)
    * [11.1. Activación de Solicitudes Programadas (`tasks/scheduled_jobs.py`)](#111-activación-de-solicitudes-programadas-tasksscheduled_jobspy)
    * [11.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)](#112-sincronización-con-salesforce-taskssalesforce_syncpy)
    * [11.3. Configuración y Ejecución del Cluster (`tasks/apps.py`)](#113-configuración-y-ejecución-del-cluster-tasksappspy)
12. [Administración de Django (`tasks/admin.py`)](#12-administración-de-django-tasksadminpy)
13. [Configuración del Entorno de Desarrollo](#13-configuración-del-entorno-de-desarrollo)
14. [Despliegue (Heroku)](#14-despliegue-heroku)
15. [Próximos Pasos y Mejoras Futuras](#15-próximos-pasos-y-mejoras-futuras)

---

## 1. Introducción y Propósito

`requests_webpage` es una aplicación web integral construida sobre el framework Django. Su propósito fundamental es servir como una plataforma centralizada y eficiente para la gestión de una variedad de solicitudes y procesos operativas internas. La aplicación está diseñada para ser altamente personalizable, permitiendo la definición de diferentes tipos de solicitudes, cada una con sus propios flujos de trabajo, campos de datos específicos, y lógicas de asignación a los equipos responsables.

Las características clave incluyen la creación y seguimiento de solicitudes, asignación a operadores y agentes de QA, gestión de estados (desde 'pendiente' hasta 'completado', incluyendo 'bloqueado', 'programado', etc.), un sistema de priorización, la capacidad de adjuntar archivos o enlaces, y un historial detallado de acciones por solicitud. Funcionalidades avanzadas como la programación de solicitudes para activación futura, el cálculo de Tiempos de Respuesta (Turn Around Time - TAT) y la **integración funcional con Salesforce para la creación automatizada de solicitudes de "Address Validation"** mejoran la planificación y el monitoreo de la eficiencia operativa. Adicionalmente, se ha implementado un sistema para el cálculo y almacenamiento de costos asociados a cada solicitud al momento de su finalización.

La plataforma utiliza `django-q2` para la gestión de tareas en segundo plano y programadas, asegurando que procesos como la activación de solicitudes o la sincronización con Salesforce no bloqueen la interfaz de usuario y se ejecuten de manera fiable. También se ha incorporado un mecanismo para pausar/reanudar tareas programadas (como la sincronización con Salesforce) desde el panel de administración.

---

## 2. Estructura Detallada del Proyecto
*(Esta sección se mantiene similar a la versión anterior del README, ya que la estructura de archivos principal no ha cambiado drásticamente. Se asume que los archivos mencionados como `salesforce_sync.py` y `scheduled_jobs.py` existen y están poblados como se describe en secciones posteriores).*

El proyecto `requests_webpage` sigue la estructura estándar de una aplicación Django, diseñada para la gestión de procesos internos.

* **`requests_webpage/`**: Directorio raíz del proyecto Django.
    * `settings.py`: Configuración global del proyecto (ver sección 3.1).
    * `urls.py`: Enrutamiento principal de URLs (ver sección 4.1).
    * `wsgi.py`, `asgi.py`: Interfaces estándar para despliegue.
* **`tasks/`**: Aplicación Django principal donde reside la lógica de negocio y gestión de solicitudes.
    * `models.py`: Define los modelos de la base de datos (ver sección 5).
    * `views.py`: Contiene la lógica de las vistas (ver sección 9).
    * `forms.py`: Define los formularios Django (ver sección 8).
    * `urls.py`: Enrutamiento específico de la aplicación `tasks` (ver sección 4.2).
    * `admin.py`: Configuración del sitio de administración de Django (ver sección 12).
    * `choices.py`: Define las opciones para los campos `ChoiceField` (ver sección 6).
    * `validators.py`: Validadores personalizados (ver sección 7).
    * `scheduled_jobs.py`: Lógica para tareas programadas (ej. activación de solicitudes) (ver sección 11.1).
    * `salesforce_sync.py`: Lógica para la integración con Salesforce (ver sección 11.2).
    * `templatetags/`: Contiene `duration_filters.py` para formatear `timedelta` en plantillas.
    * `templates/tasks/`: Plantillas HTML para la interfaz de usuario (ver sección 10).
    * `static/tasks/`: Archivos estáticos (CSS, JS) de la aplicación.
    * `migrations/`: Migraciones de base de datos.
    * `apps.py`: Configuración de la aplicación `tasks` e inicialización de tareas programadas `django-q2` (ver sección 11.3).
* `manage.py`: Utilidad de línea de comandos de Django.
* `.env`: (No versionado en Git) Almacena variables de entorno.
* `requirements.txt`: Lista las dependencias de Python.
* `README.md`: Este archivo.
* (`yender.yaml` fue eliminado en preparación para Heroku).

---
## 3. Configuración Central del Proyecto (`requests_webpage/settings.py`)
*(Esta sección se mantiene muy similar a la descripción anterior, ya que los fundamentos de `settings.py` son estables. Se enfatizan los puntos relevantes para las funcionalidades actuales).*

El archivo `requests_webpage/settings.py` contiene las configuraciones esenciales.

### 3.1. Variables Esenciales de Seguridad y Despliegue
* **`SECRET_KEY`**: Clave criptográfica, cargada desde `django-environ`.
* **`DEBUG`**: Booleano para modo depuración, cargado desde `django-environ`.
* **`ALLOWED_HOSTS`**: Lista de dominios permitidos.
* **`CSRF_TRUSTED_ORIGINS`**: Orígenes confiables para solicitudes seguras.

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)
Incluye `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `'whitenoise.runserver_nostatic'`, `django.contrib.staticfiles`, la aplicación principal `tasks`, y `django_q` para tareas en segundo plano.

### 3.3. Middleware
Capas de procesamiento que incluyen `SecurityMiddleware`, `WhiteNoiseMiddleware`, `SessionMiddleware`, `CommonMiddleware`, `CsrfViewMiddleware`, `AuthenticationMiddleware`, `MessageMiddleware`, `ClickjackingXFrameOptionsMiddleware`, y `LocaleMiddleware` para internacionalización.

### 3.4. Modelo de Usuario Personalizado (`AUTH_USER_MODEL`)
* `AUTH_USER_MODEL = 'tasks.CustomUser'` especifica el uso del modelo `CustomUser` de la aplicación `tasks`.

### 3.5. Configuración de la Base de Datos (`DATABASES`)
* Utiliza `dj_database_url.config()` para flexibilidad, con SQLite como fallback local.

### 3.6. Gestión de Archivos Estáticos y Multimedia
* `STATIC_URL`, `STATIC_ROOT`, y `STATICFILES_STORAGE` (con `whitenoise.storage.CompressedManifestStaticFilesStorage`) para archivos estáticos.
* `MEDIA_URL` y `MEDIA_ROOT` para archivos subidos por usuarios.

### 3.7. Internacionalización (i18n) y Localización (l10n)
* `LANGUAGE_CODE = 'en-us'`, `TIME_ZONE = 'UTC'`, `USE_I18N = True`, `USE_TZ = True`.

### 3.8. Configuración de Tareas en Segundo Plano (Django-Q2)
* `Q_CLUSTER`: Configuración detallada para `django-q2` incluyendo `name`, `workers`, `timeout`, `retry`, `orm`, `catch_up: False`, y `log_level`.

### 3.9. Configuración de Salesforce
* Credenciales (`SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, etc.) cargadas vía `django-environ`.
* `SALESFORCE_LIGHTNING_BASE_URL` construida dinámicamente.

### 3.10. Logging
* Configuración `LOGGING` con formateadores `verbose` y `simple`, y manejadores `console` y `file_tasks`. Loggers específicos para `django`, `django.request`, `tasks`, y `django_q`.

### 3.11. Redirecciones y Otros Ajustes
* `LOGOUT_REDIRECT_URL`, `LOGIN_REDIRECT_URL`.
* Configuraciones de seguridad para producción (ej. `SECURE_PROXY_SSL_HEADER`, `SECURE_SSL_REDIRECT`) activadas si `DEBUG` es `False`.

---
## 4. Enrutamiento de URLs

### 4.1. Enrutamiento Principal (`requests_webpage/urls.py`)
* `/admin/`: Sitio de administración.
* `/accounts/`: URLs de autenticación de Django.
* `/portal/`: Incluye `tasks.urls` con namespace `tasks`.
* Ruta raíz (`/`): Vista `home` de `tasks`.
* Servicio de media en desarrollo.

### 4.2. Enrutamiento de la Aplicación `tasks` (`tasks/urls.py`)
Define rutas específicas bajo `/portal/`:
* **Autenticación:** `accounts/login/`, `accounts/logout/`.
* **Vistas Principales:** `dashboard/`, `profile/`, `manage_prices/`.
* **Creación de Solicitudes:** `create/`, `create/user_records/`, `create/deactivation_toggle/`, etc., para todos los tipos de solicitud.
* **Detalle y Acciones:** `request/<int:pk>/` y sub-rutas para `operate`, `block`, `send_to_qa`, `qa`, `complete`, `cancel`, `resolve`, `reject`, `approve_deactivation_toggle`, `set_update_flag`, `clear_update_flag`, `uncancel`.

---
## 5. Modelo de Datos Detallado (`tasks/models.py`)


### 5.1. `CustomUser(AbstractUser)`
* **`email`**: `EmailField(unique=True)`, es el `USERNAME_FIELD`.
* **`timezone`**: `CharField` con `pytz.common_timezones` como `choices`, default 'UTC'.
* **`REQUIRED_FIELDS = ['username']`**.

### 5.2. `UserRecordsRequest(models.Model)`
Modelo central para todas las solicitudes.

#### 5.2.1. Campos Generales y de Identificación
* `type_of_process`: `CharField` con `TYPE_CHOICES` (ej. 'user\_records', 'address\_validation'), indexado.
* `unique_code`: `CharField` único, no editable, generado automáticamente.
* `timestamp`: `DateTimeField` de creación, `default=now`, indexado.
* `requested_by`: `ForeignKey` a `CustomUser`.
* `team`: `CharField` con `TEAM_CHOICES`, opcional, indexado.
* `priority`: `CharField` con `PRIORITY_CHOICES`, default `PRIORITY_NORMAL`, indexado.
* `partner_name`: `CharField`, opcional, indexado.
* `properties`: `TextField` genérico para propiedades afectadas.
* `user_groups_data`: `JSONField` para datos de "User Records".
* `special_instructions`: `TextField`.
* `status`: `CharField` con `STATUS_CHOICES`, default 'pending', indexado.
* `update_needed_flag`: `BooleanField` para solicitar actualizaciones.
* `update_requested_by`: `ForeignKey` a `CustomUser`.
* `update_requested_at`: `DateTimeField`.
* `user_file`: `FileField` con `validate_file_size`.
* `user_link`: `URLField`.

#### 5.2.2. Campos de Flujo de Trabajo y Asignación
* `operator`, `qa_agent`: `ForeignKey` a `CustomUser`.
* Timestamps: `operated_at`, `qa_pending_at`, `qa_in_progress_at`, `completed_at`, `cancelled_at`.
* `cancel_reason`, `cancelled_by`, `uncanceled_at`, `uncanceled_by`.
* `scheduled_date`: `DateField` para programación.
* `effective_start_time_for_tat`: `DateTimeField` para inicio del cálculo de TAT.
* `is_rejected_previously`: `BooleanField`.

#### 5.2.3. Campos de Detalles de Operación/QA (Comunes)
* `num_updated_users`, `num_updated_properties`, `bulk_updates`, `manual_updated_properties`, `manual_updated_units`, `update_by_csv_rows`, `processing_reports_rows` (`PositiveIntegerField`).
* `operator_spreadsheet_link` (`URLField`).
* `operating_notes` (`TextField`).

#### 5.2.4. Campos Específicos por `type_of_process`
(Todos `null=True, blank=True` en el modelo)
* **Deactivation/Toggle:** `deactivation_toggle_type`, `_active_policies`, `_properties_with_policies`, `_context`, `_leadership_approval`, `_marked_as_churned`.
* **Unit Transfer:** `unit_transfer_type`, `_new_partner_prospect_name`, `_receiving_partner_psm`, `_new_policyholders`, `_user_email_addresses`, `_prospect_portfolio_size`, `_prospect_landlord_type`, `_proof_of_sale`.
* **Generating XML:** `xml_state`, `xml_carrier_rvic`, `xml_carrier_ssic`, `xml_rvic_zip_file`, `xml_ssic_zip_file`. Campos de salida: `operator_rvic_file_slot1`, `_slot2`, `operator_ssic_file_slot1`, `_slot2`.
* **Address Validation:** `address_validation_policyholders`, `address_validation_opportunity_id`, `address_validation_user_email_addresses`.
* **Stripe Disputes:** `stripe_premium_disputes`, `stripe_ri_disputes` (`PositiveIntegerField`).
* **Property Records:** `property_records_type`, `_new_names`, `_new_pmc`, `_new_policyholder`, `_corrected_address`, `_updated_type`, `_units`, `_coverage_type`, `_coverage_multiplier`, `_coverage_amount`, `_integration_type`, `_integration_codes`, `_bank_details`.

#### 5.2.5. Campos para Integración con Salesforce
(Para `type_of_process='address_validation'`)
* Info de Opportunity: `salesforce_standard_opp_id` (18 char), `_opportunity_name`, `_number_of_units`, `_link`, `_account_manager`, `_closed_won_date`, `_leasing_integration_software`, `_information_needed_for_assets`.
* Salida/Operación: `assets_uploaded`, `av_number_of_units`, `av_number_of_invalid_units`, `link_to_assets`, `success_output_link`, `failed_output_link`, `rhino_accounts_created`.

#### 5.2.6. Campos para Costos Calculados en Finalización
Se han añadido tres conjuntos de campos `DecimalField` para almacenar los subtotales y totales generales de los costos al momento de la finalización de la solicitud. Cada conjunto corresponde a precios al cliente, costos de operación interna y costos de QA interna.
* **Client Price Subtotals/Total at Completion**:
    * `subtotal_user_update_client_price_completed`, `subtotal_property_update_client_price_completed`, ..., `subtotal_xml_file_client_price_completed`.
    * `grand_total_client_price_completed` (`max_digits=12, decimal_places=2`).
* **Operate Cost Subtotals/Total at Completion**:
    * `subtotal_user_update_operate_cost_completed`, ..., `subtotal_xml_file_operate_cost_completed`.
    * `grand_total_operate_cost_completed` (`max_digits=12, decimal_places=4`).
* **QA Cost Subtotals/Total at Completion**:
    * `subtotal_user_update_qa_cost_completed`, ..., `subtotal_xml_file_qa_cost_completed`.
    * `grand_total_qa_cost_completed` (`max_digits=12, decimal_places=4`).
* Todos estos campos tienen `null=True, blank=True` y un `default=Decimal('0.0X')`.

#### 5.2.7. Métodos y Propiedades del Modelo
* `get_type_prefix()`: Devuelve prefijo para `unique_code`.
* `save()`: Genera `unique_code` y establece `status` inicial.
* `local_timestamp` (propiedad): `timestamp` en zona horaria del solicitante.
* `calculated_turn_around_time` (propiedad): Calcula TAT (`completed_at - effective_start_time_for_tat`).

#### 5.2.8. Clase Meta (`UserRecordsRequest`)
* `verbose_name = _('Request')`, `verbose_name_plural = _('Requests')`.
* `ordering = ['-timestamp']`.

### 5.3. `AddressValidationFile(models.Model)`
* `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='address_validation_files'`).
* `uploaded_file`: `FileField` con `validate_file_size`.
* `uploaded_at`: `DateTimeField`.

### 5.4. Modelos de Historial (`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`)
* Campos comunes: `request`, actor (`ForeignKey` a `CustomUser`), timestamp (`_at`), `reason`/`message`.
* `ResolvedMessage`: `resolved_file`, `resolved_link`.
* `RejectedMessage`: `is_resolved_qa`.
* Meta: `ordering` por timestamp desc.

### 5.5. `OperationPrice(models.Model)`
Modelo Singleton para precios y costos.
* Campos `DecimalField` para:
    * **Client Prices**: `user_update_price`, `property_update_price`, `bulk_update_price`, `manual_property_update_price` (antes `manual_update_price`), `csv_update_price`, `processing_report_price`, y los nuevos: `manual_unit_update_price`, `address_validation_unit_price`, `stripe_dispute_price`, `xml_file_price`.
    * **Operate Costs**: `user_update_operate_cost`, ..., `manual_property_update_operate_cost`, ..., y los nuevos: `manual_unit_update_operate_cost`, `address_validation_unit_operate_cost`, `stripe_dispute_operate_cost`, `xml_file_operate_cost`.
    * **QA Costs**: `user_update_qa_cost`, ..., `manual_property_update_qa_cost`, ..., y los nuevos: `manual_unit_update_qa_cost`, `address_validation_unit_qa_cost`, `stripe_dispute_qa_cost`, `xml_file_qa_cost`.
* Todos los campos tienen `verbose_name` en inglés.

### 5.6. `SalesforceAttachmentLog(models.Model)`
* `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='salesforce_attachments'`).
* `file_name`, `file_extension`, `salesforce_file_link`.

### 5.7. `ScheduledTaskToggle(models.Model)`
* `task_name`: `CharField(unique=True, primary_key=True)`.
* `is_enabled`: `BooleanField(default=True)`.
* `last_modified`: `DateTimeField(auto_now=True)`.
* Usado para pausar/reanudar tareas programadas desde el admin.

---
## 6. Archivo de Opciones (`tasks/choices.py`)

Centraliza las `choices` para campos de modelos. Incluye:
* `TYPE_CHOICES`
* `TEAM_CHOICES` (Revenue, Support, Compliance, Accounting) y constantes individuales.
* `PRIORITY_CHOICES` (Low, Normal, High) y `PRIORITY_NORMAL`.
* `STATUS_CHOICES` (Pending, Scheduled, In Progress, Completed, Cancelled, Blocked, Pending for Approval, QA Pending, QA In Progress).
* `REQUEST_TYPE_CHOICES` (para UserGroupForm).
* `ACCESS_LEVEL_CHOICES` (para UserGroupForm).
* `DEACTIVATION_TOGGLE_CHOICES`.
* `LEADERSHIP_APPROVAL_CHOICES`.
* `UNIT_TRANSFER_TYPE_CHOICES`, `UNIT_TRANSFER_LANDLORD_TYPE_CHOICES`.
* `XML_STATE_CHOICES`.
* `PROPERTY_RECORDS_TYPE_CHOICES`, `PROPERTY_TYPE_CHOICES`, `COVERAGE_TYPE_CHOICES`, `COVERAGE_MULTIPLIER_CHOICES`, `INTEGRATION_TYPE_CHOICES`.
* *Todos los textos legibles en estas `choices` están en inglés.*

---
## 7. Validadores Personalizados (`tasks/validators.py`)

* **`validate_file_size(value)`**: Valida que el tamaño de archivo no exceda 10MB. Lanza `ValidationError`. Aplicado a campos `FileField` relevantes.

---
## 8. Formularios Detallados (`tasks/forms.py`)


### 8.1. Formularios de Usuario
* `CustomUserChangeForm`: Edita perfil. Labels en inglés.
* `CustomPasswordChangeForm`: Cambia contraseña. Labels y help_text en inglés.

### 8.2. `UserGroupForm(forms.Form)`
* Para grupos en "User Records". Labels y help_text en inglés.

### 8.3. `UserRecordsRequestForm(forms.Form)`
* Creación de "User Records". Labels y help_text en inglés.
* **Eliminación de `team_selection`**: Este campo ya no está presente. La lógica de equipo se maneja en la vista (error si el usuario está en Revenue y Support).
* Validación de `scheduled_date` (futura, zona horaria del usuario).

### 8.4. Formularios de Acción Simples (`BlockForm`, `ResolveForm`, `RejectForm`)
* Labels en inglés.

### 8.5. `OperateForm(forms.ModelForm)`
* Para detalles de operación en `send_to_qa_request` y `complete_request`.
* `__init__`:
    * **Lógica de campos condicionales actualizada**:
        * **Address Validation**: Muestra y requiere campos `av_*` y `link_to_assets`, `operating_notes`. Oculta otros como `processing_reports_rows`, campos de Stripe.
        * **Stripe Disputes**: Muestra y requiere `stripe_premium_disputes`, `stripe_ri_disputes`, `operating_notes`. Oculta otros.
        * **Generating XML**: Este formulario base no se usa; se utiliza `GeneratingXmlOperateForm`.
        * **Otros tipos (User Records, Deactivation, Unit Transfer, Property Records)**: Campos numéricos opcionales, `operating_notes` opcional.
* Labels en inglés.

### 8.6. `OperationPriceForm(forms.ModelForm)`
* Para `OperationPrice`. `fields = '__all__'`. Widgets `NumberInput`. Labels de `verbose_name` del modelo (en inglés).

### 8.7. Formularios Específicos por Tipo de Proceso
Heredan de `ModelForm`. Todos con labels/help_text en inglés y lógica de `scheduled_date`.
* **Ya no incluyen `team_selection`**.
* **8.7.1. `DeactivationToggleRequestForm`**: `clean()` valida campos condicionales.
* **8.7.2. `UnitTransferRequestForm`**: `clean()` valida campos "Partner to Prospect" y `properties`.
* **8.7.3. `GeneratingXmlRequestForm`**: `priority` por defecto en vista. `clean()` valida carrier y ZIPs.
* **8.7.4. `AddressValidationRequestForm`**: `clean()` valida `opportunity_id` vs. archivos/link.
* **8.7.5. `StripeDisputesRequestForm`**: `priority` por defecto en vista. `clean()` valida que al menos un tipo de disputa > 0.
* **8.7.6. `PropertyRecordsRequestForm`**: `clean()` con lógica compleja para campos condicionales `property_records_*`.
* **8.7.7. `GeneratingXmlOperateForm`**:
    * Formulario específico para operar ("Send to QA") y completar ("Complete") solicitudes "Generating XML".
    * Campos: `operating_notes` (opcional), `qa_needs_file_correction` (`BooleanField` para el flujo de QA indicando si se deben corregir/re-subir archivos).
    * **Campos de Archivo Dinámicos**: En `__init__`, se añaden `FileField`s al formulario basados en `xml_state` y carriers de la solicitud original, mapeados a `operator_rvic_file_slot1`, `_slot2`, `operator_ssic_file_slot1`, `_slot2` del modelo. Estos permiten al operador o al agente de QA subir los archivos XML/ZIP generados o corregidos.
    * `save()`: Sobrescrito para manejar la asignación de los archivos dinámicos.

---
## 9. Vistas Detalladas (`tasks/views.py`)


### 9.1. Funciones Auxiliares de Permisos
* `is_admin`, `is_leadership`, `is_agent`, `user_in_group`, `can_view_request`, `can_cancel_request`.
* `user_belongs_to_revenue_or_support`, `user_belongs_to_compliance`, `user_belongs_to_accounting`.

### 9.2. Vistas Generales y de Autenticación
* `home`, `profile`, `choose_request_type`. Mensajes de `django.contrib.messages` en inglés.

### 9.3. Vistas de Creación de Solicitudes
* **Lógica de Equipo Actualizada:** Para tipos de solicitud creados por Revenue/Support, si `user_in_group(user, TEAM_REVENUE)` y `user_in_group(user, TEAM_SUPPORT)` son ambos `True`, se muestra `messages.error` (en inglés) y se redirige, en lugar de un campo `team_selection`.
* Lógica de programación (status `scheduled`/`pending` y `effective_start_time_for_tat`) aplicada consistentemente.
* `user_records_request`: Asigna `team` (Revenue/Support).
* `deactivation_toggle_request`: Asigna `team`. Lógica de estado `pending_approval`.
* `unit_transfer_request`: Asigna `team`.
* `address_validation_request`: Asigna `team`. Maneja múltiples `request_files`.
* `property_records_request`: Asigna `team`.
* `generating_xml_request`: Fija `team=TEAM_COMPLIANCE`, `priority=PRIORITY_NORMAL`.
* `stripe_disputes_request`: Fija `team=TEAM_ACCOUNTING`, `priority=PRIORITY_NORMAL`.

### 9.4. Vistas de Dashboard y Detalles de Solicitud
* `portal_operations_dashboard`:
    * Filtra por tipo, estado, equipo, fechas. Paginación.
    * **Nuevo**: Pasa `is_admin_user` y `is_leadership_user` al contexto para la visualización condicional de la columna de costos.
* `request_detail`:
    * Verifica `can_view_request`.
    * Pasa `is_admin_user`, `is_leadership_user`, y otras flags de permiso al contexto.
    * **Para "Generating XML"**: Pasa `GeneratingXmlOperateForm(instance=user_request)` como `form_for_modal`.
    * Renderiza plantilla de detalle específica del tipo.

### 9.5. Vistas de Acciones de Flujo de Trabajo
* `operate_request`: Si `uncanceled_by` no es `None`, lo limpia.
* `block_request`: Si 'address\_validation' y `salesforce_standard_opp_id`, actualiza Opportunity en SF.
* `resolve_request`: Si 'address\_validation' y `salesforce_standard_opp_id`, actualiza Opportunity en SF.
* `send_to_qa_request`:
    * Usa `GeneratingXmlOperateForm` para 'generating\_xml', sino `OperateForm`.
    * Para `GeneratingXmlOperateForm`, el campo `qa_needs_file_correction` se oculta y no se requiere.
    * `is_rejected_previously = False`.
* `complete_request`:
    * Usa `GeneratingXmlOperateForm` para 'generating\_xml', sino `OperateForm`.
    * **Cálculo y Almacenamiento de Costos:**
        * Obtiene `OperationPrice.objects.first()`.
        * Calcula todos los subtotales de precios al cliente, costos de operación y costos de QA basados en los conteos de `updated_instance` y los precios/costos de `OperationPrice`.
        * Para `stripe_dispute`, suma `stripe_premium_disputes` y `stripe_ri_disputes`.
        * Para `xml_file`, cuenta `xml_carrier_rvic` y `xml_carrier_ssic`.
        * Almacena estos subtotales y los tres grandes totales (`grand_total_client_price_completed`, `grand_total_operate_cost_completed`, `grand_total_qa_cost_completed`) en los campos correspondientes de `updated_instance`.
        * Los nombres de estos nuevos campos de costo se añaden a `fields_to_update_django` para el `save()`.
    * Si 'address\_validation' y `salesforce_standard_opp_id`, actualiza Opportunity en SF.
* `approve_deactivation_toggle`: Lógica de `status` y `effective_start_time_for_tat` basada en `scheduled_date`.
* Otras vistas (`qa_request`, `cancel_request`, `reject_request`, `set_update_flag`, `clear_update_flag`, `uncancel_request`) mantienen su lógica principal, con mensajes de usuario en inglés.

### 9.6. Vista de Administración de Precios
* `manage_prices`: `@user_passes_test(is_admin)`. Usa `OperationPriceForm`. Mensajes en inglés.

---
## 10. Plantillas Detalladas (`tasks/templates/tasks/`)
 (y otras plantillas de detalle y creación)
* Todos los textos visibles por el usuario (labels, títulos, botones, mensajes de ayuda, etc.) deben estar en inglés o, si se decide usar i18n, envueltos en `{% trans "..." %}`. Actualmente, el usuario ha solicitado mantenerlos en inglés directamente.
* **`portal_operations_dashboard.html`**:
    * **Nueva Columna "Total Cost (Client)"**:
        * Se añade `<th>Total Cost (Client)</th>` condicionalmente si `is_admin_user` o `is_leadership_user`.
        * Se añade `<td>` correspondiente en el bucle, mostrando `request_item.grand_total_client_price_completed` si `request_item.status == 'completed'`.
        * El `colspan` del mensaje `{% empty %}` se ajusta dinámicamente.
* **Plantillas de Detalle (`*_detail.html`):**
    * **Nueva Sección "Price Breakdown"**:
        * Se muestra si `user.is_authenticated and (is_admin_user or is_leadership_user) and user_request.status == 'completed'`.
        * Se presenta en una tarjeta (`div.card`) dentro de una estructura `<div class="row justify-content-center"><div class="col-lg-6 col-md-8 col-sm-12">...</div></div>` para controlar su ancho y centrarla.
        * Muestra los subtotales `subtotal_*_client_price_completed` y el `grand_total_client_price_completed` del modelo `UserRecordsRequest`.
        * Solo muestra ítems de costo si el subtotal es mayor a cero.
    * **Modales para "Send to QA" / "Complete"**:
        * **Para `generating_xml_detail.html`**: Los modales usan `form_for_modal` (instancia de `GeneratingXmlOperateForm`). El JS maneja la visibilidad del checkbox `qa_needs_file_correction` y los campos de archivo asociados.
        * **Para `stripe_disputes_detail.html`**: Los modales muestran campos para `stripe_premium_disputes`, `stripe_ri_disputes`, y `operating_notes`. JS valida su obligatoriedad.
        * Para otros tipos, usan `OperateForm` con los campos numéricos estándar.

---
## 11. Lógica de Tareas en Segundo Plano (Django-Q2)

### 11.1. Activación de Solicitudes Programadas (`tasks/scheduled_jobs.py`)

* `process_scheduled_requests()`: Busca `status='scheduled'`, `scheduled_date <= hoy`. Cambia `status` a `pending`, establece `effective_start_time_for_tat`.

### 11.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)

* **`sync_salesforce_opportunities_task()`**:
    * **Implementada y funcional.**
    * **Control de Pausa/Reanudación:** Al inicio, verifica el estado de `ScheduledTaskToggle` para `task_name='salesforce_sync_opportunities'`. Si `is_enabled` es `False`, la tarea no se ejecuta.
    * Conecta a SF, consulta Opportunities, crea `UserRecordsRequest` ('address\_validation') y `SalesforceAttachmentLog`, actualiza Opportunity en SF.
    * Mensajes de log y de retorno de la tarea en inglés (o usando `_()` para potencial traducción).

### 11.3. Configuración y Ejecución del Cluster (`tasks/apps.py`)

* `TasksConfig.ready()`:
    * Programa `process_scheduled_requests` (diario 1 PM UTC).
    * Programa `sync_salesforce_opportunities_task` (CRON `0 13,16,19 * * *` - 1 PM, 4 PM, 7 PM UTC).
* Requiere `python manage.py qcluster`.

---
## 12. Administración de Django (`tasks/admin.py`)

* **`ScheduledTaskToggleAdmin`**: Nueva clase para gestionar el modelo `ScheduledTaskToggle`.
    * `list_display`: `task_name`, `is_enabled_display`, `last_modified`.
    * `list_editable`: `is_enabled`.
    * `fieldsets` definidos. `task_name` se hace no editable después de la creación. Labels y help_text en inglés.
    * No permite borrado por defecto.
* **`OperationPriceAdmin`**:
    * `fieldsets` actualizados para incluir los nuevos campos de precios/costos y el campo renombrado `manual_property_update_*`, organizados en "Client Prices", "Operate Costs", "QA Costs". Labels de fieldset en inglés.
* **`UserRecordsRequestAdmin`**:
    * `readonly_fields` y `fieldsets` actualizados para incluir los nuevos campos de costos almacenados (ej. `grand_total_client_price_completed`).
* Otras configuraciones de admin (CustomUser, Historial, etc.) se mantienen con sus personalizaciones.

---
## 13. Configuración del Entorno de Desarrollo
*(Sin cambios significativos respecto a la versión anterior del README. Incluir los pasos para clonar, entorno virtual, `pip install -r requirements.txt`, archivo `.env`, migraciones, superusuario, `runserver`, y `qcluster`)*.

---
## 14. Despliegue (Heroku)
*(Sin cambios significativos respecto a la versión anterior del README. Incluir `Procfile`, `runtime.txt`, `requirements.txt` (con `gunicorn`, `psycopg2-binary`), configuración de `settings.py` para producción, variables de entorno de Heroku, buildpack y add-ons)*.

---
## 15. Próximos Pasos y Mejoras Futuras
*(Similar a la versión anterior, pero reconociendo la completitud de la integración con Salesforce)*.
* Pruebas Exhaustivas (incluyendo cálculos de costos y flujos de Salesforce).
* Internacionalización (si se retoma).
* Notificaciones por Correo Electrónico.
* Refinamiento UI/UX, incluyendo la visualización de los costos de operación y QA si se decide.
* Documentación para el Usuario Final.
* Optimización y Seguridad para Producción.

---