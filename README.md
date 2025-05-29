# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** Analizado el 29 de mayo de 2025
**Fecha de Actualización del README:** 29 de mayo de 2025
**Documento de Referencia Principal:** "Descripción Detallada de la Plataforma de Gestión de Solicitudes (requests_webpage)" v2.3 (20 de mayo de 2025), actualizado con los cambios más recientes del código.

## Tabla de Contenidos
1.  [Introducción y Propósito](#1-introducción-y-propósito)
2.  [Estructura Detallada del Proyecto](#2-estructura-detallada-del-proyecto)
3.  [Configuración Central del Proyecto (`requests_webpage/settings.py`)](#3-configuración-central-del-proyecto-requests_webpagesettingspy)
    * [3.1. Variables Esenciales y de Despliegue](#31-variables-esenciales-y-de-despliegue)
    * [3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)](#32-aplicaciones-instaladas-installed_apps)
    * [3.3. Middleware](#33-middleware)
    * [3.4. Modelo de Usuario y Autenticación](#34-modelo-de-usuario-y-autenticación)
    * [3.5. Base de Datos (`DATABASES`)](#35-base-de-datos-databases)
    * [3.6. Archivos Estáticos y Multimedia](#36-archivos-estáticos-y-multimedia)
    * [3.7. Internacionalización (i18n) y Localización (l10n)](#37-internacionalización-i18n-y-localización-l10n)
    * [3.8. Configuración de Tareas en Segundo Plano (Django-Q2)](#38-configuración-de-tareas-en-segundo-plano-django-q2)
    * [3.9. Configuración de Salesforce](#39-configuración-de-salesforce)
    * [3.10. Logging](#310-logging)
    * [3.11. Procesadores de Contexto](#311-procesadores-de-contexto)
4.  [Enrutamiento de URLs](#4-enrutamiento-de-urls)
    * [4.1. Enrutamiento Principal (`requests_webpage/urls.py`)](#41-enrutamiento-principal-requests_webpageurlspy)
    * [4.2. Enrutamiento de la Aplicación `tasks` (`tasks/urls.py`)](#42-enrutamiento-de-la-aplicación-tasks-tasksurlspy)
5.  [Modelo de Datos (`tasks/models.py`)](#5-modelo-de-datos-tasksmodelspy)
    * [5.1. `CustomUser(AbstractUser)`](#51-customuserabstractuser)
    * [5.2. `UserRecordsRequest(models.Model)`](#52-userrecordsrequestmodelsmodel)
        * [5.2.1. Campos Generales y de Identificación](#521-campos-generales-y-de-identificación)
        * [5.2.2. Campos de Flujo de Trabajo y Asignación](#522-campos-de-flujo-de-trabajo-y-asignación)
        * [5.2.3. Campos de Detalles de Operación/QA](#523-campos-de-detalles-de-operaciónqa)
        * [5.2.4. Campos Específicos por `type_of_process`](#524-campos-específicos-por-type_of_process)
        * [5.2.5. Campos de Integración con Salesforce](#525-campos-de-integración-con-salesforce)
        * [5.2.6. Campos para Costos Calculados en Finalización](#526-campos-para-costos-calculados-en-finalización)
        * [5.2.7. Métodos y Propiedades del Modelo](#527-métodos-y-propiedades-del-modelo)
    * [5.3. `AddressValidationFile(models.Model)`](#53-addressvalidationfilemodelsmodel)
    * [5.4. Modelos de Historial (`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`)](#54-modelos-de-historial-blockedmessage-resolvedmessage-rejectedmessage)
    * [5.5. `OperationPrice(models.Model)`](#55-operationpricemodelsmodel)
    * [5.6. `SalesforceAttachmentLog(models.Model)`](#56-salesforceattachmentlogmodelsmodel)
    * [5.7. `ScheduledTaskToggle(models.Model)`](#57-scheduledtasktogglemodelsmodel)
6.  [Opciones Predefinidas (`tasks/choices.py`)](#6-opciones-predefinidas-taskschoicespy)
7.  [Validadores (`tasks/validators.py`)](#7-validadores-tasksvalidatorspy)
8.  [Formularios (`tasks/forms.py`)](#8-formularios-tasksformspy)
    * [8.1. Formularios de Usuario](#81-formularios-de-usuario)
    * [8.2. Formularios Comunes de Solicitudes y Acciones](#82-formularios-comunes-de-solicitudes-y-acciones)
    * [8.3. Formularios Específicos por Tipo de Proceso](#83-formularios-específicos-por-tipo-de-proceso)
9.  [Vistas (`tasks/views.py`)](#9-vistas-tasksviewspy)
    * [9.1. Funciones Auxiliares de Permisos](#91-funciones-auxiliares-de-permisos)
    * [9.2. Vistas Generales, de Perfil y Selección](#92-vistas-generales-de-perfil-y-selección)
    * [9.3. Vistas de Creación de Solicitudes](#93-vistas-de-creación-de-solicitudes)
    * [9.4. Dashboard y Detalle de Solicitud](#94-dashboard-y-detalle-de-solicitud)
    * [9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)](#95-vista-de-resumen-de-gastos-del-cliente-client_cost_summary_view)
    * [9.6. Vistas de Acciones de Flujo de Trabajo](#96-vistas-de-acciones-de-flujo-de-trabajo)
    * [9.7. Vista de Administración de Precios](#97-vista-de-administración-de-precios)
10. [Plantillas (`tasks/templates/`)](#10-plantillas-taskstemplates)
    * [10.1. Estructura Base (`base.html`)](#101-estructura-base-basehtml)
    * [10.2. Plantillas Principales](#102-plantillas-principales)
    * [10.3. Plantillas de Creación de Solicitudes](#103-plantillas-de-creación-de-solicitudes)
    * [10.4. Plantilla del Dashboard (`rhino_operations_dashboard.html`)](#104-plantilla-del-dashboard-rhino_operations_dashboardhtml)
    * [10.5. Plantillas de Detalle de Solicitud](#105-plantillas-de-detalle-de-solicitud)
    * [10.6. Plantilla de Resumen de Gastos del Cliente (`client_cost_summary.html`)](#106-plantilla-de-resumen-de-gastos-del-cliente-client_cost_summaryhtml)
11. [Tareas Programadas y en Segundo Plano (`django-q2`)](#11-tareas-programadas-y-en-segundo-plano-django-q2)
    * [11.1. `tasks/scheduled_jobs.py`](#111-tasksscheduled_jobspy)
    * [11.2. `tasks/salesforce_sync.py`](#112-taskssalesforce_syncpy)
    * [11.3. `tasks/apps.py` (Configuración de Tareas)](#113-tasksappspy-configuración-de-tareas)
12. [Interfaz de Administración (`tasks/admin.py`)](#12-interfaz-de-administración-tasksadminpy)
13. [Configuración del Entorno de Desarrollo](#13-configuración-del-entorno-de-desarrollo)
14. [Despliegue (Heroku)](#14-despliegue-heroku)
15. [Consideraciones Adicionales y Próximos Pasos](#15-consideraciones-adicionales-y-próximos-pasos)

---

## 1. Introducción y Propósito

La plataforma `requests_webpage` es una aplicación web integral, desarrollada sobre el robusto framework Django, concebida como una solución centralizada y altamente adaptable para la gestión eficiente de una diversidad de procesos y solicitudes operativas internas. El sistema permite a los usuarios la creación, el seguimiento detallado y la administración de múltiples tipos de solicitudes, cada una con flujos de trabajo, campos de datos específicos y lógicas de asignación a los equipos responsables dentro de la organización, como Revenue, Support, Compliance y Accounting.

Entre sus funcionalidades principales se encuentran la identificación unívoca de cada solicitud mediante un código, un sistema de priorización (Low, Normal, High), la capacidad de adjuntar archivos o proporcionar enlaces URL como parte de la información de la solicitud, y un registro exhaustivo del historial de acciones (bloqueos, resoluciones, rechazos) para cada una. La plataforma incorpora características avanzadas tales como la programación de solicitudes para su activación automática en fechas futuras, el cálculo preciso de Tiempos de Respuesta (Turn Around Time - TAT) basados en el inicio efectivo del trabajo y la fecha de completitud, y una **integración funcional y probada con Salesforce**. Esta integración automatiza la creación de solicitudes de tipo "Validación de Direcciones" (Address Validation) directamente a partir de Opportunities en Salesforce, incluyendo la sincronización de archivos adjuntos relevantes.

Una adición significativa reciente es un sistema para el **cálculo y almacenamiento persistente de los costos** asociados a cada solicitud. Estos costos, desglosados en precios al cliente, costos de operación interna y costos de QA interna, se "congelan" en el momento en que una solicitud es marcada como completada. Esta información financiera es accesible a través de un **nuevo reporte de "Resumen de Gastos del Cliente"**, el cual está restringido a usuarios con roles administrativos o de liderazgo, y ofrece filtros por rango de fechas, con visualización de subtotales por equipo y por tipo de proceso mediante gráficos de tarta (pie charts) interactivos generados con Chart.js.

Para la gestión de tareas que pueden ser de larga duración o que necesitan ejecutarse en momentos específicos sin interrumpir la experiencia del usuario, la aplicación utiliza `django-q2`, un sistema de colas de tareas. Esto asegura que procesos como la activación de solicitudes programadas o la sincronización periódica con Salesforce se ejecuten de manera asíncrona y fiable. Además, se ha implementado un mecanismo de control a través del panel de administración de Django, utilizando el modelo `ScheduledTaskToggle`, que permite a los administradores pausar y reanudar manualmente tareas programadas críticas, como la sincronización con Salesforce.

El sistema de administración de Django ha sido extensamente personalizado para ofrecer una interfaz intuitiva y eficiente para la gestión de los datos, la configuración de precios y el control de tareas. La interfaz de usuario general está construida con Bootstrap 5, priorizando un diseño responsivo y una experiencia de usuario clara, con todos los textos orientados al usuario presentados en inglés por defecto. El prefijo principal de las URLs de la aplicación ha sido estandarizado a `/rhino/`.

---

## 2. Estructura Detallada del Proyecto
*(La estructura de archivos y directorios del proyecto sigue las convenciones de Django. El directorio raíz `requests_webpage/` contiene el subdirectorio de configuración del proyecto con el mismo nombre y la aplicación principal `tasks/`. Esta última encapsula la mayoría de la lógica específica de la plataforma, incluyendo modelos, vistas, formularios, plantillas, tareas programadas y la configuración de la integración con Salesforce. Archivos como `manage.py` para la gestión del proyecto y `requirements.txt` para las dependencias residen en la raíz. El archivo `yender.yaml` para Render ha sido eliminado en favor de la configuración para Heroku.)*

---
## 3. Configuración Central del Proyecto (`requests_webpage/settings.py`)

Este archivo es el centro neurálgico de la configuración de Django para la aplicación.

### 3.1. Variables Esenciales y de Despliegue
* `SECRET_KEY`: Clave única para seguridad criptográfica, cargada desde variables de entorno mediante `django-environ`.
* `DEBUG`: Booleano que activa/desactiva el modo de depuración, gestionado por `django-environ`. Debe ser `False` en producción.
* `ALLOWED_HOSTS`: Lista de nombres de host/dominio permitidos. Para Heroku, se configura dinámicamente y se añade `.herokuapp.com`.
* `CSRF_TRUSTED_ORIGINS`: Lista de orígenes confiables para solicitudes HTTPS que modifican datos, configurable para entornos de producción.

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)
Define las aplicaciones Django que componen el proyecto:
* Aplicaciones estándar de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`.
* Aplicaciones de terceros:
    * `whitenoise.runserver_nostatic`: Para facilitar el servicio de archivos estáticos en desarrollo cuando `DEBUG` es `True`, sin necesidad de `collectstatic` constante. Se recomienda antes de `django.contrib.staticfiles`.
    * `django_q`: Para la gestión de colas de tareas y tareas programadas (se utiliza el fork `django-q2`).
* Aplicación propia: `tasks`.

### 3.3. Middleware
Secuencia de capas de procesamiento para solicitudes/respuestas HTTP:
`django.middleware.security.SecurityMiddleware`, `whitenoise.middleware.WhiteNoiseMiddleware` (para servir archivos estáticos en producción), `django.contrib.sessions.middleware.SessionMiddleware`, `django.middleware.common.CommonMiddleware`, `django.middleware.csrf.CsrfViewMiddleware`, `django.contrib.auth.middleware.AuthenticationMiddleware`, `django.contrib.messages.middleware.MessageMiddleware`, `django.middleware.clickjacking.XFrameOptionsMiddleware`, y `django.middleware.locale.LocaleMiddleware` (para internacionalización).

### 3.4. Modelo de Usuario y Autenticación
* `AUTH_USER_MODEL = 'tasks.CustomUser'`: Especifica que se utiliza el modelo `CustomUser` de la aplicación `tasks`.
* `LOGOUT_REDIRECT_URL = '/accounts/login/'`: Destino tras cerrar sesión.
* `LOGIN_REDIRECT_URL = '/rhino/dashboard/'`: Destino tras iniciar sesión exitosamente (actualizado al nuevo prefijo `/rhino/`).

### 3.5. Base de Datos (`DATABASES`)
Configurada mediante `dj_database_url.config()`, lo que permite leer la configuración de la base de datos desde la variable de entorno `DATABASE_URL`. Esto facilita el uso de PostgreSQL en Heroku (con `ssl_require` configurable por variable de entorno y `sslmode: 'require'` añadido si es PostgreSQL) y SQLite para desarrollo local como fallback. `conn_max_age=600` establece la persistencia de las conexiones.

### 3.6. Archivos Estáticos y Multimedia
* **Estáticos**: `STATIC_URL = 'static/'`, `STATIC_ROOT` (directorio `staticfiles/` en la raíz del proyecto para `collectstatic`), y `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'` para un servicio eficiente en producción.
* **Multimedia**: `MEDIA_URL = '/media/'`, `MEDIA_ROOT` (directorio `media/` en la raíz) para archivos subidos por usuarios.

### 3.7. Internacionalización (i18n) y Localización (l10n)
* `LANGUAGE_CODE = 'en-us'`.
* `TIME_ZONE = 'UTC'`.
* `USE_I18N = True`: Habilita el sistema de traducción de Django.
* `USE_TZ = True`: Habilita el soporte para zonas horarias en los campos `DateTimeField`.

### 3.8. Configuración de Tareas en Segundo Plano (Django-Q2)
* `Q_CLUSTER`: Diccionario que configura el cluster de `django-q2`, incluyendo `name` (ej. 'RequestWebpageScheduler_Heroku'), `workers` (configurable vía `DJANGO_Q_WORKERS`), `timeout`, `retry`, `queue_limit`, `bulk`, `orm = 'default'`, `catch_up: False` (para evitar ejecutar tareas programadas perdidas al reiniciar), y `log_level` (configurable vía `DJANGO_Q_LOG_LEVEL`).

### 3.9. Configuración de Salesforce
Credenciales (`SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, `SF_CONSUMER_KEY`, `SF_CONSUMER_SECRET`, `SF_DOMAIN`, `SF_VERSION`, `SF_INSTANCE_NAME`) y la URL base de Lightning (`SALESFORCE_LIGHTNING_BASE_URL`) se cargan de forma segura utilizando `django-environ`.

### 3.10. Logging
Configuración detallada de `LOGGING` con formateadores (`verbose`, `simple`, `qcluster`), manejadores (`console` y `file_tasks` para `logs/tasks_app.log`), y loggers específicos para `django`, `django.request`, la aplicación `tasks` (con nivel configurable por `DJANGO_LOG_LEVEL_TASKS`), y `django_q`.

### 3.11. Procesadores de Contexto
* Se ha añadido `'tasks.context_processors.user_role_permissions'` a la lista de `context_processors` en la configuración `TEMPLATES`. Este procesador se encarga de añadir las variables booleanas `is_admin_user` e `is_leadership_user` al contexto de todas las plantillas renderizadas mediante `django.shortcuts.render`, facilitando la lógica de visualización condicional de elementos (como enlaces en la barra de navegación o secciones de contenido) basados en el rol del usuario.

---
## 4. Enrutamiento de URLs

### 4.1. Enrutamiento Principal (`requests_webpage/urls.py`)

Define las rutas de más alto nivel del proyecto.
* `/admin/`: Acceso al sitio de administración de Django.
* `/accounts/`: Incluye las URLs estándar de `django.contrib.auth.urls` para la gestión de autenticación (login, logout, cambio de contraseña, etc.).
* **`/rhino/`**: Es el prefijo principal para todas las URLs de la aplicación `tasks`. Se logra mediante `path('rhino/', include('tasks.urls', namespace='tasks'))`. El `namespace='tasks'` permite la resolución inversa de URLs de forma organizada (ej. `{% url 'tasks:dashboard' %}`).
* `/`: La ruta raíz del sitio, mapeada a la vista `home` de la aplicación `tasks` (`tasks_views.home`).

### 4.2. Enrutamiento de la Aplicación `tasks` (`tasks/urls.py`)

Este archivo define los patrones de URL específicos para la aplicación `tasks`, los cuales son relativos al prefijo `/rhino/` definido en el archivo de URLs del proyecto.
* **Autenticación (Sobrescritura de Plantillas):**
    * `path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login')`
    * `path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout')`
* **Vistas Principales y de Usuario:**
    * `path('dashboard/', views.portal_operations_dashboard, name='portal_dashboard')`
    * `path('profile/', views.profile, name='profile')`
    * `path('manage_prices/', views.manage_prices, name='manage_prices')` (restringida a administradores).
    * **Nueva Ruta:** `path('client_cost_summary/', views.client_cost_summary_view, name='client_cost_summary')`.
* **Vistas de Creación de Solicitudes:**
    * `path('create/', views.choose_request_type, name='choose_request_type')`
    * Rutas específicas para cada tipo de solicitud bajo `create/`, como:
        * `create/user_records/` (vista `user_records_request`)
        * `create/deactivation_toggle/` (vista `deactivation_toggle_request`)
        * ... y así para `unit_transfer`, `generating_xml`, `address_validation`, `stripe_disputes`, y `property_records`.
* **Vistas de Detalle y Acciones sobre Solicitudes (usando `<int:pk>`):**
    * `path('request/<int:pk>/', views.request_detail, name='request_detail')`
    * Sub-rutas para acciones específicas sobre una solicitud, como:
        * `operate/`, `block/`, `send_to_qa/`, `qa/`, `complete/`, `cancel/`, `resolve/`, `reject/`.
        * `approve_deactivation_toggle/`.
        * `set_update_flag/`, `clear_update_flag/`, `uncancel/`.

---
## 5. Modelo de Datos (`tasks/models.py`)


### 5.1. `CustomUser(AbstractUser)`
Modelo de usuario personalizado.
* `email`: Campo `EmailField` único, usado como `USERNAME_FIELD`.
* `timezone`: Campo `CharField` para la zona horaria del usuario, con `choices` de `pytz.common_timezones` y `default='UTC'`.
* `REQUIRED_FIELDS = ['username']` para la creación de superusuarios.

### 5.2. `UserRecordsRequest(models.Model)`
Es el modelo central que representa una solicitud operativa.
#### 5.2.1. Campos Generales y de Identificación
* `type_of_process`: `CharField` que indica el tipo de solicitud (ej. 'user\_records', 'address\_validation'). Se define con `choices=TYPE_CHOICES` y está indexado (`db_index=True`).
* `unique_code`: `CharField` único, no editable, generado automáticamente en el método `save()`.
* `timestamp`: `DateTimeField` con `default=now`, marca la creación de la solicitud. Indexado.
* `requested_by`: `ForeignKey` al `CustomUser` que creó la solicitud.
* `team`: `CharField` (de `TEAM_CHOICES`), equipo asignado. Indexado.
* `priority`: `CharField` (de `PRIORITY_CHOICES`), default `PRIORITY_NORMAL`. Indexado.
* `partner_name`: `CharField` para el nombre del socio/cliente. Indexado.
* `properties`: `TextField` genérico para listar propiedades/identificadores afectados.
* `user_groups_data`: `JSONField` para almacenar datos estructurados, usado principalmente por "User Records".
* `special_instructions`: `TextField` para comentarios adicionales.
* `status`: `CharField` (de `STATUS_CHOICES`), estado actual de la solicitud. Indexado.
* `update_needed_flag`: `BooleanField` para indicar si se requiere un informe de progreso.
* `update_requested_by`, `update_requested_at`: Usuario y fecha de la solicitud de actualización.
* `user_file`: `FileField` (con `validate_file_size`) para adjuntar un archivo principal.
* `user_link`: `URLField` para un enlace principal.

#### 5.2.2. Campos de Flujo de Trabajo y Asignación
* `operator`, `qa_agent`: `ForeignKey` a `CustomUser` para los agentes asignados.
* Timestamps para el ciclo de vida: `operated_at`, `qa_pending_at`, `qa_in_progress_at`, `completed_at`, `cancelled_at`, `uncanceled_at`.
* Detalles de cancelación: `cancelled` (Boolean), `cancel_reason`, `cancelled_by`.
* Detalles de descancelación: `uncanceled_by`, `uncanceled_at`.
* `scheduled_date`: `DateField` para la programación de la activación de la solicitud.
* `effective_start_time_for_tat`: `DateTimeField` usado como base para el cálculo del TAT.
* `is_rejected_previously`: `BooleanField` para indicar si QA ha rechazado la solicitud anteriormente.

#### 5.2.3. Campos de Detalles de Operación/QA
Campos `PositiveIntegerField` opcionales para registrar métricas como `num_updated_users`, `num_updated_properties`, `bulk_updates`, `manual_updated_properties`, `manual_updated_units`, `update_by_csv_rows`, `processing_reports_rows`.
* `operator_spreadsheet_link`: `URLField`.
* `operating_notes`: `TextField` para notas del operador o QA.

#### 5.2.4. Campos Específicos por Tipo de Proceso
Campos opcionales (`null=True, blank=True`) cuya relevancia y uso dependen del valor de `type_of_process`.
* **Deactivation/Toggle**: `deactivation_toggle_type` (de `DEACTIVATION_TOGGLE_CHOICES`), `deactivation_toggle_active_policies`, `deactivation_toggle_properties_with_policies`, `deactivation_toggle_context`, `deactivation_toggle_leadership_approval` (de `LEADERSHIP_APPROVAL_CHOICES`), `deactivation_toggle_marked_as_churned`.
* **Unit Transfer**: `unit_transfer_type` (de `UNIT_TRANSFER_TYPE_CHOICES`), `unit_transfer_new_partner_prospect_name`, `unit_transfer_receiving_partner_psm`, `unit_transfer_new_policyholders`, `unit_transfer_user_email_addresses`, `unit_transfer_prospect_portfolio_size`, `unit_transfer_prospect_landlord_type` (de `UNIT_TRANSFER_LANDLORD_TYPE_CHOICES`), `unit_transfer_proof_of_sale`.
* **Generating XML**: `xml_state` (de `XML_STATE_CHOICES`), `xml_carrier_rvic` (Boolean), `xml_carrier_ssic` (Boolean), `xml_rvic_zip_file` (FileField), `xml_ssic_zip_file` (FileField). Campos de salida para archivos generados: `operator_rvic_file_slot1`, `operator_rvic_file_slot2`, `operator_ssic_file_slot1`, `operator_ssic_file_slot2` (todos `FileField`).
* **Address Validation**: `address_validation_policyholders`, `address_validation_opportunity_id`, `address_validation_user_email_addresses`.
* **Stripe Disputes**: `stripe_premium_disputes`, `stripe_ri_disputes` (`PositiveIntegerField`).
* **Property Records**: `property_records_type` (de `PROPERTY_RECORDS_TYPE_CHOICES`), y múltiples campos `property_records_*` como `_new_names`, `_new_pmc`, `_corrected_address`, `_updated_type`, `_units`, `_coverage_type`, `_coverage_multiplier`, `_coverage_amount`, `_integration_type`, `_integration_codes`, `_bank_details`.

#### 5.2.5. Campos de Integración con Salesforce
Específicos para `type_of_process='address_validation'`.
* **Información de la Opportunity:** `salesforce_standard_opp_id` (ID SF de 18 caracteres), `salesforce_opportunity_name`, `salesforce_number_of_units`, `salesforce_link`, `salesforce_account_manager`, `salesforce_closed_won_date`, `salesforce_leasing_integration_software`, `salesforce_information_needed_for_assets`.
* **Campos de Salida/Operación para Salesforce:** `assets_uploaded`, `av_number_of_units`, `av_number_of_invalid_units`, `link_to_assets`, `success_output_link`, `failed_output_link`, `rhino_accounts_created`.

#### 5.2.6. Campos para Costos Calculados en Finalización
Campos `DecimalField` que se rellenan cuando `status` cambia a `'completed'`.
* **Precios al Cliente (`*_client_price_completed`)**: `subtotal_user_update_client_price_completed`, `subtotal_property_update_client_price_completed`, etc., y `grand_total_client_price_completed`.
* **Costos de Operación (`*_operate_cost_completed`)**: `subtotal_user_update_operate_cost_completed`, etc., y `grand_total_operate_cost_completed`.
* **Costos de QA (`*_qa_cost_completed`)**: `subtotal_user_update_qa_cost_completed`, etc., y `grand_total_qa_cost_completed`.

#### 5.2.7. Métodos y Propiedades del Modelo
* `get_type_prefix()`: Devuelve un prefijo para `unique_code`.
* `save()`: Lógica para generar `unique_code` secuencialmente (prefijo `TIPO-AÑOQTRNUMERO`) y establecer `status` inicial.
* `local_timestamp` (propiedad): Retorna `self.timestamp` en la zona horaria del solicitante.
* `calculated_turn_around_time` (propiedad): Calcula `completed_at - effective_start_time_for_tat`.

### 5.3. `AddressValidationFile(models.Model)`
* `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='address_validation_files'`).
* `uploaded_file`: `FileField` con `validate_file_size`.
* `uploaded_at`: `DateTimeField`.

### 5.4. Modelos de Historial (`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`)
Registran eventos con `request`, actor (`ForeignKey`), timestamp (`_at`), y `reason` o `message`. `ResolvedMessage` incluye `resolved_file` y `resolved_link`. `RejectedMessage` tiene `is_resolved_qa`.

### 5.5. `OperationPrice(models.Model)`
Modelo Singleton (`pk=1`) para precios/costos unitarios, incluyendo los renombrados (ej. `manual_property_update_price`) y los nuevos para `manual_unit_update`, `address_validation_unit`, `stripe_dispute`, `xml_file`, con sus `_operate_cost` y `_qa_cost`.

### 5.6. `SalesforceAttachmentLog(models.Model)`
Metadatos de adjuntos de Salesforce: `request`, `file_name`, `file_extension`, `salesforce_file_link`.

### 5.7. `ScheduledTaskToggle(models.Model)`
* `task_name` (PK), `is_enabled`, `last_modified`. Para pausar/reanudar tareas.

---
## 6. Opciones Predefinidas (`tasks/choices.py`)

Define las listas de tuplas `CHOICES` usadas en los modelos (ej. `TYPE_CHOICES`, `STATUS_CHOICES`, `TEAM_CHOICES`, `PRIORITY_CHOICES`). El orden de `TEAM_CHOICES` y `TYPE_CHOICES` es utilizado para la visualización en la página de resumen de costos.

---
## 7. Validadores (`tasks/validators.py`)

* `validate_file_size(value)`: Validador para asegurar que los archivos subidos no excedan 10MB.

---
## 8. Formularios (`tasks/forms.py`)


### 8.1. Formularios de Usuario
* `CustomUserChangeForm`: Edición de perfil.
* `CustomPasswordChangeForm`: Cambio de contraseña.

### 8.2. Formularios Comunes de Solicitudes y Acciones
* `UserGroupForm`: Para grupos en "User Records".
* `UserRecordsRequestForm`: Creación de "User Records". No tiene `team_selection`. Validación de `scheduled_date`.
* `BlockForm`, `ResolveForm`, `RejectForm`.
* **`OperateForm`**: `ModelForm` para detalles de operación. Su método `__init__` adapta los campos visibles y su obligatoriedad según el `type_of_process` de la solicitud. Por ejemplo, para 'Address Validation' requiere campos como `av_number_of_units`, y para 'Stripe Disputes' requiere `stripe_premium_disputes` y `stripe_ri_disputes`.
* `OperationPriceForm`: Para `OperationPrice`. Refleja los nuevos campos y renombrados.

### 8.3. Formularios Específicos por Tipo de Proceso
Todos son `ModelForm` para `UserRecordsRequest`. No incluyen `team_selection`.
* `DeactivationToggleRequestForm`, `UnitTransferRequestForm`, `GeneratingXmlRequestForm` (priority por defecto en vista, valida ZIPs condicionales), `AddressValidationRequestForm` (valida `opportunity_id` vs. archivos/link), `StripeDisputesRequestForm` (priority por defecto en vista, valida conteo de disputas), `PropertyRecordsRequestForm` (lógica compleja en `clean()` para campos condicionales).
* **`GeneratingXmlOperateForm`**: Para operar y completar "Generating XML". Maneja subida de archivos XML/ZIP generados por operador/QA a través de campos dinámicos y el checkbox `qa_needs_file_correction`.

---
## 9. Vistas (`tasks/views.py`)


### 9.1. Funciones Auxiliares de Permisos
`is_admin`, `is_leadership`, `is_agent`, `user_in_group`, `user_is_admin_or_leader`, `can_view_request`, `can_cancel_request`, decoradores `user_belongs_to_*`.

### 9.2. Vistas Generales, de Perfil y Selección
`home`, `profile`, `choose_request_type`.

### 9.3. Vistas de Creación de Solicitudes
* **Lógica de Equipo Actualizada:** Error (`messages.error`) y redirección si usuario pertenece a `TEAM_REVENUE` y `TEAM_SUPPORT` simultáneamente para tipos de solicitud relevantes.

### 9.4. Dashboard y Detalle de Solicitud
* `portal_operations_dashboard`: Pasa `is_admin_user`, `is_leadership_user` al contexto.
* `request_detail`: Pasa `is_admin_user`, `is_leadership_user`. Para "Generating XML", pasa `GeneratingXmlOperateForm` como `form_for_modal`.

### 9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)
* `@login_required` y `@user_passes_test(user_is_admin_or_leader)`.
* Filtro de fechas (default mes actual).
* Calcula gran total y subtotales de `grand_total_client_price_completed` (por equipo y tipo de proceso).
* Prepara datos para dos pie charts (Chart.js), ordenados según `CHOICES`.
* Renderiza `client_cost_summary.html`.

### 9.6. Vistas de Acciones de Flujo de Trabajo
* `send_to_qa_request`, `complete_request`: Usan `GeneratingXmlOperateForm` o `OperateForm`.
* **`complete_request` Actualizada:** Calcula y guarda todos los subtotales y totales de costos (`*_client_price_completed`, `*_operate_cost_completed`, `*_qa_cost_completed`) en `UserRecordsRequest` al completar.
* Lógica de Salesforce en `block_request`, `resolve_request`, `complete_request`.

### 9.7. Vista de Administración de Precios
`manage_prices`: Restringida a admin. Usa `OperationPriceForm`.

---
## 10. Plantillas (`tasks/templates/`)
Textos de UI en inglés.

### 10.1. Estructura Base (`base.html`)

* **Nuevo Enlace "Cost Summary"**: Visible si `is_admin_user or is_leadership_user` (variables del procesador de contexto).

### 10.2. Plantillas Principales
`home.html`, `profile.html`, `choose_request_type.html`.

### 10.3. Plantillas de Creación y Detalle de Solicitudes
* **Plantillas de Detalle (`*_detail.html`):**
    * **Nueva Sección "Price Breakdown"**: Visible para `admin`/`leadership` si `status == 'completed'`. Tarjeta centrada, ancho reducido. Muestra costos del cliente.
    * Modales para "Generating XML" y "Stripe Disputes" usan sus formularios específicos.
* **`rhino_operations_dashboard.html`** (antes `portal_operations_dashboard.html`):
    * **Nueva Columna "Total Cost (Client)"**: Visible para `admin`/`leadership`.
* **`users_records_request.html`** (antes `users_records.html`).

### 10.4. Nueva Plantilla: Resumen de Gastos del Cliente (`client_cost_summary.html`)
Filtro de fechas, total, subtotales, dos `canvas` para pie charts (Chart.js) con bordes negros. JS para inicializar gráficos.

---
## 11. Tareas Programadas y en Segundo Plano (`django-q2`)

### 11.1. `tasks/scheduled_jobs.py`

* `process_scheduled_requests()`: Activa solicitudes.

### 11.2. `tasks/salesforce_sync.py`

* `sync_salesforce_opportunities_task()`: **Funcional.** Pausa/Reanudación vía `ScheduledTaskToggle`.

### 11.3. `tasks/apps.py` (Configuración de Tareas)

* Programa `process_scheduled_requests` y `sync_salesforce_opportunities_task`.

---
## 12. Interfaz de Administración (`tasks/admin.py`)

* `UserRecordsRequestAdmin`: `readonly_fields` y `fieldsets` incluyen los nuevos campos de costos.
* `OperationPriceAdmin`: `fieldsets` actualizados con nuevos precios/costos.
* **`ScheduledTaskToggleAdmin`**: Para gestionar `ScheduledTaskToggle`.

---
## 13. Configuración del Entorno de Desarrollo
*(Pasos estándar: clonar, venv, `pip install`, `.env`, migraciones, superusuario, `runserver`, `qcluster`)*.

---
## 14. Despliegue (Heroku)
*(Preparado para Heroku con `Procfile`, `runtime.txt`, y `settings.py` adaptable).*

---
## 15. Consideraciones Adicionales y Próximos Pasos
* Pruebas exhaustivas.
* Refinamiento UI/UX.

---