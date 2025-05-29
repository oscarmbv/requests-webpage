# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** Analizado el 29 de mayo de 2025
**Fecha de Actualización del README:** 29 de mayo de 2025
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
6.  [Definición Centralizada de Opciones (`tasks/choices.py`)](#6-definición-centralizada-de-opciones-taskschoicespy)
7.  [Validadores Personalizados (`tasks/validators.py`)](#7-validadores-personalizados-tasksvalidatorspy)
8.  [Formularios Detallados (`tasks/forms.py`)](#8-formularios-detallados-tasksformspy)
    * [8.1. Formularios de Gestión de Usuario](#81-formularios-de-gestión-de-usuario)
        * [8.1.1. `CustomUserChangeForm`](#811-customuserchangeform)
        * [8.1.2. `CustomPasswordChangeForm`](#812-custompasswordchangeform)
    * [8.2. Formularios para la Creación de Solicitudes](#82-formularios-para-la-creación-de-solicitudes)
        * [8.2.1. `UserGroupForm(forms.Form)`](#821-usergroupformformsform)
        * [8.2.2. `UserRecordsRequestForm(forms.Form)`](#822-userrecordsrequestformformsform)
        * [8.2.3. `DeactivationToggleRequestForm(forms.ModelForm)`](#823-deactivationtogglerequestformformsmodelform)
        * [8.2.4. `UnitTransferRequestForm(forms.ModelForm)`](#824-unittransferrequestformformsmodelform)
        * [8.2.5. `GeneratingXmlRequestForm(forms.ModelForm)`](#825-generatingxmlrequestformformsmodelform)
        * [8.2.6. `AddressValidationRequestForm(forms.ModelForm)`](#826-addressvalidationrequestformformsmodelform)
        * [8.2.7. `StripeDisputesRequestForm(forms.ModelForm)`](#827-stripedisputesrequestformformsmodelform)
        * [8.2.8. `PropertyRecordsRequestForm(forms.ModelForm)`](#828-propertyrecordsrequestformformsmodelform)
    * [8.3. Formularios para Acciones de Flujo de Trabajo y Operación](#83-formularios-para-acciones-de-flujo-de-trabajo-y-operación)
        * [8.3.1. Formularios de Acción Simples (`BlockForm`, `ResolveForm`, `RejectForm`)](#831-formularios-de-acción-simples-blockform-resolveform-rejectform)
        * [8.3.2. `OperateForm(forms.ModelForm)`](#832-operateformformsmodelform)
        * [8.3.3. `GeneratingXmlOperateForm(forms.ModelForm)`](#833-generatingxmloperateformformsmodelform)
        * [8.3.4. `OperationPriceForm(forms.ModelForm)`](#834-operationpriceformformsmodelform)
9.  [Lógica de las Vistas (`tasks/views.py`)](#9-lógica-de-las-vistas-tasksviewspy)
    * [9.1. Funciones Auxiliares y Control de Permisos](#91-funciones-auxiliares-y-control-de-permisos)
    * [9.2. Vistas Principales (Home, Profile, Choose Request Type)](#92-vistas-principales-home-profile-choose-request-type)
    * [9.3. Vistas de Creación de Solicitudes (Detalle por Tipo)](#93-vistas-de-creación-de-solicitudes-detalle-por-tipo)
    * [9.4. Vistas de Visualización (Dashboard y Detalle de Solicitud)](#94-vistas-de-visualización-dashboard-y-detalle-de-solicitud)
    * [9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)](#95-vista-de-resumen-de-gastos-del-cliente-client_cost_summary_view)
    * [9.6. Vistas de Generación de Reportes CSV](#96-vistas-de-generación-de-reportes-csv)
    * [9.7. Vistas de Acciones del Flujo de Trabajo (Detalle por Acción)](#97-vistas-de-acciones-del-flujo-de-trabajo-detalle-por-acción)
10. [Estructura y Contenido de las Plantillas (`tasks/templates/`)](#10-estructura-y-contenido-de-las-plantillas-taskstemplates)
    * [10.1. Plantilla Base (`base.html`)](#101-plantilla-base-basehtml)
    * [10.2. Plantillas de Creación de Solicitudes](#102-plantillas-de-creación-de-solicitudes)
    * [10.3. Plantilla del Dashboard (`rhino_operations_dashboard.html`)](#103-plantilla-del-dashboard-rhino_operations_dashboardhtml)
    * [10.4. Plantillas de Detalle de Solicitud](#104-plantillas-de-detalle-de-solicitud)
    * [10.5. Plantilla de Resumen de Gastos (`client_cost_summary.html`)](#105-plantilla-de-resumen-de-gastos-client_cost_summaryhtml)
    * [10.6. Plantillas para Formularios de Reportes CSV](#106-plantillas-para-formularios-de-reportes-csv)
11. [Tareas Programadas y en Segundo Plano (`django-q2`)](#11-tareas-programadas-y-en-segundo-plano-django-q2)
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
        * `apps.py`: Archivo de configuración para la aplicación `tasks`. Aquí se inicializan las tareas programadas de `django-q2`.
        * `choices.py`: Centraliza las constantes para las opciones (`choices`) de los campos de los modelos.
        * `context_processors.py`: Contiene funciones que añaden variables al contexto de las plantillas de forma global.
        * `forms.py`: Define los formularios Django que se utilizan para la entrada y validación de datos del usuario.
        * `models.py`: Define los modelos ORM de Django, que representan la estructura de las tablas de la base de datos.
        * `salesforce_sync.py`: Contiene la lógica específica para la tarea de sincronización con Salesforce.
        * `scheduled_jobs.py`: Define las funciones que se ejecutan como tareas programadas (ej. activar solicitudes).
        * `tests.py`: Contiene pruebas unitarias y de integración para la aplicación `tasks`.
        * `urls.py`: Define los patrones de URL específicos para la aplicación `tasks`.
        * `validators.py`: Contiene validadores personalizados para campos de modelos o formularios.
        * `migrations/`: Directorio que almacena los archivos de migración de la base de datos.
        * `static/tasks/`: Directorio para archivos estáticos (CSS, JavaScript, imágenes) específicos de la aplicación `tasks`.
        * `templates/tasks/`: Directorio que contiene las plantillas HTML para la interfaz de usuario de la aplicación `tasks`.
            * `registration/`: Contiene plantillas personalizadas para el flujo de autenticación (ej. `login.html`, `logged_out.html`).
        * `templatetags/`: Contiene tags y filtros de plantillas personalizados, como `duration_filters.py`.
    * `manage.py`: Utilidad de línea de comandos de Django para interactuar con el proyecto.
    * `.env`: (No versionado) Archivo para almacenar variables de entorno sensibles.
    * `requirements.txt`: Lista todas las dependencias de Python del proyecto.
    * `README.md`: Este archivo.
    * (El archivo `yender.yaml` fue eliminado, ya que el despliegue se planifica para Heroku).

---
## 3. Configuración Central del Proyecto (`requests_webpage/settings.py`)

Este archivo define la configuración global del proyecto Django.

### 3.1. Variables Fundamentales y de Entorno
* **`BASE_DIR`**: Determina la ruta base del proyecto.
* **`environ.Env`**: Se utiliza `django-environ` para gestionar las variables de entorno, permitiendo cargar configuraciones desde un archivo `.env` en desarrollo y desde el entorno del sistema en producción.
* **`SECRET_KEY`**: Clave criptográfica esencial para la seguridad de Django, cargada desde el entorno.
* **`DEBUG`**: Booleano que activa (True) o desactiva (False) el modo de depuración, cargado desde el entorno.
* **`ALLOWED_HOSTS`**: Lista de nombres de host/dominio permitidos para servir la aplicación. Se configura para desarrollo (`127.0.0.1`, `localhost`) y se adapta para producción (ej. `'.onrender.com'` previamente, ahora incluirá `'.herokuapp.com'`).
* **`CSRF_TRUSTED_ORIGINS`**: Lista de orígenes confiables para solicitudes seguras (HTTPS) al modificar datos, importante para producción.

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)
Es una lista de todas las aplicaciones Django que componen el proyecto. Django usa esta lista para cargar modelos, plantillas, comandos de administración, etc.
* Aplicaciones estándar de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`.
* Aplicaciones de terceros:
    * `'whitenoise.runserver_nostatic'`: Se incluye antes de `django.contrib.staticfiles` para que WhiteNoise pueda servir archivos estáticos durante el desarrollo si `DEBUG=True` de una manera similar a como lo hace en producción, sin necesidad de ejecutar `collectstatic` en cada cambio.
    * `'django_q'`: La aplicación `django-q2` para la gestión de tareas en segundo plano y programadas.
* Aplicación principal del proyecto: `'tasks'`.

### 3.3. Middleware
Define una serie de capas que procesan secuencialmente las solicitudes HTTP entrantes y las respuestas salientes. El orden es importante.
* `django.middleware.security.SecurityMiddleware`: Proporciona varias mejoras de seguridad.
* `whitenoise.middleware.WhiteNoiseMiddleware`: Para servir archivos estáticos de manera eficiente directamente desde la aplicación Django en producción, especialmente útil en plataformas como Heroku. Se inserta después de `SecurityMiddleware`.
* `django.contrib.sessions.middleware.SessionMiddleware`: Habilita el soporte de sesiones.
* `django.middleware.common.CommonMiddleware`: Añade funcionalidades comunes (ej. `APPEND_SLASH`).
* `django.middleware.csrf.CsrfViewMiddleware`: Protección contra ataques Cross-Site Request Forgery.
* `django.contrib.auth.middleware.AuthenticationMiddleware`: Asocia usuarios con solicitudes usando sesiones.
* `django.contrib.messages.middleware.MessageMiddleware`: Habilita el sistema de mensajes flash.
* `django.middleware.clickjacking.XFrameOptionsMiddleware`: Protección contra clickjacking.
* `django.middleware.locale.LocaleMiddleware`: Habilita la internacionalización y la selección de idioma basada en la solicitud.

### 3.4. Autenticación y Modelo de Usuario
* `AUTH_USER_MODEL = 'tasks.CustomUser'`: Le indica a Django que use el modelo `CustomUser` (definido en `tasks.models`) como el modelo de usuario para todo el proyecto, en lugar del modelo `User` estándar.
* `LOGOUT_REDIRECT_URL = '/accounts/login/'`: La URL a la que se redirige al usuario después de que cierra sesión.
* `LOGIN_REDIRECT_URL = '/rhino/dashboard/'`: **Actualizado** al nuevo prefijo `/rhino/`. Es la URL a la que se redirige al usuario después de un inicio de sesión exitoso si no se especifica un parámetro `next`.

### 3.5. Configuración de Base de Datos
* `DATABASES`: Se configura usando `dj_database_url.config()`. Esto permite que la configuración de la base de datos se lea desde la variable de entorno `DATABASE_URL` (ideal para producción en Heroku, que provee esta variable para su add-on de PostgreSQL).
* Como fallback para desarrollo local (si `DATABASE_URL` no está definida), se usa una base de datos SQLite (`sqlite:///db.sqlite3`) ubicada en el directorio raíz del proyecto.
* `conn_max_age=600`: Configura la vida útil máxima de las conexiones a la base de datos (en segundos) para mejorar el rendimiento.
* Para PostgreSQL en Heroku, se añade `{'sslmode': 'require'}` a las opciones de conexión si el motor es PostgreSQL, para asegurar conexiones SSL.

### 3.6. Gestión de Archivos Estáticos y Multimedia
* **Archivos Estáticos (CSS, JavaScript, Imágenes de la aplicación):**
    * `STATIC_URL = 'static/'`: URL base desde la cual se servirán los archivos estáticos en las plantillas (ej. `/static/css/style.css`).
    * `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`: Directorio absoluto donde el comando `python manage.py collectstatic` reunirá todos los archivos estáticos de todas las aplicaciones instaladas para el despliegue en producción.
    * `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`: Configura WhiteNoise para servir archivos estáticos de manera eficiente en producción, incluyendo compresión Gzip/Brotli y versionado de archivos (manifest).
* **Archivos Multimedia (Archivos subidos por el usuario):**
    * `MEDIA_URL = '/media/'`: URL base para los archivos subidos por los usuarios.
    * `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')`: Directorio en el sistema de archivos donde se almacenarán los archivos subidos.

### 3.7. Internacionalización (i18n) y Localización (l10n)
* `LANGUAGE_CODE = 'en-us'`: Establece el inglés de EE. UU. como el idioma por defecto de la aplicación.
* `TIME_ZONE = 'UTC'`: Define la zona horaria interna con la que Django almacena y maneja todas las fechas y horas. Es una buena práctica usar UTC internamente.
* `USE_I18N = True`: Habilita el sistema de traducción de Django.
* `USE_TZ = True`: Habilita el soporte de zonas horarias para los campos `DateTimeField`. Django almacenará las fechas y horas en UTC en la base de datos y las convertirá a la zona horaria del usuario final o la activa al mostrarlas.

### 3.8. Tareas en Segundo Plano (Django-Q2)
* `Q_CLUSTER`: Un diccionario que configura el comportamiento del cluster de `django-q2`.
    * `name`: Nombre para identificar el cluster (ej. `RequestWebpageScheduler_Heroku`).
    * `workers`: Número de procesos worker para ejecutar tareas (configurable vía `DJANGO_Q_WORKERS`).
    * `timeout`: Tiempo máximo (en segundos) que una tarea puede ejecutarse.
    * `retry`: Tiempo (en segundos) después del cual una tarea fallida se reintentará.
    * `queue_limit`: Número máximo de tareas que los workers intentarán obtener.
    * `bulk`: Número máximo de tareas que un worker procesará antes de reciclarse.
    * `orm`: Conexión de base de datos de Django a usar (ej. `'default'`).
    * `catch_up: False`: Evita que se ejecuten tareas programadas acumuladas mientras el cluster estaba inactivo.
    * `log_level`: Nivel de logging para los workers (configurable vía `DJANGO_Q_LOG_LEVEL`).

### 3.9. Integración con Salesforce
* Credenciales (`SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, `SF_CONSUMER_KEY`, `SF_CONSUMER_SECRET`, `SF_DOMAIN`, `SF_VERSION`, `SF_INSTANCE_NAME`) se cargan de forma segura desde el entorno usando `django-environ`.
* `SALESFORCE_LIGHTNING_BASE_URL`: Se construye dinámicamente usando `SF_INSTANCE_NAME` para generar enlaces a registros en la interfaz Lightning de Salesforce.

### 3.10. Configuración de Logging
* Se define un diccionario `LOGGING` para la configuración de logs.
* **Formateadores**: `verbose` (detallado), `simple`, y `qcluster` (para logs de Django-Q).
* **Manejadores**: `console` (para salida estándar) y `file_tasks` (para escribir logs de la aplicación `tasks` a `logs/tasks_app.log`). El directorio `LOG_DIR` (`logs/`) se crea si no existe.
* **Loggers**: Configuraciones específicas para `django`, `django.request`, `tasks` (con nivel configurable por `DJANGO_LOG_LEVEL_TASKS`), y `django_q`.

### 3.11. Procesadores de Contexto de Plantillas
* Se ha añadido `'tasks.context_processors.user_role_permissions'` a la lista `TEMPLATES[0]['OPTIONS']['context_processors']`. Este procesador define las variables `is_admin_user` e `is_leadership_user` y las hace disponibles automáticamente en el contexto de todas las plantillas renderizadas, simplificando la lógica de permisos en `base.html` para mostrar/ocultar elementos de navegación.

---
## 4. Enrutamiento de URLs (`urls.py`)

### 4.1. Enrutador Principal del Proyecto (`requests_webpage/urls.py`)

Este archivo es el punto de entrada para el sistema de URLs de Django.
* `path('admin/', admin.site.urls)`: Activa el sitio de administración de Django.
* `path('accounts/', include('django.contrib.auth.urls'))`: Incluye las URLs predefinidas de Django para la autenticación (login, logout, reseteo de contraseña, etc.).
* `path('rhino/', include('tasks.urls', namespace='tasks'))`: **Actualizado**. Este es el cambio principal. Todas las URLs definidas en el archivo `tasks/urls.py` (de la aplicación `tasks`) ahora estarán prefijadas con `/rhino/` en lugar de `/portal/`. El `namespace='tasks'` permite usar nombres de URL cualificados en las plantillas (ej. `{% url 'tasks:rhino_dashboard' %}`).
* `path('', tasks_views.home, name='home')`: Define la vista para la página de inicio del sitio (la URL raíz `/`).

### 4.2. Enrutador de la Aplicación `tasks` (`tasks/urls.py`)

Este archivo contiene los patrones de URL específicos para la aplicación `tasks`. Todas estas rutas son relativas al prefijo `/rhino/`.
* `app_name = 'tasks'`: Define el namespace de la aplicación.
* **Autenticación:** Rutas para `login` y `logout` utilizando `auth_views` de Django, con la posibilidad de especificar plantillas personalizadas (ej. `template_name='registration/login.html'`).
* **Vistas Principales y de Usuario:**
    * `path('dashboard/', views.portal_operations_dashboard, name='portal_dashboard')`: El dashboard principal de operaciones.
    * `path('profile/', views.profile, name='profile')`: Página de perfil del usuario.
    * `path('manage_prices/', views.manage_prices, name='manage_prices')`: Página para la administración de precios (restringida).
    * `path('client_cost_summary/', views.client_cost_summary_view, name='client_cost_summary')`: **Nueva ruta** para el reporte de resumen de costos.
* **Vistas de Generación de Reportes CSV:**
    * `path('reports/revenue_support/', views.generate_revenue_support_report_view, name='revenue_support_report')`
    * `path('reports/compliance_xml/', views.generate_compliance_xml_report_view, name='compliance_xml_report')`
    * `path('reports/accounting_stripe/', views.generate_accounting_stripe_report_view, name='accounting_stripe_report')`
* **Vistas de Creación de Solicitudes:**
    * `path('create/', views.choose_request_type, name='choose_request_type')`: Página para seleccionar el tipo de nueva solicitud.
    * Rutas específicas para cada formulario de creación: `create/user_records/`, `create/deactivation_toggle/`, `create/unit_transfer/`, `create/generating_xml/`, `create/address_validation/`, `create/stripe_disputes/`, `create/property_records/`.
* **Vistas de Detalle y Acciones sobre Solicitudes:** Utilizan un parámetro `<int:pk>` para identificar la solicitud específica.
    * `path('request/<int:pk>/', views.request_detail, name='request_detail')`: Muestra los detalles de una solicitud.
    * Sub-rutas para cada acción del flujo de trabajo: `operate/`, `block/`, `send_to_qa/`, `qa/`, `complete/`, `cancel/`, `resolve/`, `reject/`, `approve_deactivation_toggle/`, `set_update_flag/`, `clear_update_flag/`, `uncancel/`.

---
## 5. Modelo de Datos (`tasks/models.py`)

Describe la estructura de la base de datos.

### 5.1. `CustomUser(AbstractUser)`
Extiende el modelo `User` de Django.
* `email`: `EmailField(unique=True)`, usado como `USERNAME_FIELD` para la autenticación. `verbose_name='Email address'`.
* `timezone`: `CharField(max_length=100, default='UTC', choices=...)`. Almacena la zona horaria preferida del usuario, con `choices` generadas a partir de `pytz.common_timezones`.
* `REQUIRED_FIELDS = ['username']`: `username` sigue siendo requerido internamente por Django.

### 5.2. `UserRecordsRequest(models.Model)`
El modelo central para todas las solicitudes operativas.
#### 5.2.1. Atributos Generales de Identificación y Estado
* `type_of_process`: `CharField(max_length=50, choices=TYPE_CHOICES, default='user_records', db_index=True)`. Define la naturaleza de la solicitud.
* `unique_code`: `CharField(max_length=20, unique=True, editable=False)`. Código único generado.
* `timestamp`: `DateTimeField(default=now, db_index=True)`. Fecha/hora de creación.
* `requested_by`: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_requests')`.
* `team`: `CharField(max_length=20, choices=TEAM_CHOICES, null=True, blank=True, db_index=True, verbose_name="Assigned Team")`.
* `priority`: `CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, db_index=True, verbose_name="Priority")`.
* `partner_name`: `CharField(max_length=255, blank=True, null=True, db_index=True)`.
* `properties`: `TextField(blank=True, null=True, verbose_name="Properties Affected")`.
* `user_groups_data`: `JSONField(null=True, blank=True)` (para "User Records").
* `special_instructions`: `TextField(blank=True)`.
* `status`: `CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)`.
* `update_needed_flag`: `BooleanField(default=False, verbose_name="Update Needed Flag", help_text="Indicates if the requester/team needs a progress update.")`.
* `update_requested_by`: `ForeignKey(settings.AUTH_USER_MODEL, ..., verbose_name="Update Requested By")`.
* `update_requested_at`: `DateTimeField(null=True, blank=True, verbose_name="Update Requested At")`.
* `user_file`: `FileField(upload_to='user_uploads/', ..., validators=[validate_file_size], verbose_name='Upload File')`.
* `user_link`: `URLField(blank=True, null=True)`.

#### 5.2.2. Atributos de Flujo de Trabajo, Asignación y Programación
* `operator`, `qa_agent`: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, ...)`.
* Timestamps: `operated_at` (db\_index=True), `qa_pending_at`, `qa_in_progress_at`, `completed_at` (db\_index=True), `cancelled_at`, `uncanceled_at`.
* Detalles de cancelación: `cancelled` (Boolean), `cancel_reason` (Text), `cancelled_by` (User), `uncanceled_by` (User).
* `scheduled_date`: `DateField(null=True, blank=True, verbose_name="Scheduled Date", help_text="...")`.
* `effective_start_time_for_tat`: `DateTimeField(null=True, blank=True, verbose_name="Effective Start Time for TAT", help_text="...")`.
* `is_rejected_previously`: `BooleanField(default=False, verbose_name="Previously Rejected by QA", help_text="...")`.

#### 5.2.3. Atributos para Detalles de Operación y QA
Campos `PositiveIntegerField(null=True, blank=True)`: `num_updated_users`, `num_updated_properties`, `bulk_updates`, `manual_updated_properties`, `manual_updated_units` (verbose\_name="Manual Updated Units"), `update_by_csv_rows`, `processing_reports_rows`.
* `operator_spreadsheet_link`: `URLField(max_length=1024, ..., verbose_name="Operator Spreadsheet Link")`.
* `operating_notes`: `TextField(blank=True, null=True)`.

#### 5.2.4. Atributos Específicos por Tipo de Proceso (`type_of_process`)
Conjunto de campos opcionales (`null=True, blank=True`) para cada `type_of_process`.
* **Deactivation/Toggle**: `deactivation_toggle_type` (`DEACTIVATION_TOGGLE_CHOICES`), `_active_policies` (Bool), `_properties_with_policies` (Text), `_context` (Text), `_leadership_approval` (`LEADERSHIP_APPROVAL_CHOICES`), `_marked_as_churned` (Bool).
* **Unit Transfer**: `unit_transfer_type` (`UNIT_TRANSFER_TYPE_CHOICES`), `_new_partner_prospect_name` (Char), `_receiving_partner_psm` (Char), `_new_policyholders` (Text), `_user_email_addresses` (Text), `_prospect_portfolio_size` (PositiveInt), `_prospect_landlord_type` (`UNIT_TRANSFER_LANDLORD_TYPE_CHOICES`), `_proof_of_sale` (URL).
* **Generating XML**: `xml_state` (`XML_STATE_CHOICES`), `xml_carrier_rvic` (Bool), `xml_carrier_ssic` (Bool), `xml_rvic_zip_file` (File), `xml_ssic_zip_file` (File). Campos `FileField` de salida: `operator_rvic_file_slot1`, `operator_rvic_file_slot2`, `operator_ssic_file_slot1`, `operator_ssic_file_slot2`, con `help_text` descriptivo.
* **Address Validation**: `address_validation_policyholders` (Text), `_opportunity_id` (Char), `_user_email_addresses` (Text).
* **Stripe Disputes**: `stripe_premium_disputes` (PositiveInt, verbose\_name="Rhino Super Premium Disputes"), `stripe_ri_disputes` (PositiveInt, verbose\_name="Rhino Super RI Disputes").
* **Property Records**: `property_records_type` (`PROPERTY_RECORDS_TYPE_CHOICES`), y numerosos campos `property_records_*` para nuevos nombres, PMC, dirección corregida, tipo de propiedad (`PROPERTY_TYPE_CHOICES`), unidades, tipo/multiplicador/monto de cobertura (`COVERAGE_TYPE_CHOICES`, `COVERAGE_MULTIPLIER_CHOICES`, `DecimalField` con validadores Min/Max), tipo de integración (`INTEGRATION_TYPE_CHOICES`), códigos de integración, y detalles bancarios.

#### 5.2.5. Atributos para la Integración con Salesforce
Específicos para `type_of_process='address_validation'`.
* **Información de la Opportunity:** `salesforce_standard_opp_id` (Char 18, verbose\_name, help\_text), `salesforce_opportunity_name`, `salesforce_number_of_units`, `salesforce_link`, `salesforce_account_manager`, `salesforce_closed_won_date`, `salesforce_leasing_integration_software`, `salesforce_information_needed_for_assets`.
* **Campos de Salida/Operación para Salesforce:** `assets_uploaded` (Bool), `av_number_of_units` (PositiveInt), `av_number_of_invalid_units` (PositiveInt, default 0), `link_to_assets` (URL), `success_output_link` (URL), `failed_output_link` (URL), `rhino_accounts_created` (Bool).

#### 5.2.6. Atributos para Costos Calculados en Finalización
Tres grupos de campos `DecimalField` (10 subtotales y 1 total por grupo), con `verbose_name` en inglés, `null=True, blank=True, default=Decimal('0.0X')`.
* **Client Price:** Ej. `subtotal_user_update_client_price_completed`, `grand_total_client_price_completed`.
* **Operate Cost:** Ej. `subtotal_user_update_operate_cost_completed`, `grand_total_operate_cost_completed`.
* **QA Cost:** Ej. `subtotal_user_update_qa_cost_completed`, `grand_total_qa_cost_completed`.

#### 5.2.7. Métodos y Propiedades Notorias del Modelo
* `__str__()`: Devuelve una cadena representando la solicitud.
* `get_type_prefix()`: Retorna un prefijo para `unique_code`.
* `save()`: Lógica para generar `unique_code` (formato `TIPO-AÑOQTRNUMERO`) y establecer `status` inicial `'pending'`.
* `local_timestamp` (propiedad): Retorna `self.timestamp` convertido a la zona horaria del `requested_by`.
* `calculated_turn_around_time` (propiedad): Calcula `completed_at - effective_start_time_for_tat`.

### 5.3. `AddressValidationFile(models.Model)`
* `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='address_validation_files'`).
* `uploaded_file`: `FileField(upload_to='address_validation_uploads/', validators=[validate_file_size])`.
* `uploaded_at`: `DateTimeField(auto_now_add=True)`.

### 5.4. Modelos de Historial de Acciones
* **`BlockedMessage`**: `request`, `blocked_by`, `blocked_at`, `reason`.
* **`ResolvedMessage`**: `request`, `resolved_by`, `resolved_at`, `message`, `resolved_file`, `resolved_link`.
* **`RejectedMessage`**: `request`, `rejected_by`, `rejected_at`, `reason`, `is_resolved_qa`.

### 5.5. `OperationPrice(models.Model)`
Modelo Singleton (`pk=1`).
* Campos `DecimalField` para precios al cliente, costos de operación y costos de QA para todas las métricas: `user_update_price`, `property_update_price`, `bulk_update_price`, `manual_property_update_price` (renombrado), `csv_update_price`, `processing_report_price`, y los **nuevos**: `manual_unit_update_price`, `address_validation_unit_price`, `stripe_dispute_price`, `xml_file_price`, junto con sus respectivos `_operate_cost` y `_qa_cost`. Todos con `verbose_name` en inglés.

### 5.6. `SalesforceAttachmentLog(models.Model)`
* `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='salesforce_attachments'`).
* `file_name`, `file_extension`, `salesforce_file_link`.

### 5.7. `ScheduledTaskToggle(models.Model)`
* `task_name`: `CharField(unique=True, primary_key=True, help_text="Unique identifier...")`.
* `is_enabled`: `BooleanField(default=True, help_text="Check to enable...")`.
* `last_modified`: `DateTimeField(auto_now=True)`.

---
## 6. Opciones Predefinidas (`tasks/choices.py`)

Este archivo define como constantes Python todas las tuplas `choices` (valor almacenado, etiqueta legible) utilizadas en los campos `CharField` y `ChoiceField` de los modelos y formularios. Esto incluye:
* `TYPE_CHOICES`: Para los 7 tipos de proceso.
* `TEAM_CHOICES`: Revenue, Support, Compliance, Accounting.
* `PRIORITY_CHOICES`: Low, Normal, High.
* `STATUS_CHOICES`: Pending, Scheduled, In Progress, Completed, Cancelled, Blocked, Pending for Approval, QA Pending, QA In Progress.
* Opciones específicas para cada tipo de proceso, como `DEACTIVATION_TOGGLE_CHOICES`, `UNIT_TRANSFER_TYPE_CHOICES`, `XML_STATE_CHOICES`, `PROPERTY_RECORDS_TYPE_CHOICES`, etc.
El orden de las tuplas en `TEAM_CHOICES` y `TYPE_CHOICES` es relevante para la visualización en la página de resumen de costos. Todos los textos legibles están en inglés.

---
## 7. Validadores (`tasks/validators.py`)

* `validate_file_size(value)`: Validador que verifica si un archivo subido excede el límite de 10MB. Lanza `ValidationError` si es demasiado grande. Se aplica a todos los campos `FileField` relevantes.

---
## 8. Formularios (`tasks/forms.py`)

Todos los `label` y `help_text` están en inglés.

### 8.1. Formularios de Gestión de Usuario
* `CustomUserChangeForm`: Para editar `username`, `email`, `first_name`, `last_name`, `timezone`.
* `CustomPasswordChangeForm`: Para cambiar la contraseña.

### 8.2. Formularios para la Creación de Solicitudes
* **`UserGroupForm(forms.Form)`**: Formulario no vinculado para detalles de grupos en "User Records".
* **`UserRecordsRequestForm(forms.Form)`**: Para creación de "User Records". Ya no incluye `team_selection`.
* **Formularios Específicos por Tipo (`ModelForm` para `UserRecordsRequest`):**
    * `DeactivationToggleRequestForm`: `clean()` valida campos como `properties` y `deactivation_toggle_properties_with_policies` condicionalmente.
    * `UnitTransferRequestForm`: `clean()` valida campos de "Partner to Prospect" y `properties` (requerido si no hay archivo/enlace).
    * `GeneratingXmlRequestForm`: `user_file` obligatorio. `priority` por defecto en vista. `clean()` valida selección de carrier y ZIPs condicionales.
    * `AddressValidationRequestForm`: `clean()` valida `address_validation_opportunity_id` (requerido si no hay archivos múltiples ni `user_link`).
    * `StripeDisputesRequestForm`: `user_file` obligatorio. `priority` por defecto en vista. `clean()` valida que al menos un tipo de disputa sea mayor a cero.
    * `PropertyRecordsRequestForm`: `clean()` con lógica compleja para campos `property_records_*` condicionales y anidados (ej. "Coverage Type/Amount") y si no se provee archivo/enlace.
    * Todos estos formularios manejan campos de `priority` y programación (`schedule_request`, `scheduled_date`) con validación de fecha futura.

### 8.3. Formularios para Acciones de Flujo de Trabajo y Operación
* **`BlockForm`, `ResolveForm`, `RejectForm`**: Formularios simples para capturar razones/mensajes.
* **`OperateForm(forms.ModelForm)`**: Formulario genérico para ingresar detalles de operación. Su método `__init__` personaliza los campos visibles y su obligatoriedad (`required`) basado en el `type_of_process` de la instancia de la solicitud.
    * Para **"Address Validation"**: Hace obligatorios `av_number_of_units`, `av_number_of_invalid_units`, `link_to_assets`, `operating_notes`. Pre-llena `av_number_of_units`.
    * Para **"Stripe Disputes"**: Hace obligatorios `stripe_premium_disputes`, `stripe_ri_disputes`, `operating_notes`.
    * Para otros tipos, los campos numéricos y notas son generalmente opcionales.
* **`GeneratingXmlOperateForm(forms.ModelForm)`**: Específico para operar/completar solicitudes "Generating XML".
    * Campos: `operating_notes` (opcional), `qa_needs_file_correction` (checkbox).
    * **Campos de Archivo Dinámicos**: `__init__` añade `FileField`s (ej. `op_ut_rvic_csv`) basados en `xml_state` y carriers, mapeados a `operator_rvic_file_slot1`, etc.
    * `save()` sobrescrito para manejar la asignación de estos archivos dinámicos.
* **`OperationPriceForm(forms.ModelForm)`**: Para el modelo `OperationPrice`, incluye todos los campos (con nuevos y renombrados).

---
## 9. Lógica de las Vistas (`tasks/views.py`)


### 9.1. Funciones Auxiliares y Control de Permisos
Funciones como `is_admin(user)`, `is_leadership(user)`, `is_agent(user)`, `user_in_group(user, group_name)`, y la nueva `user_is_admin_or_leader(user)` se usan con `@user_passes_test` para restringir acceso. Decoradores `user_belongs_to_*_team` controlan el acceso a vistas de creación.

### 9.2. Vistas Principales (Home, Profile, Choose Request Type)
* `home`: Página de inicio.
* `profile`: Permite al usuario actualizar su información (`CustomUserChangeForm`) y contraseña (`CustomPasswordChangeForm`).
* `choose_request_type`: Presenta opciones para crear nuevos tipos de solicitud.

### 9.3. Vistas de Creación de Solicitudes (Detalle por Tipo)
Cada tipo de solicitud tiene una vista dedicada (ej. `user_records_request`, `deactivation_toggle_request`).
* **Lógica de Asignación de Equipo Actualizada:** Para solicitudes de Revenue/Support, si el usuario pertenece a ambos grupos (`TEAM_REVENUE` y `TEAM_SUPPORT`), la vista muestra un mensaje de error y redirige. Si pertenece solo a uno, el campo `team` se asigna automáticamente.
* Manejan la lógica de programación (status `scheduled` o `pending`/`pending_approval` y `effective_start_time_for_tat`).
* `address_validation_request` maneja la subida de múltiples archivos a `AddressValidationFile` usando `transaction.atomic()`.

### 9.4. Vistas de Visualización (Dashboard y Detalle de Solicitud)
* **`portal_operations_dashboard`**: Muestra una tabla paginada de `UserRecordsRequest` con filtros por tipo, estado, equipo y rango de fechas. Pasa `is_admin_user` e `is_leadership_user` al contexto para la columna de costos.
* **`request_detail`**: Muestra detalles completos de una solicitud, incluyendo historial de acciones. Pasa `is_admin_user`, `is_leadership_user` para la sección de costos. Para "Generating XML", instancia y pasa `GeneratingXmlOperateForm` como `form_for_modal`.

### 9.5. Vista de Resumen de Gastos del Cliente (`client_cost_summary_view`)
* **Nueva Vista Protegida:** `@login_required` y `@user_passes_test(user_is_admin_or_leader)`.
* **Filtros:** Acepta `start_date` y `end_date` (GET), con el mes actual como default.
* **Cálculos:** Filtra `UserRecordsRequest` por `status='completed'` y rango de fechas. Agrega `grand_total_client_price_completed` para el gran total. Calcula subtotales por `team` y por `type_of_process`, respetando el orden de `TEAM_CHOICES` y `TYPE_CHOICES`.
* **Datos para Gráficos:** Prepara listas de etiquetas y datos para dos pie charts (costos por equipo/proceso) y cinco scatter plots con líneas suavizadas (costo vs. `completed_at` para 5 tipos de proceso, desglosado por Revenue/Support). Los puntos de los scatter plots incluyen el `pk` de la solicitud.
* **Contexto:** Pasa todos los datos, incluyendo una plantilla de URL para `request_detail` (usada por los hipervínculos de los scatter plots), a `client_cost_summary.html`.

### 9.6. Vistas de Generación de Reportes CSV
Tres nuevas vistas para la generación de reportes, cada una con su propio formulario de filtros y lógica de consulta.
* **`generate_revenue_support_report_view(request)`**: Maneja `revenue_support_report_form.html`. Filtros: Fecha, Status (múltiple, incluye Scheduled/PendingApproval, "In Progress" agrupado), Tipo de Proceso (obligatorio, de 5 opciones), Equipo (Revenue, Support, Ambos). Llama a la función helper CSV específica del tipo de proceso seleccionado.
* **`generate_compliance_xml_report_view(request)`**: Maneja `compliance_xml_report_form.html`. Filtros: Fecha, Status, Estado XML (múltiple), Carriers (RVIC, SSIC; si ambos se seleccionan, busca `xml_carrier_rvic=True` Y `xml_carrier_ssic=True`). Llama a `_generate_generating_xml_csv()`.
* **`generate_accounting_stripe_report_view(request)`**: Maneja `accounting_stripe_report_form.html`. Filtros: Fecha, Status. Llama a `_generate_stripe_disputes_csv()`.
* **Funciones Auxiliares `_generate_*_csv(request_items, filename)`**: Siete funciones (una por tipo de proceso) que toman un queryset filtrado, definen encabezados CSV específicos (incluyendo todos los campos generales y específicos del tipo), formatean los datos y retornan un `HttpResponse` CSV.

### 9.7. Vistas de Acciones del Flujo de Trabajo (Detalle por Acción)
Estas vistas manejan las transiciones de estado y la lógica asociada.
* `operate_request`: Cambia estado a 'In Progress'.
* `block_request`, `resolve_request`: Crean `BlockedMessage`/`ResolvedMessage`. Actualizan Salesforce para 'Address Validation' si la solicitud tiene `salesforce_standard_opp_id`.
* `send_to_qa_request`: Utiliza `OperateForm` o `GeneratingXmlOperateForm`. Para `GeneratingXmlOperateForm`, el campo `qa_needs_file_correction` se oculta (decisión de QA). Establece `is_rejected_previously = False`.
* `qa_request`: Cambia estado a 'QA In Progress'.
* `complete_request`: Utiliza `OperateForm` o `GeneratingXmlOperateForm`. Cambia estado a 'Completed'.
    * **Cálculo y Almacenamiento de Costos:** Obtiene `OperationPrice.objects.first()`. Calcula todos los subtotales de precios al cliente, costos de operación y costos de QA basados en los conteos de la solicitud y los precios/costos unitarios. Almacena estos valores en los campos `*_completed` de `UserRecordsRequest`.
    * Actualiza Salesforce para 'Address Validation'.
* `cancel_request`, `uncancel_request`: Manejan cancelación y reactivación.
* `reject_request`: Crea `RejectedMessage`, revierte estado, establece `is_rejected_previously = True`.
* `approve_deactivation_toggle`: Para "Deactivation/Toggle", maneja aprobación y estado/TAT según `scheduled_date`.
* `set_update_needed_flag`, `clear_update_needed_flag`: Gestionan el flag de solicitud de actualización.

---
## 10. Estructura y Contenido de las Plantillas (`tasks/templates/`)
Desarrolladas con Bootstrap 5. Textos de UI directamente en inglés.

### 10.1. Plantilla Base (`base.html`)

Define la estructura común: navbar, footer, bloques para `title`, `extra_css`, `content`, `extra_js`.
* **Barra de Navegación Actualizada**:
    * Enlace "Manage Prices" visible para `user.is_superuser` o `user.is_staff`.
    * Enlace "Cost Summary" individual visible para `is_admin_user` o `is_leadership_user`.
    * Menú desplegable "CSV Reports" (antes "Reports") visible para `is_admin_user` o `is_leadership_user`, con enlaces directos a los formularios de generación de reportes para Revenue/Support, Compliance, y Accounting. Se eliminó el sub-encabezado y el separador internos.

### 10.2. Plantillas de Creación de Solicitudes
* **`users_records_request.html`** (antes `users_records.html`): Para "User Records".
* Otras plantillas (`deactivation_toggle_request.html`, `generating_xml_request.html`, etc.) para cada tipo de proceso, con sus campos y lógica JS específica para condicionalidad y programación.

### 10.3. Plantilla del Dashboard (`rhino_operations_dashboard.html`)
(Antes `portal_operations_dashboard.html`).
* Tabla de solicitudes con filtros por tipo, estado, equipo, y rango de fechas.
* **Nueva Columna "Total Cost (Client)"**: Condicionalmente visible para `admin` o `leadership`, muestra `grand_total_client_price_completed` para solicitudes completadas. `colspan` del mensaje `{% empty %}` ajustado dinámicamente.

### 10.4. Plantillas de Detalle de Solicitud
(ej. `user_records_detail.html`, `generating_xml_detail.html`, etc.)
* Muestran información completa, historial, y botones de acción condicionales.
* **Nueva Sección "Price Breakdown"**: Visible para `admin`/`leadership` si `status == 'completed'`. En una tarjeta centrada de ancho reducido. Muestra `grand_total_client_price_completed` y subtotales relevantes.
* **Modales para `generating_xml_detail.html` y `stripe_disputes_detail.html`**: Usan `GeneratingXmlOperateForm` y `OperateForm` (adaptado) respectivamente.

### 10.5. Plantilla de Resumen de Gastos (`client_cost_summary.html`)
* Nueva plantilla para `/rhino/client_cost_summary/`.
* Formulario de filtro de fechas (default mes actual).
* Muestra Gran Total y tablas/listas de subtotales por equipo y tipo de proceso (ordenadas según `CHOICES`).
* **Gráficos (Chart.js):**
    * Dos pie charts para distribución de costos (equipo y proceso) con bordes negros.
    * Cinco gráficos de dispersión con líneas suavizadas (`type: 'line'`, `tension`) para los 5 tipos de proceso principales. Ejes: `grand_total_client_price_completed` vs `completed_at`. Dos series por gráfico (Revenue, Support).
    * Los puntos en los scatter plots son hipervínculos a `request_detail` (requiere pasar `pk` en los datos y plantilla de URL a JS).
* JavaScript incluye Chart.js y `chartjs-adapter-date-fns`.

### 10.6. Nuevas Plantillas para Formularios de Reportes CSV
* **`revenue_support_report_form.html`**: Filtros de fecha, status (múltiple), tipo de proceso (desplegable obligatorio), equipo (Revenue, Support, Ambos).
* **`compliance_xml_report_form.html`**: Filtros de fecha, status, Estado XML (múltiple), Carriers (RVIC, SSIC).
* **`accounting_stripe_report_form.html`**: Filtros de fecha y status.

---
## 11. Tareas Programadas y en Segundo Plano (`django-q2`)

### 11.1. Procesamiento de Solicitudes Programadas (`tasks/scheduled_jobs.py`)

* `process_scheduled_requests()`: Busca solicitudes con `status='scheduled'` y `scheduled_date <= hoy`. Cambia su `status` a `'pending'` y establece `effective_start_time_for_tat`.

### 11.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)

* `sync_salesforce_opportunities_task()`:
    * **Funcionalidad completada y probada.**
    * **Control de Pausa/Reanudación:** Verifica el modelo `ScheduledTaskToggle` (para `task_name='salesforce_sync_opportunities'`). Si `is_enabled` es `False`, la tarea no se ejecuta.
    * Se conecta a Salesforce, ejecuta una consulta SOQL detallada para Opportunities, y para cada una:
        * Crea una `UserRecordsRequest` de tipo `'address_validation'`, mapeando campos relevantes (Partner Name, IDs, nombre de Opportunity, etc.).
        * Obtiene y crea registros `SalesforceAttachmentLog` para los archivos adjuntos de la Opportunity.
        * Actualiza el campo `Invisible_Status__c` de la Opportunity en Salesforce a 'In Progress'.
    * Utiliza un usuario de sistema (`SALESFORCE_SYSTEM_USER_EMAIL`) para `requested_by`.

### 11.3. Configuración de Programación de Tareas (`tasks/apps.py`)

* Dentro del método `ready()` de `TasksConfig(AppConfig)`:
    * Se asegura de que `django_q` esté en `INSTALLED_APPS`.
    * Crea o verifica la existencia de las tareas programadas en el modelo `Schedule` de `django-q2`:
        * `process_scheduled_requests`: Ejecución `Schedule.DAILY` (1 PM UTC).
        * `sync_salesforce_opportunities_task`: Ejecución `Schedule.CRON` ('0 13,16,19 \* \* \*' - 1 PM, 4 PM, 7 PM UTC).

---
## 12. Interfaz de Administración de Django (`tasks/admin.py`)

Personalizaciones para una gestión de datos eficiente.
* **`CustomUserAdmin`**: Muestra `timezone` y otros campos relevantes.
* **`UserRecordsRequestAdmin`**:
    * `list_display`, `list_filter`, `search_fields` configurados.
    * `readonly_fields` extensos para proteger la integridad de los datos (timestamps, datos generados, campos específicos, detalles de operación, **nuevos campos de costos `*_completed`**).
    * `fieldsets` organizados en secciones colapsables, incluyendo los nuevos campos de costos.
    * Inlines para `AddressValidationFile`, `BlockedMessage`, `ResolvedMessage`, `RejectedMessage`.
    * Acciones personalizadas para disparar manualmente `sync_salesforce_opportunities_task` y `process_scheduled_requests`.
* **`OperationPriceAdmin`**: `fieldsets` actualizados para reflejar los nuevos campos de precios/costos y el campo renombrado (`manual_property_update_*`). Organizados por "Client Prices", "Operate Costs", "QA Costs".
* **`ScheduledTaskToggleAdmin`**: Nueva clase admin para el modelo `ScheduledTaskToggle`. Permite editar `is_enabled` directamente en la lista. `task_name` no es editable tras la creación.
* Otras clases admin (`HistoryMessageAdmin`, `SalesforceAttachmentLogAdmin`, `AddressValidationFileAdmin`) con sus respectivas configuraciones de visualización y permisos.

---
## 13. Configuración del Entorno de Desarrollo
*(Pasos estándar: Clonar el repositorio. Crear y activar un entorno virtual (ej. `python -m venv venv`, `source venv/bin/activate`). Instalar dependencias: `pip install -r requirements.txt`. Crear un archivo `.env` en la raíz del proyecto con variables como `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=True`, y las credenciales de Salesforce. Aplicar migraciones: `python manage.py migrate`. Crear un superusuario: `python manage.py createsuperuser`. Ejecutar el servidor de desarrollo: `python manage.py runserver`. Ejecutar el cluster de Django-Q2 en una terminal separada: `python manage.py qcluster`.)*

---
## 14. Despliegue (Heroku)
*(La aplicación está preparada para el despliegue en Heroku. Requiere un `Procfile` (con entradas `web`, `worker`, `release`), un `runtime.txt`, `requirements.txt` actualizado. `settings.py` está configurado para adaptarse a variables de entorno de Heroku. El archivo `yender.yaml` ha sido eliminado. Se necesitarán buildpacks y add-ons de Heroku (Postgres).)*

---
## 15. Consideraciones Adicionales y Próximos Pasos
* Realizar pruebas exhaustivas de todas las funcionalidades, incluyendo los nuevos reportes CSV, los filtros, los cálculos de costos y la interacción de los gráficos en la página de resumen de costos.
* Optimizar las consultas de base de datos para los reportes y el resumen de costos si el volumen de datos es muy alto.
* Si se decide implementar la internacionalización completa, se deberán aplicar las etiquetas `{% trans %}` en todas las plantillas y gestionar los archivos de traducción `.po`.
* Planificar e implementar un sistema de notificaciones por correo electrónico para eventos clave.
* Continuar el refinamiento de la interfaz de usuario (UI) y la experiencia de usuario (UX).
* Crear documentación detallada para los usuarios finales de la plataforma.

---