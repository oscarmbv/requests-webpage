# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** Analizado el 1 de junio de 2025 (con las últimas implementaciones de notificaciones)
**Fecha de Actualización del README:** 1 de junio de 2025
**Documento de Referencia Principal:** "Descripción Detallada de la Plataforma de Gestión de Solicitudes (requests_webpage)" v2.3 (20 de mayo de 2025), adaptado y actualizado según el estado actual del código.

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
    * [3.12. Configuración de Email y Telegram para Notificaciones](#312-configuración-de-email-y-telegram-para-notificaciones)
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
        * [5.4.1. `BlockedMessage`](#541-blockedmessage)
        * [5.4.2. `ResolvedMessage`](#542-resolvedmessage)
        * [5.4.3. `RejectedMessage`](#543-rejectedmessage)
    * [5.5. `OperationPrice(models.Model)`](#55-operationpricemodelsmodel)
    * [5.6. `SalesforceAttachmentLog(models.Model)`](#56-salesforceattachmentlogmodelsmodel)
    * [5.7. `ScheduledTaskToggle(models.Model)`](#57-scheduledtasktogglemodelsmodel)
    * [5.8. `NotificationToggle(models.Model)`](#58-notificationtogglemodelsmodel)
6.  [Definición Centralizada de Opciones (`tasks/choices.py`)](#6-definición-centralizada-de-opciones-taskschoicespy)
    * [6.1. Opciones de Modelos y Formularios](#61-opciones-de-modelos-y-formularios)
    * [6.2. Claves de Eventos de Notificación](#62-claves-de-eventos-de-notificación)
7.  [Validadores Personalizados (`tasks/validators.py`)](#7-validadores-personalizados-tasksvalidatorspy)
8.  [Formularios Detallados (`tasks/forms.py`)](#8-formularies-detallados-tasksformspy)
    * [8.1. Formularios de Gestión de Usuario](#81-formularios-de-gestión-de-usuario)
    * [8.2. Formularios para la Creación de Solicitudes](#82-formularios-para-la-creación-de-solicitudes)
    * [8.3. Formularios para Acciones de Flujo de Trabajo y Operación](#83-formularios-para-acciones-de-flujo-de-trabajo-y-operación)
    * [8.4. Formulario para Proveer Actualización (`ProvideUpdateForm`)](#84-formulario-para-proveer-actualización-provideupdateform)
9.  [Lógica de las Vistas (`tasks/views.py`)](#9-lógica-de-las-vistas-tasksviewspy)
    * [9.1. Funciones Auxiliares y Control de Permisos](#91-funciones-auxiliares-y-control-de-permisos)
    * [9.2. Vistas Principales (Home, Profile, Choose Request Type)](#92-vistas-principales-home-profile-choose-request-type)
    * [9.3. Vistas de Creación de Solicitudes](#93-vistas-de-creación-de-solicitudes)
    * [9.4. Vistas de Visualización (Dashboard y Detalle de Solicitud)](#94-vistas-de-visualización-dashboard-y-detalle-de-solicitud)
    * [9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)](#95-vista-de-resumen-de-gastos-del-cliente-client_cost_summary_view)
    * [9.6. Vistas de Generación de Reportes CSV](#96-vistas-de-generación-de-reportes-csv)
    * [9.7. Vistas de Acciones del Flujo de Trabajo](#97-vistas-de-acciones-del-flujo-de-trabajo)
        * [9.7.1. Integración de Notificaciones en Vistas de Acción](#971-integración-de-notificaciones-en-vistas-de-acción)
10. [Módulo de Notificaciones (`tasks/notifications.py`)](#10-módulo-de-notificaciones-tasksnotificationspy)
    * [10.1. Funciones Helper de Notificación](#101-funciones-helper-de-notificación)
    * [10.2. Funciones Específicas de Notificación por Evento](#102-funciones-específicas-de-notificación-por-evento)
    * [10.3. Lógica de Control de Envío de Correos (Toggles)](#103-lógica-de-control-de-envío-de-correos-toggles)
11. [Estructura y Contenido de las Plantillas (`tasks/templates/`)](#11-estructura-y-contenido-de-las-plantillas-taskstemplates)
    * [11.1. Plantilla Base (`base.html`)](#111-plantilla-base-basehtml)
    * [11.2. Plantillas de Creación de Solicitudes](#112-plantillas-de-creación-de-solicitudes)
    * [11.3. Plantilla del Dashboard (`rhino_operations_dashboard.html`)](#113-plantilla-del-dashboard-rhino_operations_dashboardhtml)
    * [11.4. Plantillas de Detalle de Solicitud (`*_detail.html`)](#114-plantillas-de-detalle-de-solicitud-request_detailhtml)
        * [11.4.1. Modal para "Provide Update"](#1141-modal-para-provide-update)
    * [11.5. Plantilla de Resumen de Gastos (`client_cost_summary.html`)](#115-plantilla-de-resumen-de-gastos-client_cost_summaryhtml)
    * [11.6. Plantillas para Formularios de Reportes CSV](#116-plantillas-para-formularios-de-reportes-csv)
    * [11.7. Plantillas de Correo Electrónico (`tasks/templates/tasks/emails/`)](#117-plantillas-de-correo-electrónico-taskstemplatestasksemails)
12. [Tareas Programadas y en Segundo Plano (`django-q2`)](#12-tareas-programadas-y-en-segundo-plano-django-q2)
    * [12.1. Procesamiento de Solicitudes Programadas (`tasks/scheduled_jobs.py`)](#121-procesamiento-de-solicitudes-programadas-tasksscheduled_jobspy)
    * [12.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)](#122-sincronización-con-salesforce-taskssalesforce_syncpy)
    * [12.3. Configuración de Programación de Tareas (`tasks/apps.py`)](#123-configuración-de-programación-de-tareas-tasksappspy)
        * [12.3.1. Creación de Instancias `NotificationToggle`](#1231-creación-de-instancias-notificationtoggle)
    * [12.4. Hooks de Tareas (Opcional - `tasks/hooks.py`)](#124-hooks-de-tareas-opcional---taskshookspy)
13. [Interfaz de Administración de Django (`tasks/admin.py`)](#13-interfaz-de-administración-de-django-tasksadminpy)
    * [13.1. `NotificationToggleAdmin`](#131-notificationtoggleadmin)
14. [Configuración del Entorno de Desarrollo](#14-configuración-del-entorno-de-desarrollo)
15. [Despliegue (Heroku)](#15-despliegue-heroku)
16. [Consideraciones Adicionales y Próximos Pasos](#16-consideraciones-adicionales-y-próximos-pasos)

---

## 1. Introducción y Propósito

La plataforma `requests_webpage` es una aplicación web integral, desarrollada sobre el robusto framework Django, concebida como una solución centralizada y altamente adaptable para la gestión eficiente de una diversidad de procesos y solicitudes operativas internas. El sistema permite a los usuarios la creación, el seguimiento detallado y la administración de múltiples tipos de solicitudes, cada una con flujos de trabajo, campos de datos específicos y lógicas de asignación a los equipos responsables dentro de la organización, como Revenue, Support, Compliance y Accounting.

Entre sus funcionalidades principales se encuentran la identificación unívoca de cada solicitud mediante un código, un sistema de priorización (Low, Normal, High), la capacidad de adjuntar archivos o proporcionar enlaces URL como parte de la información de la solicitud, y un registro exhaustivo del historial de acciones (bloqueos, resoluciones, rechazos) para cada una. La plataforma incorpora características avanzadas tales como la programación de solicitudes para su activación automática en fechas futuras, el cálculo preciso de Tiempos de Respuesta (Turn Around Time - TAT) basados en el inicio efectivo del trabajo y la fecha de completitud, y una integración funcional con Salesforce. Esta integración automatiza la creación de solicitudes de tipo "Validación de Direcciones" (Address Validation) directamente a partir de Opportunities en Salesforce, incluyendo la sincronización de archivos adjuntos relevantes.

Una adición significativa es un **sistema de notificaciones por eventos**, que informa a los usuarios relevantes sobre cambios importantes en el ciclo de vida de las solicitudes a través de **correo electrónico y mensajes de Telegram**. Actualmente, se han implementado notificaciones para 13 eventos clave:
1.  Nueva solicitud creada (manual o desde Salesforce).
2.  Solicitud de "Deactivation/Toggle" pendiente de aprobación.
3.  Solicitud de "Deactivation/Toggle" aprobada.
4.  Solicitud programada activada (cambia de 'Scheduled' a 'Pending').
5.  Se solicita una actualización para una tarea.
6.  Se provee una actualización para una tarea (con mensaje del proveedor).
7.  Solicitud bloqueada.
8.  Solicitud bloqueada resuelta.
9.  Solicitud enviada a QA.
10. Solicitud rechazada (desde QA o similar).
11. Solicitud cancelada.
12. Solicitud descancelada.
13. Solicitud completada.

El envío de correos electrónicos para cada uno de estos eventos puede ser **activado o desactivado individualmente desde el panel de administración de Django** a través del nuevo modelo `NotificationToggle`, permitiendo una gestión flexible de los límites de envío de servicios de correo transaccional como SendGrid. Las notificaciones de Telegram, por ahora, se envían independientemente de estos toggles de correo.

Se ha mejorado la interacción del usuario para el evento "Update Provided", donde ahora se presenta un formulario modal para que el usuario ingrese un mensaje de actualización que se incluye en la notificación correspondiente.

También se ha implementado un sistema para el cálculo y almacenamiento persistente de los costos asociados a cada solicitud. Estos costos, desglosados en precios al cliente, costos de operación interna y costos de QA interna, se "congelan" en el momento en que una solicitud es marcada como completada. Esta información financiera es accesible a través de un reporte de "Resumen de Gastos del Cliente" restringido a usuarios con roles administrativos o de liderazgo, y ofrece filtros por rango de fechas, con visualización de subtotales por equipo y por tipo de proceso mediante gráficos.

La plataforma se apoya en `django-q2` para la gestión de tareas en segundo plano y programadas, asegurando que procesos como la activación automática de solicitudes programadas, la sincronización periódica con Salesforce, y el envío asíncrono de las 13 tipos de notificaciones implementadas se ejecuten de manera fiable.

---

## 2. Estructura Detallada del Proyecto
La aplicación sigue una estructura de proyecto Django bien definida para promover la organización y la mantenibilidad del código.
* **`requests_webpage/` (Directorio Raíz del Proyecto):** Contiene todos los archivos y carpetas del proyecto.
    * **`requests_webpage/` (Directorio de Configuración del Proyecto):**
        * `__init__.py`: Indica a Python que este directorio debe ser tratado como un paquete.
        * `settings.py`: Archivo principal de configuración de Django.
        * `urls.py`: Archivo de enrutamiento de URLs a nivel de proyecto.
        * `wsgi.py`: Punto de entrada para servidores web compatibles con WSGI para el despliegue.
        * `asgi.py`: Punto de entrada para servidores web compatibles con ASGI, para funcionalidades asíncronas de Django.
    * **`tasks/` (Aplicación Principal):** Contiene la lógica de negocio central de la plataforma.
        * `__init__.py`: Marca el directorio `tasks` como un paquete Python.
        * `admin.py`: Define cómo se muestran y gestionan los modelos de la aplicación `tasks` en el sitio de administración de Django.
        * `apps.py`: Archivo de configuración para la aplicación `tasks`. Aquí se inicializan las tareas programadas de `django-q2` y los `NotificationToggle` iniciales.
        * `choices.py`: Centraliza las constantes para las opciones (`choices`) de los campos de los modelos y las claves de eventos de notificación.
        * `context_processors.py`: Contiene funciones que añaden variables al contexto de las plantillas de forma global.
        * `forms.py`: Define los formularios Django que se utilizan para la entrada y validación de datos del usuario.
        * `hooks.py`: (Opcional, pero implementado) Contiene funciones hook para las tareas de `django-q2` (ej. `print_task_result`) que registran el resultado de las tareas asíncronas.
        * `models.py`: Define los modelos ORM de Django, que representan la estructura de las tablas de la base de datos.
        * `notifications.py`: **Nuevo archivo crucial** que centraliza toda la lógica para construir y enviar las 13 tipos de notificaciones por correo electrónico y Telegram, incluyendo la verificación de los `NotificationToggle`.
        * `salesforce_sync.py`: Contiene la lógica específica para la tarea de sincronización con Salesforce, ahora también llama a la función de notificación de nueva solicitud.
        * `scheduled_jobs.py`: Define las funciones que se ejecutan como tareas programadas. La función `process_scheduled_requests` ahora también llama a la función de notificación correspondiente.
        * `tests.py`: Contiene pruebas unitarias y de integración para la aplicación `tasks`.
        * `urls.py`: Define los patrones de URL específicos para la aplicación `tasks`.
        * `validators.py`: Contiene validadores personalizados para campos de modelos o formularios.
        * `migrations/`: Directorio que almacena los archivos de migración de la base de datos.
        * `static/tasks/`: Directorio para archivos estáticos (CSS, JavaScript, imágenes) específicos de la aplicación `tasks`.
        * `templates/tasks/`: Directorio que contiene las plantillas HTML para la interfaz de usuario de la aplicación `tasks`.
            * `emails/`: **Nuevo directorio** que contiene las plantillas HTML y de texto plano para las 13 notificaciones por correo electrónico (ej. `new_request_created.html`, `request_approved_notification.txt`, etc.).
            * `registration/`: Contiene plantillas personalizadas para el flujo de autenticación.
        * `templatetags/`: Contiene tags y filtros de plantillas personalizados, como `duration_filters.py`.
    * `manage.py`: Utilidad de línea de comandos de Django para interactuar con el proyecto.
    * `.env`: (No versionado) Archivo para almacenar variables de entorno sensibles.
    * `requirements.txt`: Lista todas las dependencias de Python del proyecto.
    * `README.md`: Este archivo.

---
## 3. Configuración Central del Proyecto (`requests_webpage/settings.py`)

Este archivo define la configuración global del proyecto Django.

### 3.1. Variables Fundamentales y de Entorno
* **`BASE_DIR`**: Determina la ruta base del proyecto.
* **`environ.Env`**: Se utiliza `django-environ` para gestionar las variables de entorno, permitiendo cargar configuraciones desde un archivo `.env` en desarrollo y desde el entorno del sistema en producción.
* **`SECRET_KEY`**: Clave criptográfica esencial para la seguridad de Django, cargada desde el entorno.
* **`DEBUG`**: Booleano que activa (True) o desactiva (False) el modo de depuración, cargado desde el entorno.
* **`ALLOWED_HOSTS`**: Lista de nombres de host/dominio permitidos para servir la aplicación. Se configura para desarrollo (`127.0.0.1`, `localhost`) y se adapta para producción (ej. `'.herokuapp.com'`).
* **`CSRF_TRUSTED_ORIGINS`**: Lista de orígenes confiables para solicitudes seguras (HTTPS) al modificar datos, importante para producción.

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)
Es una lista de todas las aplicaciones Django que componen el proyecto.
* Aplicaciones estándar de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`.
* Aplicaciones de terceros:
    * `'whitenoise.runserver_nostatic'`: Para servir archivos estáticos durante el desarrollo de manera similar a producción.
    * `'django_q'`: La aplicación `django-q2` para la gestión de tareas en segundo plano y programadas.
* Aplicación principal del proyecto: `'tasks'`.

### 3.3. Middleware
Define una serie de capas que procesan secuencialmente las solicitudes HTTP entrantes y las respuestas salientes.
* `django.middleware.security.SecurityMiddleware`
* `whitenoise.middleware.WhiteNoiseMiddleware`: Para servir archivos estáticos eficientemente en producción.
* `django.contrib.sessions.middleware.SessionMiddleware`
* `django.middleware.common.CommonMiddleware`
* `django.middleware.csrf.CsrfViewMiddleware`
* `django.contrib.auth.middleware.AuthenticationMiddleware`
* `django.contrib.messages.middleware.MessageMiddleware`
* `django.middleware.clickjacking.XFrameOptionsMiddleware`
* `django.middleware.locale.LocaleMiddleware`: Habilita la internacionalización.

### 3.4. Autenticación y Modelo de Usuario
* `AUTH_USER_MODEL = 'tasks.CustomUser'`: Indica a Django que use el modelo `CustomUser` de la app `tasks`.
* `LOGOUT_REDIRECT_URL = '/accounts/login/'`: URL de redirección tras cerrar sesión.
* `LOGIN_REDIRECT_URL = '/rhino/dashboard/'`: URL de redirección tras iniciar sesión.

### 3.5. Configuración de Base de Datos
* `DATABASES`: Configurada usando `dj_database_url.config()`, permitiendo leer desde `DATABASE_URL` (ideal para Heroku).
* Fallback a SQLite para desarrollo local.
* `conn_max_age=600` y opciones SSL para PostgreSQL.

### 3.6. Gestión de Archivos Estáticos y Multimedia
* **Archivos Estáticos:**
    * `STATIC_URL = 'static/'`.
    * `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`.
    * `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`.
* **Archivos Multimedia:**
    * `MEDIA_URL = '/media/'`.
    * `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')`.

### 3.7. Internacionalización (i18n) y Localización (l10n)
* `LANGUAGE_CODE = 'en-us'`.
* `TIME_ZONE = 'UTC'`.
* `USE_I18N = True`, `USE_TZ = True`.

### 3.8. Tareas en Segundo Plano (Django-Q2)
* `Q_CLUSTER`: Diccionario que configura el cluster de `django-q2`, incluyendo nombre, workers, timeout, reintentos, y nivel de log.

### 3.9. Integración con Salesforce
* Credenciales (`SF_USERNAME`, `SF_PASSWORD`, etc.) se cargan desde el entorno.
* `SALESFORCE_LIGHTNING_BASE_URL` para construir enlaces.

### 3.10. Configuración de Logging
* Configuración detallada para `LOGGING` con formateadores (`verbose`, `simple`, `qcluster`), manejadores (`console`, `file_tasks`), y loggers específicos para `django`, `django.request`, `tasks`, y `django_q`.

### 3.11. Procesadores de Contexto de Plantillas
* `'tasks.context_processors.user_role_permissions'` añadido para hacer disponibles `is_admin_user` e `is_leadership_user` globalmente en las plantillas.

### 3.12. Configuración de Email y Telegram para Notificaciones
* **Email (SendGrid):**
    * `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`
    * `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER` (usualmente `'apikey'`), `EMAIL_HOST_PASSWORD` (la clave API de SendGrid) se cargan desde variables de entorno.
    * `DEFAULT_FROM_EMAIL`: Dirección de remitente verificada en SendGrid.
* **Telegram:**
    * `TELEGRAM_BOT_TOKEN`: El token API del bot de Telegram, cargado desde variables de entorno.
    * `TELEGRAM_DEFAULT_CHAT_ID`: Un chat ID por defecto (ej. para admin o un grupo de pruebas), cargado desde variables de entorno.
* **`SITE_DOMAIN`**: Variable de entorno (ej. `SITE_DOMAIN='https://tu-app.herokuapp.com'`) utilizada para construir URLs absolutas en las notificaciones enviadas desde tareas en segundo plano.

---
## 4. Enrutamiento de URLs (`urls.py`)

### 4.1. Enrutador Principal del Proyecto (`requests_webpage/urls.py`)

Este archivo es el punto de entrada para el sistema de URLs de Django.
* `path('admin/', admin.site.urls)`: Activa el sitio de administración de Django.
* `path('accounts/', include('django.contrib.auth.urls'))`: Incluye las URLs predefinidas de Django para la autenticación.
* `path('rhino/', include('tasks.urls', namespace='tasks'))`: Todas las URLs definidas en `tasks/urls.py` están prefijadas con `/rhino/`. El `namespace='tasks'` permite usar nombres de URL cualificados.
* `path('', tasks_views.home, name='home')`: Define la vista para la página de inicio del sitio.

### 4.2. Enrutador de la Aplicación `tasks` (`tasks/urls.py`)

Contiene los patrones de URL específicos para la aplicación `tasks`, relativos a `/rhino/`.
* `app_name = 'tasks'`.
* **Autenticación:** `login`, `logout`.
* **Vistas Principales y de Usuario:** `rhino_dashboard` (antes `portal_dashboard`), `profile`, `manage_prices`, `client_cost_summary`.
* **Vistas de Generación de Reportes CSV:** `revenue_support_report`, `compliance_xml_report`, `accounting_stripe_report`.
* **Vistas de Creación de Solicitudes:** `choose_request_type` y rutas específicas para los 7 tipos de proceso (`user_records_request`, `deactivation_toggle_request`, etc.).
* **Vistas de Detalle y Acciones sobre Solicitudes:** `request_detail` y sub-rutas para acciones como `operate`, `block`, `send_to_qa`, `complete`, `cancel`, etc.

---
## 5. Modelo de Datos Detallado (`tasks/models.py`)

Describe la estructura de la base de datos de la aplicación `tasks`.

### 5.1. `CustomUser(AbstractUser)`
Modelo de usuario personalizado que extiende `AbstractUser` de Django.
* **Campos Principales:**
    * `email`: `EmailField(unique=True)`. Se utiliza como `USERNAME_FIELD` para la autenticación.
    * `timezone`: `CharField(max_length=100, default='UTC', choices=...)`. Almacena la zona horaria preferida del usuario, con `choices` generadas a partir de `pytz.common_timezones`.
* `REQUIRED_FIELDS = ['username']`: Aunque el login es por email, `username` sigue siendo requerido por Django.

### 5.2. `UserRecordsRequest(models.Model)`
Es el modelo central que representa todas las solicitudes operativas dentro de la plataforma. Este modelo es extenso y ha sido diseñado para ser flexible y cubrir una amplia gama de necesidades de seguimiento y procesamiento.

#### 5.2.1. Atributos Generales de Identificación y Estado
* `type_of_process`: `CharField`. Define la naturaleza de la solicitud (ej. 'user_records', 'address_validation'). Utiliza `TYPE_CHOICES` definidas en `tasks.choices`.
* `unique_code`: `CharField`. Un código único generado automáticamente para cada solicitud, con un prefijo basado en `type_of_process`.
* `timestamp`: `DateTimeField`. Fecha y hora de creación de la solicitud.
* `requested_by`: `ForeignKey` a `CustomUser`. El usuario que creó la solicitud.
* `team`: `CharField`. El equipo asignado para procesar la solicitud (ej. 'Revenue', 'Support'). Utiliza `TEAM_CHOICES`.
* `priority`: `CharField`. Prioridad de la solicitud (ej. 'Low', 'Normal', 'High'). Utiliza `PRIORITY_CHOICES`.
* `partner_name`: `CharField`. Nombre del socio o cliente asociado a la solicitud.
* `properties`: `TextField`. Lista de propiedades afectadas, relevante para varios tipos de procesos.
* `user_groups_data`: `JSONField`. Almacena datos estructurados para solicitudes de tipo "User Records".
* `special_instructions`: `TextField`. Instrucciones especiales o comentarios adicionales.
* `status`: `CharField`. El estado actual de la solicitud en el flujo de trabajo (ej. 'Pending', 'In Progress', 'Completed'). Utiliza `STATUS_CHOICES`.
* `user_file`: `FileField`. Para subir un archivo principal asociado con la solicitud (ej. una hoja de cálculo).
* `user_link`: `URLField`. Para proporcionar un enlace a un recurso externo (ej. Google Sheets).

#### 5.2.2. Atributos de Flujo de Trabajo, Asignación y Programación
* `update_needed_flag`: `BooleanField`. Indica si se ha solicitado una actualización de progreso para esta tarea.
* `update_requested_by`: `ForeignKey` a `CustomUser`. El usuario que solicitó la actualización.
* `update_requested_at`: `DateTimeField`. Cuándo se solicitó la actualización.
* `scheduled_date`: `DateField`. Fecha para la cual la solicitud está programada para activarse (pasar a 'Pending').
* `effective_start_time_for_tat`: `DateTimeField`. Timestamp que marca el inicio real del ciclo de trabajo para el cálculo del TAT.
* `operator`: `ForeignKey` a `CustomUser`. El agente asignado para operar/procesar la solicitud.
* `qa_agent`: `ForeignKey` a `CustomUser`. El agente asignado para realizar el control de calidad (QA).
* Timestamps de flujo de trabajo: `operated_at`, `qa_pending_at`, `qa_in_progress_at`, `completed_at`, `cancelled_at`, `uncanceled_at`.
* Detalles de cancelación: `cancelled` (Boolean), `cancelled_by` (`ForeignKey` a `CustomUser`), `cancel_reason` (`TextField`), `uncanceled_by` (`ForeignKey` a `CustomUser`).
* `is_rejected_previously`: `BooleanField`. Indica si la solicitud fue rechazada previamente por QA.

#### 5.2.3. Atributos para Detalles de Operación y QA
Campos `PositiveIntegerField` para registrar conteos de operaciones: `num_updated_users`, `num_updated_properties`, `bulk_updates`, `manual_updated_properties`, `manual_updated_units`, `update_by_csv_rows`, `processing_reports_rows`.
* `operator_spreadsheet_link`: `URLField`. Enlace a una hoja de cálculo utilizada por el operador.
* `operating_notes`: `TextField`. Notas del operador o del agente de QA.

#### 5.2.4. Atributos Específicos por Tipo de Proceso (`type_of_process`)
El modelo `UserRecordsRequest` incluye un conjunto de campos que son específicos para ciertos tipos de proceso. Todos son opcionales (`null=True, blank=True`) a nivel de base de datos, y su relevancia y obligatoriedad se manejan en los formularios y la lógica de las vistas.
* **Deactivation/Toggle**: `deactivation_toggle_type` (usando `DEACTIVATION_TOGGLE_CHOICES`), `deactivation_toggle_active_policies` (Boolean), `deactivation_toggle_properties_with_policies` (Text), `deactivation_toggle_context` (Text), `deactivation_toggle_leadership_approval` (usando `LEADERSHIP_APPROVAL_CHOICES`), `deactivation_toggle_marked_as_churned` (Boolean).
* **Unit Transfer**: `unit_transfer_type` (usando `UNIT_TRANSFER_TYPE_CHOICES`), `unit_transfer_new_partner_prospect_name` (Char), `unit_transfer_receiving_partner_psm` (Char), `unit_transfer_new_policyholders` (Text), `unit_transfer_user_email_addresses` (Text), `unit_transfer_prospect_portfolio_size` (PositiveInt), `unit_transfer_prospect_landlord_type` (usando `UNIT_TRANSFER_LANDLORD_TYPE_CHOICES`), `unit_transfer_proof_of_sale` (URL).
* **Generating XML**: `xml_state` (usando `XML_STATE_CHOICES`), `xml_carrier_rvic` (Boolean), `xml_carrier_ssic` (Boolean), `xml_rvic_zip_file` (FileField), `xml_ssic_zip_file` (FileField). También incluye campos para los archivos de salida del operador: `operator_rvic_file_slot1`, `operator_rvic_file_slot2`, `operator_ssic_file_slot1`, `operator_ssic_file_slot2`.
* **Address Validation (Campos de entrada manual/custom)**: `address_validation_policyholders` (Text), `address_validation_opportunity_id` (Char, para el ID de Oportunidad personalizado si no viene de SF), `address_validation_user_email_addresses` (Text).
* **Stripe Disputes**: `stripe_premium_disputes` (PositiveInt), `stripe_ri_disputes` (PositiveInt).
* **Property Records**: `property_records_type` (usando `PROPERTY_RECORDS_TYPE_CHOICES`), `property_records_new_names` (Text), `property_records_new_pmc` (Char), `property_records_new_policyholder` (Text), `property_records_corrected_address` (Text), `property_records_updated_type` (usando `PROPERTY_TYPE_CHOICES`), `property_records_units` (Text), `property_records_coverage_type` (usando `COVERAGE_TYPE_CHOICES`), `property_records_coverage_multiplier` (usando `COVERAGE_MULTIPLIER_CHOICES`), `property_records_coverage_amount` (DecimalField con validadores Min/Max), `property_records_integration_type` (usando `INTEGRATION_TYPE_CHOICES`), `property_records_integration_codes` (Text), `property_records_bank_details` (Text).

#### 5.2.5. Atributos para la Integración con Salesforce
Estos campos se utilizan principalmente para solicitudes de tipo `'address_validation'` originadas desde Salesforce.
* **Información de la Opportunity de Salesforce:**
    * `salesforce_standard_opp_id`: `CharField(max_length=18)`. El ID estándar de 18 caracteres de la Opportunity.
    * `salesforce_opportunity_name`: `CharField`.
    * `salesforce_number_of_units`: `PositiveIntegerField`.
    * `salesforce_link`: `URLField`. Enlace directo a la Opportunity en Salesforce Lightning.
    * `salesforce_account_manager`: `CharField`.
    * `salesforce_closed_won_date`: `DateField`.
    * `salesforce_leasing_integration_software`: `CharField`.
    * `salesforce_information_needed_for_assets`: `TextField`.
* **Campos de Salida de Operación (relacionados con Salesforce para Address Validation):**
    * `assets_uploaded`: `BooleanField`. Indica si los activos se subieron a Salesforce.
    * `av_number_of_units`: `PositiveIntegerField`. Número de unidades procesadas en la operación de validación.
    * `av_number_of_invalid_units`: `PositiveIntegerField`. Número de unidades inválidas encontradas.
    * `link_to_assets`: `URLField`. Enlace a los activos generados (ej. Google Sheet).
    * `success_output_link`: `URLField`. Enlace a la salida de unidades exitosas.
    * `failed_output_link`: `URLField`. Enlace a la salida de unidades fallidas.
    * `rhino_accounts_created`: `BooleanField`. Indica si se crearon cuentas Rhino.

#### 5.2.6. Atributos para Costos Calculados en Finalización
Estos campos `DecimalField` se rellenan cuando una solicitud se marca como 'Completed'. Almacenan una "instantánea" de los costos en ese momento.
* **Client Price Subtotals y Grand Total:** 10 campos de subtotales (ej. `subtotal_user_update_client_price_completed`) y `grand_total_client_price_completed`.
* **Operate Cost Subtotals y Grand Total:** 10 campos de subtotales (ej. `subtotal_user_update_operate_cost_completed`) y `grand_total_operate_cost_completed`.
* **QA Cost Subtotals y Grand Total:** 10 campos de subtotales (ej. `subtotal_user_update_qa_cost_completed`) y `grand_total_qa_cost_completed`.

#### 5.2.7. Métodos y Propiedades Notorias del Modelo
* `__str__()`: Devuelve una representación en cadena de la solicitud.
* `get_type_prefix()`: Retorna un prefijo de cadena basado en `type_of_process`, utilizado para generar `unique_code`.
* `save()`: Sobrescrito para generar automáticamente el `unique_code` secuencial (formato `TIPO-AÑOQTR-NUMEROSEC`) al crear una nueva instancia y para establecer el estado inicial a `'pending'` si no se ha definido.
* `local_timestamp` (propiedad): Devuelve el `timestamp` de la solicitud convertido a la zona horaria del `requested_by` (o UTC si no se puede determinar).
* `calculated_turn_around_time` (propiedad): Calcula la diferencia entre `completed_at` y `effective_start_time_for_tat` si ambos están definidos y el estado es 'completed'. Devuelve un objeto `timedelta` o `None`.

### 5.3. `AddressValidationFile(models.Model)`
Almacena archivos individuales subidos específicamente para solicitudes de tipo "Address Validation".
* `request`: `ForeignKey` a `UserRecordsRequest` con `related_name='address_validation_files'`.
* `uploaded_file`: `FileField` que almacena el archivo en `address_validation_uploads/`. Utiliza `validate_file_size`.
* `uploaded_at`: `DateTimeField(auto_now_add=True)`.

### 5.4. Modelos de Historial de Acciones
Estos modelos registran eventos clave en el ciclo de vida de una `UserRecordsRequest`.
* **`BlockedMessage(models.Model)`**: Registra cuándo y por qué se bloqueó una solicitud. Campos: `request`, `blocked_by` (`ForeignKey` a `CustomUser`), `blocked_at`, `reason`.
* **`ResolvedMessage(models.Model)`**: Registra cuándo y cómo se resolvió una solicitud bloqueada. Campos: `request`, `resolved_by` (`ForeignKey` a `CustomUser`), `resolved_at`, `message`, `resolved_file` (FileField), `resolved_link` (URLField).
* **`RejectedMessage(models.Model)`**: Registra cuándo y por qué se rechazó una solicitud (usualmente desde QA). Campos: `request`, `rejected_by` (`ForeignKey` a `CustomUser`), `rejected_at`, `reason`, `is_resolved_qa` (Boolean).

### 5.5. `OperationPrice(models.Model)`
Modelo Singleton (se espera una única instancia con `pk=1`) para almacenar los precios unitarios y costos operativos/QA para las diferentes métricas de las solicitudes.
* Incluye campos `DecimalField` para precios al cliente (ej. `user_update_price`), costos de operación (ej. `user_update_operate_cost`), y costos de QA (ej. `user_update_qa_cost`) para diversas operaciones como actualizaciones de usuario, actualizaciones de propiedad, actualizaciones masivas, procesamiento de CSV, etc., incluyendo los ítems específicos para Address Validation, Stripe Disputes y XML Files.

### 5.6. `SalesforceAttachmentLog(models.Model)`
Almacena metadatos de archivos adjuntos provenientes de Salesforce y asociados a una `UserRecordsRequest` creada automáticamente.
* `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='salesforce_attachments'`).
* `file_name`, `file_extension`, `salesforce_file_link`.

### 5.7. `ScheduledTaskToggle(models.Model)`
Permite habilitar o pausar la ejecución de tareas programadas específicas (como la sincronización con Salesforce) a través del panel de administración de Django.
* `task_name`: `CharField(unique=True, primary_key=True)`. Identificador único de la tarea.
* `is_enabled`: `BooleanField(default=True)`. Controla si la tarea se ejecuta.
* `last_modified`: `DateTimeField(auto_now=True)`.

### 5.8. `NotificationToggle(models.Model)`
**Nuevo Modelo.** Permite controlar individualmente desde el panel de administración si se envían notificaciones por correo electrónico para cada uno de los 13 tipos de eventos de notificación definidos.
* `event_key`: `CharField(max_length=100, unique=True, primary_key=True)`. Una clave de cadena única que identifica el evento (ej. `'new_request_created'`, `'request_approved'`).
* `description`: `CharField(max_length=255, blank=True)`. Una descripción legible para el administrador sobre qué es el evento.
* `is_email_enabled`: `BooleanField(default=True)`. Si es `True`, se envían correos para este evento; si es `False`, se omiten.
* `last_modified`: `DateTimeField(auto_now=True)`.

---
## 6. Definición Centralizada de Opciones (`tasks/choices.py`)

Este archivo es crucial para mantener la consistencia de las opciones utilizadas en los modelos y formularios.

### 6.1. Opciones de Modelos y Formularios
Contiene todas las tuplas `choices` (valor almacenado en BD, etiqueta legible para el usuario) para campos como:
* `TYPE_CHOICES`: Define los 7 tipos principales de procesos (User Records, Deactivation/Toggle, Unit Transfer, Generating XML, Address Validation, Stripe Disputes, Property Records).
* `TEAM_CHOICES`: Define los equipos operativos (Revenue, Support, Compliance, Accounting).
* `PRIORITY_CHOICES`: Define los niveles de prioridad (Low, Normal, High).
* `STATUS_CHOICES`: Define los posibles estados de una solicitud (Pending, Scheduled, In Progress, Completed, etc.).
* `REQUEST_TYPE_CHOICES` (para UserGroupForm), `ACCESS_LEVEL_CHOICES`.
* Constantes y choices específicas para cada tipo de proceso: `DEACTIVATION_TOGGLE_CHOICES`, `LEADERSHIP_APPROVAL_CHOICES`, `UNIT_TRANSFER_TYPE_CHOICES`, `UNIT_TRANSFER_LANDLORD_TYPE_CHOICES`, `XML_STATE_CHOICES`, `PROPERTY_RECORDS_TYPE_CHOICES`, `PROPERTY_TYPE_CHOICES`, `COVERAGE_TYPE_CHOICES`, `COVERAGE_MULTIPLIER_CHOICES`, `INTEGRATION_TYPE_CHOICES`.
Todos los textos legibles están en inglés.

### 6.2. Claves de Eventos de Notificación
**Nueva sección.** Se han añadido constantes de cadena para las 13 claves de eventos de notificación. Estas claves son utilizadas por el modelo `NotificationToggle` y las funciones en `tasks/notifications.py` para identificar cada evento de forma única y consistente.
Ejemplos:
* `EVENT_KEY_NEW_REQUEST_CREATED = 'new_request_created'`
* `EVENT_KEY_REQUEST_APPROVED = 'request_approved'`
* ... (y las otras 11 claves)
También se incluye un diccionario `ALL_NOTIFICATION_EVENT_KEYS` que mapea estas claves a descripciones legibles, utilizado en `apps.py` para la creación inicial de los objetos `NotificationToggle`.

---
## 7. Validadores Personalizados (`tasks/validators.py`)

* `validate_file_size(value)`: Validador reutilizable que verifica si un archivo subido excede un límite predefinido (actualmente 10MB). Lanza una `ValidationError` si el archivo es demasiado grande. Este validador se aplica a todos los campos `FileField` relevantes en los modelos y formularios para asegurar que no se suban archivos excesivamente grandes.

---
## 8. Formularios Detallados (`tasks/forms.py`)

Este archivo define todos los formularios Django utilizados en la aplicación `tasks` para la entrada y validación de datos. Todos los `label` y `help_text` están en inglés. Los widgets de formulario están configurados con clases de Bootstrap para una mejor integración visual.

### 8.1. Formularios de Gestión de Usuario
* **`CustomUserChangeForm(UserChangeForm)`**: Para editar la información básica del perfil de usuario (`username`, `email`, `first_name`, `last_name`, `timezone`). No maneja el cambio de contraseña.
* **`CustomPasswordChangeForm(PasswordChangeForm)`**: Formulario especializado para que los usuarios cambien su propia contraseña, incluyendo la validación de la contraseña antigua y la confirmación de la nueva.

### 8.2. Formularios para la Creación de Solicitudes
* **`UserGroupForm(forms.Form)`**: Sub-formulario (utilizado en un `formset_factory`) para capturar detalles de grupos de usuarios dentro de una solicitud de tipo "User Records". Incluye `type_of_request` (Add, Edit, Remove), `user_email_addresses`, `access_level`, y `properties`. La obligatoriedad de `access_level` depende del `type_of_request`.
* **`UserRecordsRequestForm(forms.Form)`**: Formulario principal (no `ModelForm`) para crear solicitudes de tipo "User Records". Incluye `partner_name`, `special_instructions`, `user_file`, `user_link`, `priority`, y los campos de programación `schedule_request` y `scheduled_date`. Su método `clean()` valida la lógica de programación de fechas.
* **`DeactivationToggleRequestForm(forms.ModelForm)`**: Para crear solicitudes de "Deactivation and Toggle". Define campos específicos como `deactivation_toggle_type`, `properties`, `deactivation_toggle_active_policies`, etc. El método `clean()` implementa lógica condicional para la obligatoriedad y validación de campos basados en el `deactivation_toggle_type` seleccionado y maneja la validación de la programación de fechas.
* **`UnitTransferRequestForm(forms.ModelForm)`**: Para solicitudes de "Unit Transfer". Incluye campos como `unit_transfer_type`, `partner_name` (origen), `unit_transfer_new_partner_prospect_name` (destino), `properties`, y campos condicionales para "Partner to Prospect". El método `clean()` valida estos campos condicionales y la obligatoriedad de `properties` si no se proporciona un archivo o enlace, además de la programación.
* **`GeneratingXmlRequestForm(forms.ModelForm)`**: Para solicitudes de "Generating XML files". Campos: `xml_state`, `xml_carrier_rvic`, `xml_carrier_ssic`, `user_file` (obligatorio), y los campos condicionales `xml_rvic_zip_file` y `xml_ssic_zip_file` (requeridos para ciertos estados). El método `clean()` valida la selección de al menos un carrier y la obligatoriedad de los archivos ZIP. `priority` se maneja en la vista.
* **`AddressValidationRequestForm(forms.ModelForm)`**: Para crear solicitudes de "Address Validation". Incluye `partner_name`, campos manuales como `address_validation_policyholders`, `address_validation_opportunity_id`, `user_link`, y `address_validation_user_email_addresses`. El campo para múltiples archivos se maneja en la vista (`request.FILES.getlist('request_files')`). El método `clean()` valida que se proporcione `address_validation_opportunity_id` si no se suben archivos ni se da un enlace, y maneja la programación.
* **`StripeDisputesRequestForm(forms.ModelForm)`**: Para solicitudes de "Stripe Disputes". Campos: `stripe_premium_disputes`, `stripe_ri_disputes`, `user_file` (obligatorio), `special_instructions`. El método `clean()` valida que al menos uno de los conteos de disputas sea mayor que cero. `priority` se maneja en la vista.
* **`PropertyRecordsRequestForm(forms.ModelForm)`**: Para solicitudes de "Property Records". Es un formulario complejo con muchos campos condicionales (`property_records_*`) basados en el `property_records_type` seleccionado. El método `clean()` implementa una lógica detallada para la obligatoriedad de estos campos si no se proporciona un archivo o enlace, y también maneja la validación de la programación de fechas.

### 8.3. Formularios para Acciones de Flujo de Trabajo y Operación
* **Formularios de Acción Simples**:
    * `BlockForm(forms.Form)`: Un campo `reason` (Textarea) para bloquear una solicitud.
    * `ResolveForm(forms.Form)`: Campos `message` (Textarea), `resolved_file` (FileField opcional), `resolved_link` (URLField opcional) para resolver una solicitud bloqueada.
    * `RejectForm(forms.Form)`: Un campo `reason` (Textarea) para rechazar una solicitud.
* **`OperateForm(forms.ModelForm)`**: Formulario genérico basado en `UserRecordsRequest` para capturar detalles de operación cuando una solicitud se envía a QA o se completa. Su `__init__` personaliza dinámicamente los campos visibles y su obligatoriedad (`required=True/False`) según el `type_of_process` de la instancia de la solicitud. Por ejemplo, para "Address Validation", hace obligatorios campos como `av_number_of_units` y `link_to_assets`. Para "Stripe Disputes", hace obligatorios `stripe_premium_disputes` y `stripe_ri_disputes`. Para otros tipos, la mayoría de los campos de conteo son opcionales.
* **`GeneratingXmlOperateForm(forms.ModelForm)`**: Hereda de `OperateForm` pero es específico para operar y completar solicitudes de "Generating XML files". Su `__init__` añade dinámicamente los campos `FileField` necesarios (`operator_rvic_file_slot1`, etc.) basados en el `xml_state` y los carriers seleccionados en la solicitud original. También incluye un campo `qa_needs_file_correction` (Boolean) para el flujo de QA. El método `save()` está sobrescrito para manejar correctamente la asignación de estos archivos dinámicos a los campos correctos del modelo.
* **`OperationPriceForm(forms.ModelForm)`**: Formulario para editar la única instancia del modelo `OperationPrice`, permitiendo a los administradores gestionar los precios y costos unitarios de las operaciones.

### 8.4. Formulario para Proveer Actualización (`ProvideUpdateForm`)
* **`ProvideUpdateForm(forms.Form)`**: **Nuevo formulario**. Contiene un único campo `update_message` (`CharField` con `Textarea`) que es `required=True`. Este formulario se presenta en un modal cuando un usuario hace clic en el botón "Provide Update" en la página de detalle de una solicitud. El mensaje ingresado se pasa a la función de notificación `notify_update_provided` y no se almacena en la base de datos.

---
## 9. Lógica de las Vistas (`tasks/views.py`)

El archivo `tasks/views.py` contiene la lógica de negocio principal para manejar las solicitudes HTTP, interactuar con los modelos y formularios, y renderizar las plantillas.

### 9.1. Funciones Auxiliares y Control de Permisos
Se utilizan varias funciones helper para verificar los roles y permisos de los usuarios:
* `is_admin(user)`: Verifica si el usuario es superusuario o staff.
* `is_leadership(user)`: Verifica si el usuario pertenece al grupo "Leaderships".
* `is_agent(user)`: Verifica si el usuario pertenece al grupo "Agents".
* `user_is_admin_or_leader(user)`: Combinación de las dos primeras.
* `user_in_group(user, group_name)`: Verifica la pertenencia a un grupo específico.
* `can_view_request(user, user_request)`, `can_cancel_request(user, user_request)`: Lógica específica para permisos de acciones.
Estas funciones se usan frecuentemente con el decorador `@user_passes_test` o directamente en las vistas para controlar el acceso a funcionalidades o la visibilidad de elementos.
Decoradores como `@user_belongs_to_revenue_or_support` y otros específicos de equipo (`@user_belongs_to_compliance`, `@user_belongs_to_accounting`) restringen el acceso a las vistas de creación de solicitudes según el equipo del usuario.

### 9.2. Vistas Principales (Home, Profile, Choose Request Type)
* **`home(request)`**: Renderiza la página de inicio `tasks/home.html`.
* **`profile(request)`**: Permite a los usuarios autenticados ver y actualizar su información de perfil (usando `CustomUserChangeForm`) y cambiar su contraseña (usando `CustomPasswordChangeForm`).
* **`choose_request_type(request)`**: Renderiza `tasks/choose_request_type.html`, que presenta al usuario las diferentes categorías de solicitudes que puede crear.

### 9.3. Vistas de Creación de Solicitudes
Existen vistas dedicadas para cada uno de los 7 tipos de proceso (ej. `user_records_request`, `deactivation_toggle_request`, `address_validation_request`, etc.).
* **Procesamiento de Formularios:** Cada vista maneja la lógica `GET` (mostrar formulario vacío) y `POST` (procesar datos enviados). Se utilizan los formularios correspondientes definidos en `tasks.forms`.
* **Asignación de Equipo:** Para tipos de solicitud que pueden ser creados por usuarios de Revenue o Support (User Records, Deactivation/Toggle, Unit Transfer, Address Validation, Property Records), se verifica que el usuario no pertenezca a ambos grupos simultáneamente. El campo `team` de la `UserRecordsRequest` se asigna automáticamente según el grupo del usuario. Para Compliance (Generating XML) y Accounting (Stripe Disputes), el equipo se asigna directamente en la vista.
* **Programación de Solicitudes:** Todas las vistas de creación implementan la lógica para manejar los campos `schedule_request` y `scheduled_date`. Si se marca la programación y se proporciona una fecha válida, el estado inicial de la solicitud se establece en `'scheduled'` y se guarda `scheduled_date`; de lo contrario, el estado inicial es `'pending'` (o `'pending_approval'` para ciertos tipos de Deactivation/Toggle) y se establece `effective_start_time_for_tat`.
* **Lógica Específica por Tipo:**
    * `user_records_request`: Maneja el `formset_factory` para `UserGroupForm`. Valida el formulario principal y el formset. El formset es requerido solo si no se proporciona un archivo (`user_file`) o enlace (`user_link`).
    * `deactivation_toggle_request`: Determina si la solicitud requiere aprobación de liderazgo basado en `deactivation_toggle_type` y si el creador es un líder. El estado inicial puede ser `'pending_approval'`, `'scheduled'` (si se programa y no requiere aprobación o el creador es líder), o `'pending'`.
    * `address_validation_request`: Maneja la subida de múltiples archivos (`request.FILES.getlist('request_files')`) que se guardan como instancias de `AddressValidationFile` relacionadas con la `UserRecordsRequest`, utilizando `transaction.atomic()`.
* **Notificaciones:** Todas las vistas de creación, después de guardar exitosamente una nueva instancia de `UserRecordsRequest`, encolan una tarea asíncrona para llamar a `tasks.notifications.notify_new_request_created` (o `notify_pending_approval_request` si aplica para Deactivation/Toggle), pasando el PK de la solicitud y la información del host/scheme actual.

### 9.4. Vistas de Visualización (Dashboard y Detalle de Solicitud)
* **`portal_operations_dashboard(request)`**: (Nombre de URL `rhino_dashboard`) Muestra una tabla paginada de todas las `UserRecordsRequest`. Incluye filtros por tipo de proceso, estado, equipo asignado, y rango de fechas de creación (usando `timestamp`). La paginación se maneja con `Paginator` de Django. Pasa `is_admin_user` e `is_leadership_user` al contexto para la visualización condicional de la columna de costos.
* **`request_detail(request, pk)`**: Muestra los detalles completos de una `UserRecordsRequest` específica, identificada por su `pk`.
    * Determina dinámicamente qué plantilla de detalle usar (`user_records_detail.html`, `deactivation_toggle_detail.html`, etc.) basado en `user_request.type_of_process`.
    * Obtiene y pasa al contexto el historial de acciones (bloqueos, resoluciones, rechazos).
    * Procesa y formatea datos específicos del tipo de solicitud para su visualización (ej. `user_groups_data` para User Records, `address_validation_files` para Address Validation).
    * Calcula y pasa variables de permiso al contexto (ej. `can_reject_request`, `can_request_update_action`, `can_cancel_request`).
    * Para solicitudes de "Generating XML", instancia y pasa `GeneratingXmlOperateForm` al contexto como `form_for_modal` para ser usado en los modales de "Send to QA" y "Complete".
    * Muestra la sección de "Price Breakdown" si la solicitud está completada y el usuario es admin o líder.

### 9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)
Vista protegida para administradores y líderes.
* Filtra solicitudes completadas por rango de fechas.
* Calcula el gran total de `grand_total_client_price_completed`.
* Agrupa y suma los costos por equipo (`team`) y por tipo de proceso (`type_of_process`).
* Prepara datos para gráficos Chart.js:
    * Dos gráficos de tarta (pie charts) para la distribución de costos por equipo y por tipo de proceso.
    * Gráficos de dispersión con líneas (line charts) para la tendencia de costos (`grand_total_client_price_completed` vs. `completed_at`) para cinco tipos de proceso clave, desglosados por equipo (Revenue/Support). Los puntos de datos en estos gráficos incluyen el `pk` de la solicitud, permitiendo enlazar a la página de detalle de la solicitud.
* Pasa todos estos datos, incluyendo una plantilla de URL para `request_detail`, a la plantilla `tasks/cost_summary.html`.

### 9.6. Vistas de Generación de Reportes CSV
Tres vistas para generar reportes CSV, cada una con su propio formulario de filtros y utilizando funciones helper para la generación del CSV.
* **`generate_revenue_support_report_view(request)`**: Filtros por fecha, estado, tipo de proceso (obligatorio, de una lista de 5 relevantes), y equipo (Revenue, Support, Ambos). Llama a la función `_generate_*_csv` correspondiente al tipo de proceso.
* **`generate_compliance_xml_report_view(request)`**: Filtros por fecha, estado, estado XML, y carriers (RVIC/SSIC). Llama a `_generate_generating_xml_csv()`.
* **`generate_accounting_stripe_report_view(request)`**: Filtros por fecha y estado. Llama a `_generate_stripe_disputes_csv()`.
* **Funciones Helper `_generate_*_csv(request_items, filename)`**: Siete funciones distintas (una para cada tipo de proceso principal: User Records, Property Records, Unit Transfer, Deactivation/Toggle, Address Validation, Generating XML, Stripe Disputes) que toman un queryset, definen encabezados CSV específicos, formatean los datos de cada solicitud (incluyendo todos los campos generales y específicos del tipo, así como fechas formateadas y valores de `choices`), y retornan un `HttpResponse` con el archivo CSV.

### 9.7. Vistas de Acciones del Flujo de Trabajo
Estas vistas manejan las transiciones de estado y la lógica asociada para una `UserRecordsRequest`. Todas las vistas de acción relevantes ahora también disparan notificaciones asíncronas.
* **`operate_request(request, pk)`**: Cambia el estado de 'Pending' o 'Completed' (si se reabre) a 'In Progress'. Asigna el `request.user` como `operator`. Limpia campos de QA y `uncanceled_by`.
* **`block_request(request, pk)`**: Cambia el estado a 'Blocked'. Crea un `BlockedMessage` con la razón. Para solicitudes de 'Address Validation' con `salesforce_standard_opp_id`, intenta actualizar la Opportunity en Salesforce a 'Escalated'.
* **`resolve_request(request, pk)`**: Cambia el estado de 'Blocked' a 'Pending'. Crea un `ResolvedMessage`. Reinicia `effective_start_time_for_tat`. Para 'Address Validation', intenta actualizar la Opportunity en Salesforce a 'In Progress'.
* **`send_to_qa_request(request, pk)`**: Cambia el estado de 'In Progress' a 'QA Pending'. Utiliza `OperateForm` o `GeneratingXmlOperateForm` para guardar detalles de la operación. Establece `qa_pending_at` y resetea `is_rejected_previously` a `False`.
* **`qa_request(request, pk)`**: Cambia el estado de 'QA Pending' a 'QA In Progress'. Asigna el `request.user` como `qa_agent` y establece `qa_in_progress_at`.
* **`complete_request(request, pk)`**: Cambia el estado de 'QA In Progress' a 'Completed'. Utiliza `OperateForm` o `GeneratingXmlOperateForm`. Establece `completed_at`. **Calcula y guarda todos los subtotales y totales de precios/costos** en los campos `*_completed` de la `UserRecordsRequest` basados en `OperationPrice`. Para 'Address Validation', actualiza campos relevantes en la Opportunity de Salesforce.
* **`cancel_request(request, pk)`**: Cambia el estado a 'Cancelled'. Establece `cancelled=True`, `cancelled_by`, `cancelled_at`. Limpia `scheduled_date` si existía.
* **`uncancel_request(request, pk)`**: Cambia el estado de 'Cancelled' a 'Pending'. Limpia campos de cancelación y establece `uncanceled_by`, `uncanceled_at`.
* **`reject_request(request, pk)`**: Cambia el estado (usualmente a 'In Progress'). Crea un `RejectedMessage`. Limpia campos de QA/Completado y establece `is_rejected_previously = True`.
* **`approve_deactivation_toggle(request, pk)`**: Para solicitudes de "Deactivation/Toggle" en 'Pending Approval'. Cambia el estado a 'Pending' (e inicia TAT) o a 'Scheduled' dependiendo de `scheduled_date` y la fecha actual.
* **`set_update_needed_flag(request, pk)`**: Establece `update_needed_flag = True` y registra `update_requested_by` y `update_requested_at`.
* **`clear_update_needed_flag(request, pk)`**: **Modificada significativamente.** Ahora procesa `ProvideUpdateForm` (enviado desde un modal). Si el formulario es válido, obtiene el `update_message`, establece `update_needed_flag = False`, y luego dispara la notificación `notify_update_provided` con el mensaje.

#### 9.7.1. Integración de Notificaciones en Vistas de Acción
Cada una de las vistas mencionadas en 9.7 (y las vistas de creación en 9.3) ahora incluye una llamada a `async_task` después de que la acción principal se completa con éxito (ej. después de guardar el cambio de estado). Esta llamada encola la función de notificación correspondiente de `tasks.notifications.py` (ej. `notify_request_blocked`, `notify_request_completed`) con los parámetros necesarios (PK de la solicitud, PK del usuario actor, y cualquier otro dato relevante como mensajes de formularios). Esto asegura que las notificaciones se envíen de forma asíncrona sin bloquear la respuesta al usuario.

---
## 10. Módulo de Notificaciones (`tasks/notifications.py`)

Este **nuevo archivo** es el centro de toda la lógica de envío de notificaciones por correo electrónico y Telegram.

### 10.1. Funciones Helper de Notificación
* **`get_absolute_url_for_request(request_obj, http_request=None)`**: Construye la URL absoluta para una `UserRecordsRequest` dada, necesaria para los enlaces en las notificaciones. Prioriza `http_request.build_absolute_uri()` si `http_request` está disponible (típicamente cuando se llama desde una vista); de lo contrario, usa `settings.SITE_DOMAIN` (esencial para tareas asíncronas que no tienen un contexto de solicitud HTTP).
* **`send_request_notification_email(subject, template_name_base, context, recipient_list, request_obj=None, http_request_for_url=None)`**: Función genérica para enviar correos. Renderiza las plantillas HTML (`.html`) y de texto plano (`.txt`) correspondientes al `template_name_base` desde el directorio `tasks/templates/tasks/emails/`. Utiliza `django.core.mail.send_mail`. Incluye logging detallado y manejo de excepciones como `TemplateDoesNotExist`.
* **`escape_markdown_v2(text)`**: Función helper para escapar caracteres especiales requeridos por el formato `MarkdownV2` de Telegram, asegurando que el texto se muestre correctamente.
* **`send_telegram_message(bot_token, chat_id, message_text)`**: Envía un mensaje a través de la API de Telegram utilizando la librería `requests`. El `message_text` se envía con `parse_mode='MarkdownV2'`. Incluye logging y manejo de errores, intentando registrar la respuesta de la API de Telegram en caso de error.
* **`is_email_notification_enabled(event_key_param)`**: Consulta el modelo `NotificationToggle` usando la `event_key` proporcionada. Devuelve `True` si `is_email_enabled` es verdadero para ese evento, o `False` si está deshabilitado. Registra la decisión. Si el `NotificationToggle` para una clave no existe, por defecto considera la notificación como habilitada y registra una advertencia.

### 10.2. Funciones Específicas de Notificación por Evento
Se han implementado 13 funciones, una para cada evento de notificación (ej. `notify_new_request_created`, `notify_request_approved`, `notify_request_blocked`, `notify_request_completed`, etc.). Cada una de estas funciones:
1.  Define una `current_event_key` (idealmente importada desde `tasks.choices`) que corresponde a su evento.
2.  Obtiene los objetos de modelo necesarios (la `UserRecordsRequest`, el usuario actor, etc.) a partir de los PKs pasados como argumentos.
3.  Prepara los datos comunes como la `request_url`.
4.  **Para correos electrónicos:**
    * Llama a `is_email_notification_enabled(current_event_key)`.
    * Si está habilitado:
        * Construye el `subject` y el diccionario `context` con los datos específicos del evento y los objetos relevantes (ej. `request_obj`, `approver_user`, `block_reason_text`).
        * Determina la lista de `email_recipient_list` (usando un `set` para evitar duplicados), aplicando la lógica de destinatarios específica para ese evento (ej. notificar al operador, al creador original, al usuario que bloqueó, etc., y siempre al correo temporal `oscarmbv@gmail.com`).
        * Llama a `send_request_notification_email` con el nombre base de la plantilla de correo apropiada (ej. `'request_approved_notification'`).
    * Si está deshabilitado, registra que el envío de correo fue omitido.
5.  **Para Telegram:**
    * Construye el `telegram_message_text` específico para el evento, utilizando `escape_markdown_v2` para los datos dinámicos y las URLs crudas para los hipervínculos. Se ha prestado atención a cómo se insertan los emails en el texto para mejorar la compatibilidad con MarkdownV2.
    * Llama a `send_telegram_message`, usualmente al `TELEGRAM_DEFAULT_CHAT_ID` (esto podría expandirse en el futuro para destinatarios de Telegram más específicos).

### 10.3. Lógica de Control de Envío de Correos (Toggles)
La función `is_email_notification_enabled(event_key)` es el núcleo de este control. Permite que el estado de `NotificationToggle.is_email_enabled` (manejado desde el admin) determine si la parte de envío de correo de cada función de notificación específica se ejecuta o no.

---
## 11. Estructura y Contenido de las Plantillas (`tasks/templates/`)

### 11.1. Plantilla Base (`base.html`)
Define la estructura HTML común para todas las páginas, incluyendo la barra de navegación superior, el bloque de contenido principal, y el pie de página. Utiliza Bootstrap 5 para el estilo.
* **Barra de Navegación:** Incluye enlaces a Home, Dashboard, New Request. Muestra condicionalmente "Manage Prices" (para superuser/staff) y un menú desplegable "CSV Reports" con enlaces a los reportes de Revenue/Support, Compliance y Accounting, y un enlace a "Cost Summary" (estos últimos visibles para admin/leadership). También tiene un menú de usuario para Profile y Logout.

### 11.2. Plantillas de Creación de Solicitudes
Existen plantillas HTML dedicadas para cada uno de los 7 formularios de creación de solicitudes (ej. `user_records_request.html`, `deactivation_toggle_request.html`, `address_validation_request.html`, etc.).
* Renderizan los campos del formulario correspondiente, usualmente en una estructura de dos columnas para organizar la información.
* Incluyen JavaScript para la lógica condicional de campos (ej. mostrar/ocultar campos basados en selecciones previas, como los campos de ZIP para "Generating XML" o los campos de Prospect para "Unit Transfer").
* Todas las plantillas de creación ahora incluyen campos para `priority` y la sección de "Scheduling (Optional)" con `schedule_request` (checkbox) y `scheduled_date` (campo de fecha que se muestra/oculta con JS).

### 11.3. Plantilla del Dashboard (`rhino_operations_dashboard.html`)
Muestra una tabla paginada de solicitudes con filtros.
* **Filtros:** Botones de radio para filtrar por Tipo de Proceso, Estado y Equipo. Campos de fecha para filtrar por rango de creación.
* **Tabla de Solicitudes:** Columnas para Code, Time of Request (con fecha programada si aplica), Type, Team, Priority, Requested By, Partner/State (condicional), Status (con badges de color), Operator, QA By, Turn Around Time.
* **Columna "Total Price"**: Condicionalmente visible para `is_admin_user` o `is_leadership_user`, muestra `grand_total_client_price_completed`.
* JavaScript para aplicar los filtros sin recargar la página completamente (actualiza los parámetros GET y recarga).

### 11.4. Plantillas de Detalle de Solicitud (`*_detail.html`)
Existen plantillas de detalle específicas para cada tipo de proceso (ej. `user_records_detail.html`, `generating_xml_detail.html`, `address_validation_detail.html`, etc.).
* **Estructura Común:**
    * Muestran información general de la solicitud (ID, estado, timestamps, prioridad, equipo, TAT usando `format_timedelta`).
    * Detalles de la sumisión (partner, archivos/enlaces, instrucciones especiales).
    * Detalles específicos del tipo de proceso (ej. grupos de usuarios para User Records, detalles de XML para Generating XML, información de Salesforce para Address Validation).
    * Detalles de la operación si la solicitud ha sido operada (conteos, notas del operador, enlace a spreadsheet).
    * Sección "Price Breakdown" (visible para admin/leadership si la solicitud está completada).
    * Historial de acciones (Blocked, Resolved, Rejected messages).
    * Botones de acción condicionales según el estado de la solicitud y los permisos del usuario (Operate, Block, Send to QA, Start QA, Complete, Resolve, Reject, Approve, Cancel, Uncancel, Request Update, Provide Update).
* **JavaScript para Modales:** Lógica para validar campos en los modales de "Send to QA" y "Complete" (especialmente para campos obligatorios en ciertos tipos de proceso como Address Validation).
* **Filtro `format_timedelta`**: Utilizado para mostrar el `calculated_turn_around_time` de forma legible.

#### 11.4.1. Modal para "Provide Update"
El botón "Update Provided" en las plantillas de detalle (ahora etiquetado como "Provide Update") ha sido modificado para activar un modal (`#provideUpdateModal`). Este modal contiene el `ProvideUpdateForm` con un campo de texto para que el usuario ingrese su mensaje de actualización. Al enviar, el formulario del modal hace un POST a la vista `clear_update_needed_flag` con el mensaje. Esta estructura de modal se replica en las 7 plantillas de detalle de solicitud.

### 11.5. Plantilla de Resumen de Gastos (`client_cost_summary.html`)
Nueva plantilla que muestra el reporte de resumen de costos.
* Incluye un formulario para filtrar por rango de fechas.
* Muestra el gran total de costos y subtotales por equipo y tipo de proceso.
* Renderiza gráficos usando Chart.js: dos gráficos de tarta y cinco gráficos de dispersión/línea para tendencias de costos, con puntos clickeables que enlazan a los detalles de la solicitud.

### 11.6. Plantillas para Formularios de Reportes CSV
Nuevas plantillas para presentar los formularios de filtro antes de generar los reportes CSV:
* `revenue_support_report.html` (antes `revenue_support_report_form.html`)
* `compliance_xml_report.html` (antes `compliance_xml_report_form.html`)
* `accounting_stripe_report.html` (antes `accounting_stripe_report_form.html`)
Estas plantillas contienen los selectores de fecha, estado, tipo de proceso, etc., específicos para cada reporte.

### 11.7. Plantillas de Correo Electrónico (`tasks/templates/tasks/emails/`)
**Nuevo directorio.** Contiene plantillas HTML y de texto plano separadas para cada uno de los 13 eventos de notificación.
Ejemplos:
* `new_request_created.html` y `new_request_created.txt`
* `salesforce_new_request.html` y `salesforce_new_request.txt` (para solicitudes creadas desde Salesforce)
* `request_approved_notification.html` y `request_approved_notification.txt`
* `update_provided_notification.html` y `update_provided_notification.txt` (incluye el mensaje del `ProvideUpdateForm`)
* ... y así para los 13 eventos.
Estas plantillas utilizan el contexto proporcionado por las funciones en `tasks/notifications.py` para mostrar información dinámica como el código de la solicitud, el tipo, el usuario actor, mensajes específicos del evento, y un enlace a los detalles de la solicitud. Usan el tag `{% timezone "America/Caracas" %}` para mostrar las fechas en la zona horaria de Caracas.

---
## 12. Tareas Programadas y en Segundo Plano (`django-q2`)

La aplicación utiliza `django-q2` para manejar tareas que deben ejecutarse en segundo plano o de forma programada.

### 12.1. Procesamiento de Solicitudes Programadas (`tasks/scheduled_jobs.py`)
* **`process_scheduled_requests()`**: Esta función se ejecuta diariamente (ver `apps.py`). Busca `UserRecordsRequest` con `status='scheduled'` y cuya `scheduled_date` sea igual o anterior a la fecha actual. Cambia su estado a `'pending'` y establece `effective_start_time_for_tat`. **Ahora también encola una tarea asíncrona para llamar a `tasks.notifications.notify_scheduled_request_activated`** para notificar sobre la activación de estas solicitudes.

### 12.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)
* **`sync_salesforce_opportunities_task()`**: Tarea principal que se ejecuta múltiples veces al día (ver `apps.py`).
    * Verifica el estado del `ScheduledTaskToggle` `'salesforce_sync_opportunities'` antes de ejecutarse.
    * Se conecta a Salesforce usando las credenciales de `settings.py`.
    * Ejecuta una consulta SOQL para obtener Opportunities que cumplen criterios específicos (ej. Stage '5-Closed Won', `Assets_Uploaded__c = false`, `Invisible_Status__c = 'New'`, etc.).
    * Para cada Opportunity elegible:
        * Crea una `UserRecordsRequest` de tipo `'address_validation'`, mapeando campos relevantes desde la Opportunity (Partner Name, IDs, nombre de Opportunity, número de unidades, etc.) al modelo de solicitud. El `requested_by` se establece a un usuario de sistema.
        * Obtiene los archivos adjuntos de la Opportunity desde Salesforce y crea registros `SalesforceAttachmentLog` asociados a la nueva `UserRecordsRequest`.
        * Actualiza el campo `Invisible_Status__c` de la Opportunity en Salesforce a 'In Progress'.
        * **Ahora también encola una tarea asíncrona para llamar a `tasks.notifications.notify_new_request_created`** para notificar sobre la creación de esta solicitud originada en Salesforce.

### 12.3. Configuración de Programación de Tareas (`tasks/apps.py`)
El método `ready()` de `TasksConfig(AppConfig)` se encarga de configurar las tareas programadas al inicio de la aplicación.
* Se asegura de que `django_q` esté en `INSTALLED_APPS`.
* Utiliza `django_q.models.Schedule.objects.create()` (o `get_or_create`) para definir:
    * La tarea `process_scheduled_requests` para ejecutarse diariamente a la 1 PM UTC (`Schedule.DAILY`).
    * La tarea `sync_salesforce_opportunities_task` para ejecutarse múltiples veces al día usando CRON (`'0 13,16,19 * * *'`, es decir, a las 13:00, 16:00 y 19:00 UTC).
* Usa `logger` en lugar de `print` para los mensajes de estado.

#### 12.3.1. Creación de Instancias `NotificationToggle`
También dentro del método `ready()` de `tasks/apps.py`, se ha añadido lógica para asegurar que existan instancias del modelo `NotificationToggle` para cada uno de los 13 eventos de notificación definidos.
* Se itera sobre un diccionario `NOTIFICATION_EVENTS_SETUP` (que mapea claves de evento como `'new_request_created'` a descripciones legibles).
* Se usa `NotificationToggle.objects.get_or_create()` para crear cada toggle si no existe, estableciendo `is_email_enabled = True` por defecto.
Esto asegura que los controles estén disponibles en el admin de Django tan pronto como la aplicación se configura y las migraciones se aplican.

### 12.4. Hooks de Tareas (Opcional - `tasks/hooks.py`)
Se ha creado un archivo `tasks/hooks.py` con una función `print_task_result(task)`. Esta función se especifica en el parámetro `hook` de las llamadas a `async_task` para las notificaciones y registra el resultado (éxito o fallo) de estas tareas asíncronas en los logs de Django, lo cual es útil para la depuración y el seguimiento del sistema de notificaciones.

---
## 13. Interfaz de Administración de Django (`tasks/admin.py`)
Se han realizado personalizaciones significativas en el admin de Django para facilitar la gestión de los datos de la aplicación `tasks`.
* **`CustomUserAdmin`**: Extiende `UserAdmin` para incluir el campo `timezone` en la visualización y edición de usuarios.
* **`UserRecordsRequestAdmin`**: Ofrece una vista detallada y organizada para `UserRecordsRequest`.
    * `list_display`, `list_filter`, `search_fields`, `date_hierarchy`, `ordering` están configurados para una fácil navegación.
    * `readonly_fields` extensos para proteger datos generados automáticamente o que se manejan a través del flujo de la aplicación (incluyendo los nuevos campos de costos `*_completed`).
    * `fieldsets` organizados en secciones colapsables para agrupar lógicamente la gran cantidad de campos del modelo, incluyendo secciones para cada tipo de proceso específico y para los detalles de operación y costos.
    * Inlines para `AddressValidationFileInline`, `BlockedMessageInline`, `ResolvedMessageInline`, y `RejectedMessageInline` para mostrar el historial relacionado directamente en la página de detalle de la solicitud.
    * Acciones personalizadas para disparar manualmente tareas de `django-q2` como `sync_salesforce_opportunities_task` y `process_scheduled_requests`.
* **`HistoryMessageAdmin` (y subclases `BlockedMessageAdmin`, etc.)**: Clases admin para visualizar el historial de mensajes de bloqueo, resolución y rechazo, con enlaces a la solicitud y al usuario actor.
* **`OperationPriceAdmin`**: Permite editar la única instancia de `OperationPrice` a través de `fieldsets` organizados por "Client Prices", "Operate Costs", y "QA Costs".
* **`SalesforceAttachmentLogAdmin`**: Para visualizar los logs de adjuntos de Salesforce.
* **`ScheduledTaskToggleAdmin`**: Permite a los administradores habilitar o pausar tareas programadas específicas. `is_enabled` es editable en la lista.

### 13.1. `NotificationToggleAdmin`
**Nueva clase Admin.** Se ha registrado el modelo `NotificationToggle` para que los administradores puedan:
* Ver una lista de todos los eventos de notificación definidos (los 13 tipos).
* Ver la descripción de cada evento.
* **Activar o desactivar (`is_email_enabled`) el envío de correos electrónicos para cada evento individualmente.** Este campo es editable directamente en la vista de lista para una gestión rápida.
* Ver cuándo se modificó por última vez cada toggle.

---
## 14. Configuración del Entorno de Desarrollo
* Clonar el repositorio.
* Crear y activar un entorno virtual (ej. `python -m venv venv`, `source venv/bin/activate` o `venv\Scripts\activate` en Windows).
* Instalar dependencias: `pip install -r requirements.txt`.
* Crear un archivo `.env` en la raíz del proyecto (basado en un `.env.example` si existiera) con variables como:
    * `DJANGO_SECRET_KEY`
    * `DJANGO_DEBUG=True`
    * `DATABASE_URL` (ej. `sqlite:///db.sqlite3` para desarrollo local)
    * Credenciales de Salesforce (`SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, `SF_CONSUMER_KEY`, `SF_CONSUMER_SECRET`, `SF_INSTANCE_NAME`).
    * Credenciales del servidor de correo (SendGrid): `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER='apikey'`, `EMAIL_HOST_PASSWORD` (la clave API de SendGrid), `DEFAULT_FROM_EMAIL` (remitente verificado).
    * Token del Bot de Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID` (para pruebas).
    * `SITE_DOMAIN` (ej. `SITE_DOMAIN='http://localhost:8000'`).
* Aplicar migraciones: `python manage.py migrate`.
* Crear un superusuario: `python manage.py createsuperuser`.
* (Opcional) Cargar datos iniciales si es necesario (ej. `OperationPrice`, aunque `get_or_create` lo maneja; `NotificationToggle` se crea vía `apps.py`).
* Ejecutar el servidor de desarrollo: `python manage.py runserver`.
* Ejecutar el cluster de Django-Q2 en una terminal separada: `python manage.py qcluster`.

---
## 15. Despliegue (Heroku)
La aplicación está configurada para ser desplegable en Heroku.
* **`Procfile`**: Necesario para Heroku. Debería contener al menos:
    ```
    web: gunicorn requests_webpage.wsgi --log-file -
    worker: python manage.py qcluster
    release: python manage.py migrate
    ```
* **`runtime.txt`**: Especifica la versión de Python (ej. `python-3.10.12`).
* **`requirements.txt`**: Lista todas las dependencias, incluyendo `gunicorn` y `psycopg2-binary` para PostgreSQL.
* **Variables de Entorno en Heroku**: Todas las variables del archivo `.env` (especialmente `SECRET_KEY`, `DATABASE_URL` provisto por Heroku, credenciales de Salesforce, SendGrid, Telegram, `SITE_DOMAIN` apuntando a la URL de Heroku, `DJANGO_DEBUG=False`) deben configurarse en el panel de Heroku (Settings > Config Vars).
* **Buildpacks**: Se necesitará el buildpack de Python.
* **Add-ons**: Heroku Postgres para la base de datos.
* **Archivos Estáticos**: WhiteNoise está configurado para servir archivos estáticos. `collectstatic` se ejecuta durante la fase de `release` (o puede ser parte del build si se usa `collectstatic_build`).

---
## 16. Consideraciones Adicionales y Próximos Pasos

* **Pruebas Exhaustivas del Sistema de Notificaciones:**
    * Verificar que los 13 tipos de notificaciones (email y Telegram) se disparen correctamente para cada evento.
    * Probar la funcionalidad de los `NotificationToggle` desde el admin para activar/desactivar los correos de cada evento y confirmar que la lógica se respeta.
    * Asegurar que los destinatarios de cada notificación sean los correctos según la lógica implementada (incluyendo las condiciones especiales).
    * Validar el contenido y formato de todos los correos y mensajes de Telegram, incluyendo los enlaces y la visualización de la hora en la zona de Caracas.
* **Gestión Avanzada de Destinatarios de Notificación:**
    * Implementar la capacidad para que los usuarios (o administradores) definan sus preferencias de notificación (qué eventos recibir, por qué canal).
    * Añadir un campo `telegram_chat_id` al modelo `CustomUser` y lógica para que los usuarios lo puedan registrar/actualizar.
    * Permitir la configuración de listas de correo o `chat_id` de grupos de Telegram para equipos específicos (ej. notificar a todo el "QA Team" cuando una solicitud se envía a QA).
* **Toggle para Notificaciones de Telegram:** Considerar añadir `is_telegram_enabled` a `NotificationToggle` y una función `is_telegram_notification_enabled()` para un control similar sobre los mensajes de Telegram.
* **Refinar Contenido y Plantillas:** Mejorar el diseño HTML de los correos y el contenido de todos los mensajes para máxima claridad y utilidad.
* **Manejo de Errores en Formularios Modales:** Para el `ProvideUpdateForm` (y otros futuros modales), mejorar la retroalimentación al usuario si el formulario no es válido, idealmente mostrando los errores directamente en el modal sin recargar toda la página de detalle (podría requerir JavaScript adicional).
* **Optimización y Escalabilidad:**
    * Continuar monitoreando las consultas a la base de datos, especialmente en las funciones de notificación y reportes.
    * Revisar el rendimiento de `django-q2` a medida que el uso de la aplicación y el volumen de tareas asíncronas crecen.
* **Internacionalización (i18n) Completa:** Si la aplicación se usará en múltiples idiomas, continuar/completar el proceso de marcar todas las cadenas de texto visibles por el usuario con `{% trans %}` en plantillas y `gettext_lazy` en Python, y gestionar los archivos de traducción `.po`.
* **Autenticación de Dominio para SendGrid:** Una vez que se disponga de un dominio propio para producción, configurar la "Autenticación de Dominio" (SPF, DKIM) en SendGrid para mejorar significativamente la entregabilidad de los correos y la reputación del remitente.
* **Documentación para Usuarios Finales:** Desarrollar guías detalladas para los diferentes roles de usuario sobre cómo utilizar todas las funcionalidades de la plataforma, incluyendo la gestión de solicitudes y el nuevo sistema de notificaciones.
* **Seguridad:** Realizar revisiones de seguridad periódicas, especialmente en cuanto al manejo de credenciales, permisos, y la interacción con APIs externas como Salesforce y Telegram.

---