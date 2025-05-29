# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** Analizado el 29 de mayo de 2025
**Fecha de Actualización del README:** 29 de mayo de 2025
**Documento de Referencia Principal:** "Descripción Detallada de la Plataforma de Gestión de Solicitudes (requests_webpage)" v2.3 (20 de mayo de 2025), actualizado para reflejar el estado actual del código.

## Tabla de Contenidos
1.  [Introducción y Propósito](#1-introducción-y-propósito)
2.  [Estructura Detallada del Proyecto](#2-estructura-detallada-del-proyecto)
3.  [Configuración Central del Proyecto (`requests_webpage/settings.py`)](#3-configuración-central-del-proyecto-requests_webpagesettingspy)
    * [3.1. Variables Fundamentales y de Entorno](#31-variables-fundamentales-y-de-entorno)
    * [3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)](#32-aplicaciones-instaladas-installed_apps)
    * [3.3. Middleware](#33-middleware)
    * [3.4. Autenticación y Modelo de Usuario](#34-autenticación-y-modelo-de-usuario)
    * [3.5. Configuración de Base de Datos](#35-configuración-de-base-de-datos)
    * [3.6. Gestión de Archivos Estáticos y Multimedia](#36-gestión-de-archivos-estáticos-y-multimedia)
    * [3.7. Internacionalización (i18n) y Localización (l10n)](#37-internacionalización-i18n-y-localización-l10n)
    * [3.8. Tareas en Segundo Plano (Django-Q2)](#38-tareas-en-segundo-plano-django-q2)
    * [3.9. Integración con Salesforce](#39-integración-con-salesforce)
    * [3.10. Configuración de Logging](#310-configuración-de-logging)
    * [3.11. Procesadores de Contexto de Plantillas](#311-procesadores-de-contexto-de-plantillas)
4.  [Enrutamiento de URLs (`urls.py`)](#4-enrutamiento-de-urls-urlspy)
    * [4.1. Enrutador Principal del Proyecto (`requests_webpage/urls.py`)](#41-enrutador-principal-del-proyecto-requests_webpageurlspy)
    * [4.2. Enrutador de la Aplicación `tasks` (`tasks/urls.py`)](#42-enrutador-de-la-aplicación-tasks-tasksurlspy)
5.  [Modelo de Datos Detallado (`tasks/models.py`)](#5-modelo-de-datos-detallado-tasksmodelspy)
    * [5.1. `CustomUser(AbstractUser)`](#51-customuserabstractuser)
    * [5.2. `UserRecordsRequest(models.Model)`](#52-userrecordsrequestmodelsmodel)
        * [5.2.1. Atributos Generales de Identificación y Estado](#521-atributos-generales-de-identificación-y-estado)
        * [5.2.2. Atributos de Flujo de Trabajo, Asignación y Programación](#522-atributos-de-flujo-de-trabajo-asignación-y-programación)
        * [5.2.3. Atributos para Detalles de Operación y QA](#523-atributos-para-detalles-de-operación-y-qa)
        * [5.2.4. Atributos Específicos por Tipo de Proceso (`type_of_process`)](#524-atributos-específicos-por-tipo-de-proceso-type_of_process)
        * [5.2.5. Atributos para la Integración con Salesforce](#525-atributos-para-la-integración-con-salesforce)
        * [5.2.6. Atributos para Costos Calculados en Finalización](#526-atributos-para-costos-calculados-en-finalización)
        * [5.2.7. Métodos y Propiedades Notorias del Modelo](#527-métodos-y-propiedades-notorias-del-modelo)
    * [5.3. `AddressValidationFile(models.Model)`](#53-addressvalidationfilemodelsmodel)
    * [5.4. Modelos de Historial de Acciones](#54-modelos-de-historial-de-acciones)
    * [5.5. `OperationPrice(models.Model)`](#55-operationpricemodelsmodel)
    * [5.6. `SalesforceAttachmentLog(models.Model)`](#56-salesforceattachmentlogmodelsmodel)
    * [5.7. `ScheduledTaskToggle(models.Model)`](#57-scheduledtasktogglemodelsmodel)
6.  [Definición Centralizada de Opciones (`tasks/choices.py`)](#6-definición-centralizada-de-opciones-taskschoicespy)
7.  [Validadores Personalizados (`tasks/validators.py`)](#7-validadores-personalizados-tasksvalidatorspy)
8.  [Formularios Detallados (`tasks/forms.py`)](#8-formularios-detallados-tasksformspy)
    * [8.1. Formularios de Gestión de Usuario](#81-formularios-de-gestión-de-usuario)
    * [8.2. Formularios para la Creación de Solicitudes](#82-formularios-para-la-creación-de-solicitudes)
    * [8.3. Formularios para Acciones de Flujo de Trabajo y Operación](#83-formularios-para-acciones-de-flujo-de-trabajo-y-operación)
9.  [Lógica de las Vistas (`tasks/views.py`)](#9-lógica-de-las-vistas-tasksviewspy)
    * [9.1. Funciones Auxiliares y Control de Permisos](#91-funciones-auxiliares-y-control-de-permisos)
    * [9.2. Vistas Principales (Home, Profile, Choose Request Type)](#92-vistas-principales-home-profile-choose-request-type)
    * [9.3. Vistas de Creación de Solicitudes (Detalle por Tipo)](#93-vistas-de-creación-de-solicitudes-detalle-por-tipo)
    * [9.4. Vistas de Visualización (Dashboard y Detalle de Solicitud)](#94-vistas-de-visualización-dashboard-y-detalle-de-solicitud)
    * [9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)](#95-vista-de-resumen-de-gastos-del-cliente-client_cost_summary_view)
    * [9.6. Vistas de Acciones del Flujo de Trabajo (Detalle por Acción)](#96-vistas-de-acciones-del-flujo-de-trabajo-detalle-por-acción)
10. [Estructura y Contenido de las Plantillas (`tasks/templates/`)](#10-estructura-y-contenido-de-las-plantillas-taskstemplates)
    * [10.1. Plantilla Base (`base.html`)](#101-plantilla-base-basehtml)
    * [10.2. Plantillas de Creación de Solicitudes (Ejemplos)](#102-plantillas-de-creación-de-solicitudes-ejemplos)
    * [10.3. Plantilla del Dashboard (`rhino_operations_dashboard.html`)](#103-plantilla-del-dashboard-rhino_operations_dashboardhtml)
    * [10.4. Plantillas de Detalle de Solicitud (Ejemplos y Estructura Común)](#104-plantillas-de-detalle-de-solicitud-ejemplos-y-estructura-común)
    * [10.5. Plantilla de Resumen de Gastos (`client_cost_summary.html`)](#105-plantilla-de-resumen-de-gastos-client_cost_summaryhtml)
11. [Tareas Programadas y en Segundo Plano (Django-Q2)](#11-tareas-programadas-y-en-segundo-plano-django-q2)
    * [11.1. Procesamiento de Solicitudes Programadas (`tasks/scheduled_jobs.py`)](#111-procesamiento-de-solicitudes-programadas-tasksscheduled_jobspy)
    * [11.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)](#112-sincronización-con-salesforce-taskssalesforce_syncpy)
    * [11.3. Configuración de Programación de Tareas (`tasks/apps.py`)](#113-configuración-de-programación-de-tareas-tasksappspy)
12. [Interfaz de Administración de Django (`tasks/admin.py`)](#12-interfaz-de-administración-de-django-tasksadminpy)
13. [Configuración del Entorno de Desarrollo](#13-configuración-del-entorno-de-desarrollo)
14. [Despliegue (Heroku)](#14-despliegue-heroku)
15. [Consideraciones Adicionales y Próximos Pasos](#15-consideraciones-adicionales-y-próximos-pasos)

---

## 1. Introducción y Propósito

La plataforma `requests_webpage` es una aplicación web integral, desarrollada sobre el robusto framework Django, concebida como una solución centralizada y altamente adaptable para la gestión eficiente de una diversidad de procesos y solicitudes operativas internas. El sistema permite a los usuarios la creación, el seguimiento detallado y la administración de múltiples tipos de solicitudes, cada una con flujos de trabajo, campos de datos específicos y lógicas de asignación a los equipos responsables dentro de la organización, como Revenue, Support, Compliance y Accounting.

Entre sus funcionalidades principales se encuentran la identificación unívoca de cada solicitud mediante un código, un sistema de priorización (Low, Normal, High), la capacidad de adjuntar archivos o proporcionar enlaces URL como parte de la información de la solicitud, y un registro exhaustivo del historial de acciones (bloqueos, resoluciones, rechazos) para cada una. La plataforma incorpora características avanzadas tales como la programación de solicitudes para su activación automática en fechas futuras, el cálculo preciso de Tiempos de Respuesta (Turn Around Time - TAT) basados en el inicio efectivo del trabajo y la fecha de completitud, y una **integración funcional y probada con Salesforce**. Esta integración automatiza la creación de solicitudes de tipo "Validación de Direcciones" (Address Validation) directamente a partir de Opportunities en Salesforce, incluyendo la sincronización de archivos adjuntos relevantes.

Una adición significativa reciente es un sistema para el **cálculo y almacenamiento persistente de los costos** asociados a cada solicitud. Estos costos, desglosados en precios al cliente, costos de operación interna y costos de QA interna, se "congelan" en el momento en que una solicitud es marcada como completada. Esta información financiera es accesible a través de un **nuevo reporte de "Resumen de Gastos del Cliente"** (accesible en `/rhino/client_cost_summary/`), el cual está restringido a usuarios con roles administrativos o de liderazgo, y ofrece filtros por rango de fechas, con visualización de subtotales por equipo y por tipo de proceso mediante gráficos de tarta (pie charts) y gráficos de dispersión con líneas suavizadas (scatter plots) generados con Chart.js. Los puntos en los scatter plots son interactivos y enlazan al detalle de la solicitud correspondiente.

La plataforma se apoya en `django-q2` para la gestión de tareas en segundo plano y programadas, asegurando que procesos como la activación automática de solicitudes programadas o la sincronización periódica con Salesforce se ejecuten de manera asíncrona y fiable. Además, se ha implementado un mecanismo a través del panel de administración de Django, utilizando el modelo `ScheduledTaskToggle`, que permite a los administradores pausar y reanudar manualmente tareas programadas críticas, como la sincronización con Salesforce.

El sistema de administración de Django ha sido extensamente personalizado para ofrecer una interfaz intuitiva y eficiente para la gestión de los datos, la configuración de precios y el control de tareas. La interfaz de usuario general está construida con Bootstrap 5, priorizando un diseño responsivo y una experiencia de usuario clara, con todos los textos orientados al usuario presentados en inglés por defecto. El prefijo principal de las URLs de la aplicación ha sido estandarizado a `/rhino/`.

---

## 2. Estructura Detallada del Proyecto
*(La estructura de archivos principal sigue las convenciones de Django: el directorio del proyecto `requests_webpage/` contiene el subdirectorio de configuración y la aplicación principal `tasks/`. La aplicación `tasks/` encapsula modelos, vistas, formularios, plantillas, tareas programadas y la lógica de integración. Los nombres de plantillas importantes ahora incluyen `rhino_operations_dashboard.html` y `users_records_request.html`.)*

---
## 3. Configuración Central del Proyecto (`requests_webpage/settings.py`)

Este archivo configura aspectos globales de la aplicación.

### 3.1. Variables Fundamentales y de Entorno
* `SECRET_KEY`, `DEBUG`: Gestionadas por `django-environ` para seguridad y flexibilidad entre entornos.
* `ALLOWED_HOSTS`: Lista de hosts permitidos, adaptable para desarrollo y producción (ej. `'.herokuapp.com'`).
* `CSRF_TRUSTED_ORIGINS`: Dominios confiables para CSRF, importante en producción.

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)
Consiste en aplicaciones estándar de Django (`django.contrib.admin`, `django.contrib.auth`, etc.), la aplicación principal del proyecto `tasks`, y aplicaciones de terceros como `django_q` (para tareas en segundo plano) y `'whitenoise.runserver_nostatic'` (para el manejo de archivos estáticos en desarrollo).

### 3.3. Middleware
Una secuencia de componentes que procesan solicitudes y respuestas. Incluye `SecurityMiddleware`, `WhiteNoiseMiddleware` (para servir archivos estáticos), `SessionMiddleware`, `CommonMiddleware`, `CsrfViewMiddleware`, `AuthenticationMiddleware`, `MessageMiddleware`, `ClickjackingXFrameOptionsMiddleware`, y `LocaleMiddleware` (preparada para internacionalización).

### 3.4. Autenticación y Modelo de Usuario
* `AUTH_USER_MODEL = 'tasks.CustomUser'`: Indica el uso del modelo de usuario personalizado `CustomUser` de la aplicación `tasks`.
* `LOGOUT_REDIRECT_URL = '/accounts/login/'`: URL a la que se redirige tras cerrar sesión.
* `LOGIN_REDIRECT_URL = '/rhino/dashboard/'`: URL a la que se redirige tras un inicio de sesión exitoso (actualizado al nuevo prefijo `/rhino/`).

### 3.5. Configuración de Base de Datos
Utiliza `dj_database_url.config()` para leer la configuración desde la variable de entorno `DATABASE_URL`. Esto permite usar PostgreSQL en Heroku (con `ssl_require` y `sslmode='require'`) y SQLite como alternativa para desarrollo local. `conn_max_age` está configurado para la persistencia de conexiones.

### 3.6. Gestión de Archivos Estáticos y Multimedia
* **Archivos Estáticos**: `STATIC_URL = 'static/'`. `STATIC_ROOT` es el directorio donde `collectstatic` reúne los archivos. `STATICFILES_STORAGE` está configurado como `'whitenoise.storage.CompressedManifestStaticFilesStorage'` para un servicio eficiente en producción.
* **Archivos Multimedia**: `MEDIA_URL = '/media/'` y `MEDIA_ROOT` para la gestión de archivos subidos por los usuarios.

### 3.7. Internacionalización (i18n) y Localización (l10n)
* `LANGUAGE_CODE = 'en-us'`: Idioma por defecto.
* `TIME_ZONE = 'UTC'`: Zona horaria interna.
* `USE_I18N = True` y `USE_TZ = True`: Habilitan la traducción y el soporte de zonas horarias.

### 3.8. Tareas en Segundo Plano (Django-Q2)
* `Q_CLUSTER`: Diccionario de configuración para el cluster de `django-q2`, definiendo `name`, `workers`, `timeout`, `retry`, `orm` (usa la base de datos 'default'), `catch_up: False`, y `log_level`.

### 3.9. Integración con Salesforce
Credenciales y configuraciones para la API de Salesforce (`SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, `SF_CONSUMER_KEY`, `SF_CONSUMER_SECRET`, `SF_DOMAIN`, `SF_VERSION`, `SF_INSTANCE_NAME`) se cargan de forma segura usando `django-environ`. La `SALESFORCE_LIGHTNING_BASE_URL` se construye dinámicamente.

### 3.10. Configuración de Logging
Configuración detallada de `LOGGING` con múltiples formateadores (`verbose`, `simple`, `qcluster`) y manejadores (`console`, `file_tasks` para `logs/tasks_app.log`). Se definen loggers específicos para `django`, `django.request`, la aplicación `tasks` (con nivel configurable por `DJANGO_LOG_LEVEL_TASKS`), y `django_q`.

### 3.11. Procesadores de Contexto de Plantillas
* Se ha añadido `'tasks.context_processors.user_role_permissions'` a la lista de `context_processors` en la configuración de `TEMPLATES`. Este procesador tiene la responsabilidad de añadir las variables booleanas `is_admin_user` (evalúa si el usuario es superusuario o staff) e `is_leadership_user` (evalúa si el usuario pertenece al grupo 'Leaderships') al contexto de todas las plantillas que se renderizan mediante `django.shortcuts.render()`. Esto simplifica la lógica de visualización condicional en plantillas como `base.html` para elementos de navegación globales.

---
## 4. Enrutamiento de URLs (`urls.py`)

### 4.1. Enrutador Principal del Proyecto (`requests_webpage/urls.py`)

Este archivo es el primer punto de entrada para el enrutamiento de URLs.
* `path('admin/', admin.site.urls)`: Define el acceso al panel de administración de Django.
* `path('accounts/', include('django.contrib.auth.urls'))`: Incluye las URLs estándar para la autenticación de usuarios.
* `path('rhino/', include('tasks.urls', namespace='tasks'))`: **Actualizado**. Todas las URLs de la aplicación `tasks` ahora están prefijadas con `/rhino/`. El `namespace='tasks'` es crucial para la resolución inversa de URLs (ej. `{% url 'tasks:nombre_vista' %}`).
* `path('', tasks_views.home, name='home')`: Define la vista para la página de inicio del sitio.

### 4.2. Enrutador de la Aplicación `tasks` (`tasks/urls.py`)

Define los patrones de URL específicos para la aplicación `tasks`, relativos al prefijo `/rhino/`.
* `app_name = 'tasks'`.
* **Autenticación:** Rutas para `login` y `logout` usando `auth_views` con plantillas personalizadas si es necesario.
* **Vistas Principales:** Rutas para `portal_dashboard`, `profile`, `manage_prices`.
* **Nueva Ruta de Resumen de Costos:** `path('client_cost_summary/', views.client_cost_summary_view, name='client_cost_summary')`.
* **Creación de Solicitudes:** Una ruta `create/` para la vista `choose_request_type`, seguida de sub-rutas para cada tipo de solicitud específico (ej. `create/user_records/`, `create/address_validation/`).
* **Detalle y Acciones de Solicitud:** Un patrón base `request/<int:pk>/` para `request_detail`, y sub-rutas para todas las acciones del flujo de trabajo (ej. `operate/`, `block/`, `send_to_qa/`, `complete/`, `cancel/`, etc.).

---
## 5. Modelo de Datos Detallado (`tasks/models.py`)


### 5.1. `CustomUser(AbstractUser)`
Modelo de usuario que extiende `AbstractUser`.
* `email = models.EmailField(unique=True)`: Se utiliza como el campo de nombre de usuario (`USERNAME_FIELD`).
* `timezone = models.CharField(...)`: Almacena la zona horaria preferida del usuario, con `choices` generadas desde `pytz.common_timezones` y `'UTC'` como valor por defecto.

### 5.2. `UserRecordsRequest(models.Model)`
El modelo principal que representa cada solicitud operativa en el sistema.
#### 5.2.1. Atributos Generales de Identificación y Estado
* `type_of_process`: `CharField` crucial que define la naturaleza de la solicitud (ej. `'user_records'`, `'deactivation_toggle'`). Usa `TYPE_CHOICES` y está indexado.
* `unique_code`: `CharField` único y no editable, generado automáticamente con un prefijo basado en el tipo de proceso y una secuencia trimestral/anual.
* `timestamp`: `DateTimeField` que registra la fecha y hora de creación.
* `requested_by`: `ForeignKey` al `CustomUser` que creó la solicitud.
* `team`: `CharField` opcional que indica el equipo asignado (de `TEAM_CHOICES`).
* `priority`: `CharField` para la prioridad (`PRIORITY_CHOICES`), con `'normal'` como valor por defecto.
* `partner_name`: `CharField` para el nombre del socio o cliente.
* `properties`: `TextField` para una lista de propiedades o identificadores afectados.
* `user_groups_data`: `JSONField` para datos estructurados en solicitudes de "User Records".
* `special_instructions`: `TextField` para notas adicionales.
* `status`: `CharField` (de `STATUS_CHOICES`) que indica el estado actual del flujo de trabajo.
* `update_needed_flag`, `update_requested_by`, `update_requested_at`: Para gestionar solicitudes de actualización de progreso.
* `user_file`, `user_link`: Para adjuntar un archivo o un enlace genérico a la solicitud.

#### 5.2.2. Atributos de Flujo de Trabajo, Asignación y Programación
* `operator`, `qa_agent`: `ForeignKey` a `CustomUser` para los agentes asignados.
* Timestamps para eventos clave: `operated_at`, `qa_pending_at`, `qa_in_progress_at`, `completed_at`, `cancelled_at`, `uncanceled_at`.
* Detalles de cancelación: `cancelled` (Boolean), `cancel_reason` (Text), `cancelled_by` (User), `uncanceled_by` (User).
* `scheduled_date`: `DateField` para programar la activación futura de una solicitud.
* `effective_start_time_for_tat`: `DateTimeField` que marca el inicio real para el cálculo del TAT.
* `is_rejected_previously`: `BooleanField` que indica si la solicitud fue rechazada por QA.

#### 5.2.3. Atributos para Detalles de Operación y QA
Campos `PositiveIntegerField` opcionales para registrar métricas cuantitativas de la operación: `num_updated_users`, `num_updated_properties`, `bulk_updates`, `manual_updated_properties`, `manual_updated_units`, `update_by_csv_rows`, `processing_reports_rows`.
* `operator_spreadsheet_link`: `URLField` para un enlace a una hoja de cálculo externa.
* `operating_notes`: `TextField` para notas detalladas del operador o del agente de QA.

#### 5.2.4. Atributos Específicos por Tipo de Proceso (`type_of_process`)
El modelo incluye un conjunto extenso de campos que son relevantes solo para ciertos valores de `type_of_process`. Todos son opcionales (`null=True, blank=True`) a nivel de base de datos.
* **Deactivation/Toggle**: `deactivation_toggle_type`, `_active_policies`, `_properties_with_policies`, `_context`, `_leadership_approval`, `_marked_as_churned`.
* **Unit Transfer**: `unit_transfer_type`, `_new_partner_prospect_name`, etc.
* **Generating XML**: `xml_state`, `xml_carrier_rvic` (Boolean), `xml_carrier_ssic` (Boolean), y campos `FileField` para los ZIPs de entrada (`xml_rvic_zip_file`, `xml_ssic_zip_file`) y para los archivos de salida generados por el operador (`operator_rvic_file_slot1`, `operator_rvic_file_slot2`, `operator_ssic_file_slot1`, `operator_ssic_file_slot2`).
* **Address Validation**: `address_validation_policyholders`, `_opportunity_id`, `_user_email_addresses`.
* **Stripe Disputes**: `stripe_premium_disputes`, `stripe_ri_disputes` (`PositiveIntegerField`).
* **Property Records**: `property_records_type`, y numerosos campos `property_records_*` para nuevos nombres, PMC, dirección corregida, tipo de propiedad, unidades, detalles de cobertura, códigos de integración y detalles bancarios.

#### 5.2.5. Atributos para la Integración con Salesforce
Específicos para `type_of_process='address_validation'`.
* `salesforce_standard_opp_id`: ID de Salesforce (18 caracteres).
* Otros campos para nombre de la oportunidad, número de unidades, enlace a SF, Account Manager, fecha de "Closed Won", software de integración, e información necesaria para activos.
* Campos de salida de la operación de AV: `assets_uploaded`, `av_number_of_units`, `av_number_of_invalid_units`, `link_to_assets`, `success_output_link`, `failed_output_link`, `rhino_accounts_created`.

#### 5.2.6. Atributos para Costos Calculados en Finalización
Se han añadido tres grupos de campos `DecimalField` para almacenar los costos calculados cuando una solicitud se marca como `completed`. Tienen `verbose_name` en inglés y `default=Decimal('0.0X')`.
* **Precios al Cliente (`*_client_price_completed`)**: 10 campos de subtotales (uno por cada métrica en `OperationPrice`, ej. `subtotal_user_update_client_price_completed`, `subtotal_xml_file_client_price_completed`) y `grand_total_client_price_completed`. `max_digits=10` (o 12 para total), `decimal_places=2`.
* **Costos de Operación (`*_operate_cost_completed`)**: 10 campos de subtotales y `grand_total_operate_cost_completed`. `max_digits=10` (o 12 para total), `decimal_places=4`.
* **Costos de QA (`*_qa_cost_completed`)**: 10 campos de subtotales y `grand_total_qa_cost_completed`. `max_digits=10` (o 12 para total), `decimal_places=4`.

#### 5.2.7. Métodos y Propiedades Notorias del Modelo
* `get_type_prefix()`: Retorna un prefijo de cadena para el `unique_code`.
* `save()`: Sobrescrito para generar el `unique_code` si es una nueva instancia (formato `TIPO-AÑOQTRNUMERO`, secuencial) y para establecer el `status` a `'pending'` por defecto si no se ha definido.
* `local_timestamp` (propiedad): Retorna `self.timestamp` convertido a la zona horaria del `requested_by`.
* `calculated_turn_around_time` (propiedad): Calcula la diferencia entre `completed_at` y `effective_start_time_for_tat`.

### 5.3. `AddressValidationFile(models.Model)`
Permite adjuntar múltiples archivos a una solicitud de "Address Validation".
* `request`: `ForeignKey` a `UserRecordsRequest`.
* `uploaded_file`: `FileField` con `validate_file_size`.
* `uploaded_at`: `DateTimeField`.

### 5.4. Modelos de Historial de Acciones
* **`BlockedMessage`**: Registra información sobre bloqueos (quién, cuándo, razón).
* **`ResolvedMessage`**: Registra información sobre resoluciones (quién, cuándo, mensaje, archivo/enlace opcional).
* **`RejectedMessage`**: Registra información sobre rechazos (quién, cuándo, razón, `is_resolved_qa`).

### 5.5. `OperationPrice(models.Model)`
Modelo Singleton (`pk=1`) que almacena los precios unitarios para facturación al cliente y los costos internos de operación y QA.
* **Campos renombrados/actualizados:** `manual_property_update_price` (antes `manual_update_price`) y sus contrapartes de costo.
* **Nuevos campos de precio/costo:** `manual_unit_update_price`, `address_validation_unit_price`, `stripe_dispute_price`, `xml_file_price`, cada uno con sus correspondientes `_operate_cost` y `_qa_cost`.
* Todos los campos son `DecimalField` con `verbose_name` en inglés.

### 5.6. `SalesforceAttachmentLog(models.Model)`
Registra metadatos de archivos adjuntos de Salesforce vinculados a solicitudes de "Address Validation".
* `request`: `ForeignKey` a `UserRecordsRequest`.
* `file_name`, `file_extension`, `salesforce_file_link` (URL).

### 5.7. `ScheduledTaskToggle(models.Model)`
Permite habilitar o deshabilitar tareas programadas específicas desde el admin.
* `task_name`: `CharField` único, usado como clave primaria (ej. `'salesforce_sync_opportunities'`).
* `is_enabled`: `BooleanField` (default `True`).
* `last_modified`: `DateTimeField` (actualización automática).

---
## 6. Opciones Predefinidas (`tasks/choices.py`)

Este archivo es fundamental ya que centraliza todas las tuplas `choices` usadas en los campos `CharField` y `ChoiceField` de los modelos y formularios. Esto incluye `TYPE_CHOICES` para los tipos de proceso, `STATUS_CHOICES` para los estados de las solicitudes, `TEAM_CHOICES` para los equipos, `PRIORITY_CHOICES`, y muchas otras opciones específicas para cada tipo de solicitud (ej. `DEACTIVATION_TOGGLE_CHOICES`, `XML_STATE_CHOICES`, `PROPERTY_RECORDS_TYPE_CHOICES`, etc.). Mantener estas opciones en un solo lugar mejora la consistencia y facilita las modificaciones. El orden de las tuplas en `TEAM_CHOICES` y `TYPE_CHOICES` es ahora utilizado por la vista `client_cost_summary_view` para determinar el orden de visualización de los subtotales en la página de resumen de costos. Todos los textos legibles por el usuario en estas `choices` están en inglés.

---
## 7. Validadores (`tasks/validators.py`)

* **`validate_file_size(value)`**: Validador personalizado que asegura que los archivos subidos por los usuarios no excedan un límite predefinido (actualmente 10MB). Lanza una `ValidationError` si el archivo es demasiado grande. Se aplica a varios campos `FileField` en los modelos.

---
## 8. Formularios (`tasks/forms.py`)

Define los formularios Django para la entrada y validación de datos. Todos los `label` y `help_text` visibles por el usuario están definidos en inglés.

### 8.1. Formularios de Gestión de Usuario
* **`CustomUserChangeForm`**: Hereda de `UserChangeForm` para editar `username`, `email`, `first_name`, `last_name`, y `timezone`. Omite el campo `password`.
* **`CustomPasswordChangeForm`**: Hereda de `PasswordChangeForm` para el cambio seguro de contraseñas.

### 8.2. Formularios para la Creación de Solicitudes
Estos formularios están vinculados al modelo `UserRecordsRequest` (heredan de `forms.ModelForm`) o son `forms.Form` para estructuras más complejas.
* **`UserGroupForm(forms.Form)`**: Formulario no vinculado a modelo para un grupo de usuarios en "User Records". Campos: `type_of_request`, `user_email_addresses`, `access_level` (condicional), `properties`. Usado con `formset_factory`.
* **`UserRecordsRequestForm(forms.Form)`**: Para detalles generales al crear "User Records" (partner, instrucciones, adjuntos, prioridad, programación). **Ya no incluye `team_selection`**; la asignación y validación de equipo se maneja en la vista.
* **Formularios Específicos por Tipo (ej. `DeactivationToggleRequestForm`, `UnitTransferRequestForm`, `GeneratingXmlRequestForm`, `AddressValidationRequestForm`, `StripeDisputesRequestForm`, `PropertyRecordsRequestForm`):**
    * Heredan de `ModelForm` y definen los campos relevantes para cada `type_of_process`.
    * Implementan lógica de validación condicional en sus métodos `clean()` para asegurar que se proporcionen los datos correctos según las selecciones del usuario (ej. en `PropertyRecordsRequestForm`, los campos requeridos cambian según `property_records_type`).
    * Ya no incluyen `team_selection`; la lógica de equipo se maneja en la vista correspondiente.
    * Incluyen campos para `priority` y programación (`schedule_request`, `scheduled_date`) con validación.

### 8.3. Formularios para Acciones de Flujo de Trabajo y Operación
* **`BlockForm`, `ResolveForm`, `RejectForm`**: Formularios simples (`forms.Form`) para capturar razones o mensajes.
* **`OperateForm(forms.ModelForm)`**: Usado en modales para "Send to QA" y "Complete". Su método `__init__` personaliza los campos visibles y requeridos según el `type_of_process` de la solicitud.
    * Ha sido **actualizado** para manejar condicionalmente los campos de 'Address Validation' (ej. `av_number_of_units`) y 'Stripe Disputes' (ej. `stripe_premium_disputes`).
* **`GeneratingXmlOperateForm(forms.ModelForm)`**: Formulario especializado para las acciones "Send to QA" y "Complete" de solicitudes "Generating XML".
    * Maneja la subida/actualización de los archivos XML/ZIP generados (`operator_rvic_file_slot1`, etc.) a través de campos de archivo añadidos dinámicamente en `__init__` según el `xml_state` y los carriers de la solicitud.
    * Incluye el campo `qa_needs_file_correction` (checkbox) para el flujo donde QA indica que los archivos deben ser corregidos/re-subidos por el operador.
* **`OperationPriceForm(forms.ModelForm)`**: Para gestionar la instancia Singleton de `OperationPrice`. Lista todos los campos del modelo para edición, reflejando los campos renombrados y los nuevos.

---
## 9. Lógica de las Vistas (`tasks/views.py`)


### 9.1. Funciones Auxiliares y Control de Permisos
Se utilizan funciones helper como `is_admin(user)`, `is_leadership(user)`, `is_agent(user)`, `user_in_group(group_name)` y la nueva `user_is_admin_or_leader(user)` para verificar roles. Decoradores como `@login_required` y `@user_passes_test` con estas funciones restringen el acceso a las vistas. Los decoradores `user_belongs_to_revenue_or_support`, `user_belongs_to_compliance`, y `user_belongs_to_accounting` controlan el acceso a las vistas de creación de solicitudes por equipo.

### 9.2. Vistas Principales (Home, Profile, Choose Request Type)
* `home`: Página de inicio.
* `profile`: Gestión de perfil de usuario y cambio de contraseña.
* `choose_request_type`: Página de selección para iniciar la creación de una nueva solicitud.

### 9.3. Vistas de Creación de Solicitudes (Detalle por Tipo)
Cada tipo de solicitud tiene su propia vista de creación (ej. `user_records_request`, `deactivation_toggle_request`, etc.).
* **Lógica de Asignación de Equipo Actualizada:** Para los tipos de solicitud que dependen de los equipos Revenue o Support, si el usuario creador pertenece a ambos grupos, la vista ahora muestra un mensaje de error (`messages.error`) indicando la ambigüedad y redirige (probablemente al dashboard). Si el usuario pertenece solo a uno de estos equipos, el campo `team` de la solicitud se asigna automáticamente. El campo `team_selection` en los formularios ha sido eliminado.
* **Manejo de Programación:** Estas vistas procesan los campos `schedule_request` y `scheduled_date` de los formularios. Si una solicitud se programa, su `status` se establece a `'scheduled'`, se guarda `scheduled_date`, y `effective_start_time_for_tat` se deja como `None` (se establecerá cuando la tarea se active). Si no se programa, el `status` es `'pending'` (o `'pending_approval'` para ciertos tipos de "Deactivation/Toggle" que requieren aprobación de liderazgo y no son creados por un líder), y `effective_start_time_for_tat` se establece al momento de la creación.
* `address_validation_request` maneja la subida de múltiples archivos a través de `request.FILES.getlist('request_files')` y crea instancias `AddressValidationFile`.

### 9.4. Vistas de Visualización (Dashboard y Detalle de Solicitud)
* **`portal_operations_dashboard`**: Muestra una lista paginada de todas las solicitudes con filtros por tipo, estado, equipo y rango de fechas. Pasa las variables `is_admin_user` e `is_leadership_user` al contexto para controlar la visibilidad de la nueva columna de costos.
* **`request_detail`**: Muestra los detalles completos de una solicitud específica. Recupera la solicitud, su historial de acciones (bloqueos, resoluciones, rechazos), y datos específicos del tipo de proceso (como grupos de usuarios para "User Records" o archivos para "Address Validation"). Pasa múltiples variables de contexto para controlar la visibilidad de botones de acción y ahora también `is_admin_user` e `is_leadership_user` para la sección de costos. Para solicitudes "Generating XML", pasa una instancia de `GeneratingXmlOperateForm` (como `form_for_modal`) para ser usada en los modales de operación.

### 9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)
* **Nueva Vista Protegida:** Accesible solo para usuarios autenticados que sean `admin` o `leadership` (usando `@user_passes_test(user_is_admin_or_leader)`).
* **Filtros de Fecha:** Acepta `start_date` y `end_date` como parámetros GET. Si no se proporcionan, por defecto muestra los datos para el mes actual completo.
* **Cálculo de Costos:**
    * Filtra `UserRecordsRequest` por `status='completed'` y el rango de fechas.
    * Calcula el "Gran Total" sumando `grand_total_client_price_completed` de las solicitudes filtradas.
    * Calcula "Subtotales por Equipo" agrupando por `team` y sumando `grand_total_client_price_completed`. El orden de los equipos en la salida respeta el orden definido en `TEAM_CHOICES`.
    * Calcula "Subtotales por Tipo de Proceso" agrupando por `type_of_process` y sumando `grand_total_client_price_completed`. El orden de los procesos en la salida respeta el orden definido en `TYPE_CHOICES`.
* **Datos para Gráficos (Chart.js):**
    * Prepara listas de etiquetas (nombres de equipo/proceso) y datos (subtotales) para dos gráficos de tarta (pie charts).
    * Prepara datos para cinco gráficos de dispersión con líneas suavizadas (`type: 'line'` con `tension`). Cada gráfico es para un tipo de proceso principal ('address\_validation', 'user\_records', 'property\_records', 'unit\_transfer', 'deactivation\_toggle') y muestra dos series: una para el equipo "Revenue" y otra para "Support". Los puntos de datos son `(completed_at, grand_total_client_price_completed)` y cada punto incluye el `pk` de la solicitud para permitir la navegación a su detalle.
* **Contexto y Plantilla:** Pasa todos los datos calculados y la plantilla de URL para `request_detail` al contexto de `tasks/client_cost_summary.html`.

### 9.6. Vistas de Acciones del Flujo de Trabajo (Detalle por Acción)
Manejan los cambios de estado de las solicitudes.
* `operate_request`: Cambia estado a 'In Progress', asigna operador.
* `block_request`, `resolve_request`: Crean registros de historial y actualizan Salesforce si es 'Address Validation' y tiene `salesforce_standard_opp_id`.
* `send_to_qa_request`: Utiliza `OperateForm` o `GeneratingXmlOperateForm` para capturar detalles de operación. Cambia estado a 'QA Pending'. Para `GeneratingXmlOperateForm`, el campo `qa_needs_file_correction` se oculta ya que esta decisión la toma QA, no el operador al enviar.
* `qa_request`: Agente toma solicitud de 'QA Pending' a 'QA In Progress'.
* `complete_request`:
    * Usa `OperateForm` o `GeneratingXmlOperateForm`. Cambia estado a 'Completed'.
    * **Cálculo y Almacenamiento de Costos:** Al marcar como 'completed', obtiene la instancia de `OperationPrice`. Calcula todos los subtotales (precios al cliente, costos de operación, costos de QA) basados en los conteos de operación de la solicitud (ej. `num_updated_users`, `av_number_of_units`, `stripe_premium_disputes`, conteo de carriers para XML) y los precios/costos unitarios actuales de `OperationPrice`. Estos subtotales y los tres grandes totales se guardan en los nuevos campos `*_completed` del modelo `UserRecordsRequest`.
    * Actualiza Salesforce si es 'Address Validation'.
* `cancel_request`, `uncancel_request`, `reject_request`, `approve_deactivation_toggle`, `set_update_needed_flag`, `clear_update_needed_flag`.

---
## 10. Estructura y Contenido de las Plantillas (`tasks/templates/`)
Textos de UI directamente en inglés.

### 10.1. Plantilla Base (`base.html`)

Define la estructura común (navbar, footer, mensajes flash).
* **Nuevo Enlace "Cost Summary"**: Añadido a la barra de navegación. Visible solo si la variable de contexto `is_admin_user` o `is_leadership_user` es verdadera.

### 10.2. Plantillas de Creación de Solicitudes
* **`users_records_request.html`** (antes `users_records.html`): Para "User Records", usa `UserRecordsRequestForm` y `UserGroupFormSet`.
* Otras plantillas como `deactivation_toggle_request.html`, `unit_transfer_request.html`, `generating_xml_request.html`, `address_validation_request.html`, `stripe_disputes_request.html`, `property_records_request.html`. Todas incluyen JS para lógica condicional de campos y manejo de programación.

### 10.3. Plantilla del Dashboard (`rhino_operations_dashboard.html`)
(Antes `portal_operations_dashboard.html`).
* Muestra tabla de solicitudes con filtros.
* **Nueva Columna "Total Cost (Client)"**: Visible solo para `admin` o `leadership`. Muestra `grand_total_client_price_completed` para solicitudes completadas. `colspan` ajustado en mensaje `{% empty %}`.

### 10.4. Plantillas de Detalle de Solicitud
(ej. `user_records_detail.html`, `generating_xml_detail.html`, `address_validation_detail.html`, etc.)
* Muestran información completa de la solicitud, historial y botones de acción.
* **Nueva Sección "Price Breakdown"**:
    * Visible solo para `admin` o `leadership` y si `user_request.status == 'completed'`.
    * Presentada en una tarjeta centrada de ancho reducido (`col-lg-6 col-md-8`).
    * Muestra los subtotales `subtotal_*_client_price_completed` y el `grand_total_client_price_completed` almacenados en el modelo.
* Modales para acciones "Send to QA" / "Complete":
    * Para "Generating XML": usan `form_for_modal` (instancia de `GeneratingXmlOperateForm`). JS maneja visibilidad de `qa_needs_file_correction` y campos de archivo.
    * Para "Stripe Disputes": usan `OperateForm` adaptado para mostrar campos de conteo de disputas y notas.

### 10.5. Plantilla de Resumen de Gastos (`client_cost_summary.html`)
* Nueva plantilla con formulario de filtro de fechas.
* Muestra el gran total de `grand_total_client_price_completed`.
* Tablas/listas de subtotales por equipo y por tipo de proceso (ordenados según `CHOICES`).
* **Gráficos (Chart.js):**
    * Dos pie charts para distribución de costos por equipo y por tipo de proceso, con bordes negros.
    * Cinco gráficos de dispersión con líneas suavizadas (`type: 'line'`, `tension`) para los tipos de proceso 'address\_validation', 'user\_records', 'property\_records', 'unit\_transfer', y 'deactivation\_toggle'. Muestran `grand_total_client_price_completed` (eje Y) vs. `completed_at` (eje X, tipo 'time'). Cada gráfico tiene dos series: una para "Revenue" y otra para "Support".
    * **Hipervínculos en Scatter Plots:** Los puntos en los gráficos de dispersión son clicables y redirigen a la página de detalle de la solicitud correspondiente.
* **JavaScript (`extra_js`):**
    * Incluye Chart.js y el adaptador de tiempo `chartjs-adapter-date-fns` vía CDN.
    * Inicializa todos los gráficos (2 pie, 5 scatter) con los datos pasados desde la vista (usando `|json_script`).
    * Configura el `onClick` y `onHover` para los scatter plots para la funcionalidad de hipervínculos y cambio de cursor.
    * Configura el formateo de tooltips y ejes para moneda y fechas.

---
## 11. Tareas Programadas y en Segundo Plano (`django-q2`)

### 11.1. `tasks/scheduled_jobs.py`

* `process_scheduled_requests()`: Cambia el estado de solicitudes programadas (`status='scheduled'`) a `'pending'` cuando `scheduled_date` es hoy o anterior, y establece `effective_start_time_for_tat`.

### 11.2. `tasks/salesforce_sync.py`

* `sync_salesforce_opportunities_task()`:
    * **Funcionalidad completada y probada.**
    * **Control de Pausa/Reanudación:** Al inicio, verifica el modelo `ScheduledTaskToggle` (para `task_name='salesforce_sync_opportunities'`). Si `is_enabled` es `False`, la tarea registra que está pausada y no continúa.
    * Se conecta a Salesforce, ejecuta una consulta SOQL para obtener Opportunities específicas, y para cada una:
        * Crea una `UserRecordsRequest` de tipo `'address_validation'`, mapeando campos relevantes.
        * Crea registros `SalesforceAttachmentLog` para los archivos adjuntos de la Opportunity.
        * Actualiza un campo en la Opportunity de Salesforce para marcarla como procesada.

### 11.3. `tasks/apps.py` (Configuración de Tareas)

* Dentro del método `ready()` de `TasksConfig(AppConfig)`:
    * Se asegura de que `django_q` esté en `INSTALLED_APPS`.
    * Crea o verifica la existencia de las tareas programadas en el modelo `Schedule` de `django-q2`:
        * `process_scheduled_requests`: Se ejecuta diariamente a la 1:00 PM UTC (`Schedule.DAILY`).
        * `sync_salesforce_opportunities_task`: Se ejecuta tres veces al día (1 PM, 4 PM, 7 PM UTC) usando `Schedule.CRON` con la expresión `'0 13,16,19 * * *'`.

---
## 12. Interfaz de Administración de Django (`tasks/admin.py`)

Personalizaciones para facilitar la gestión de datos.
* **`CustomUserAdmin`**: Muestra `timezone` en la lista y formularios de edición.
* **`UserRecordsRequestAdmin`**:
    * `list_display`, `list_filter`, `search_fields` configurados para fácil acceso.
    * **`readonly_fields` y `fieldsets` actualizados para incluir los nuevos campos de costos `*_completed`** y otros campos de solo lectura para mantener la integridad de los datos.
    * Inlines para `AddressValidationFile`, `BlockedMessage`, `ResolvedMessage`, `RejectedMessage`.
    * Acciones personalizadas para disparar manualmente `sync_salesforce_opportunities_task` y `process_scheduled_requests`.
* **`OperationPriceAdmin`**: `fieldsets` actualizados para los nuevos campos de precios/costos y el campo renombrado.
* **`ScheduledTaskToggleAdmin`**: Nueva clase admin para gestionar el modelo `ScheduledTaskToggle`, permitiendo habilitar/deshabilitar tareas programadas desde el admin. `list_display` incluye `task_name`, `is_enabled_display`, `last_modified`. `is_enabled` es editable en la lista. `task_name` es no editable después de la creación.
* Otros admins (`HistoryMessageAdmin`, `SalesforceAttachmentLogAdmin`) con sus configuraciones.

---
## 13. Configuración del Entorno de Desarrollo
*(Pasos estándar: clonar el repositorio, crear y activar un entorno virtual Python, instalar dependencias con `pip install -r requirements.txt`, crear y configurar un archivo `.env` con variables como `DJANGO_SECRET_KEY` y `DJANGO_DEBUG`, aplicar migraciones de base de datos con `python manage.py migrate`, crear un superusuario con `python manage.py createsuperuser`, ejecutar el servidor de desarrollo con `python manage.py runserver`, y ejecutar el cluster de Django-Q2 en una terminal separada con `python manage.py qcluster`)*.

---
## 14. Despliegue (Heroku)
*(La aplicación está preparada para el despliegue en Heroku. Requiere un `Procfile` (con entradas para `web`, `worker`, y `release`), un archivo `runtime.txt` para especificar la versión de Python, y un `requirements.txt` actualizado. El archivo `settings.py` está configurado para adaptarse a variables de entorno de Heroku para `DATABASE_URL`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, etc. El archivo `yender.yaml` ha sido eliminado. Se necesitarán buildpacks de Heroku (Python) y add-ons (Heroku Postgres).)*

---
## 15. Consideraciones Adicionales y Próximos Pasos
* Realizar pruebas exhaustivas de todas las funcionalidades, especialmente los nuevos cálculos de costos, la página de resumen de gastos con sus filtros y gráficos, y la integración con Salesforce.
* Evaluar el rendimiento de las consultas para la página de resumen de costos, especialmente si el volumen de solicitudes completadas es alto, y optimizar si es necesario (ej. con índices de base de datos adicionales).
* Si se decide implementar la internacionalización completa, se deberán aplicar las etiquetas `{% trans %}` en todas las plantillas y gestionar los archivos de traducción `.po`.
* Planificar e implementar un sistema de notificaciones por correo electrónico para alertar a los usuarios sobre eventos importantes.
* Continuar el refinamiento de la interfaz de usuario (UI) y la experiencia de usuario (UX) basado en el feedback.
* Crear documentación detallada y guías para los usuarios finales de la plataforma.

---