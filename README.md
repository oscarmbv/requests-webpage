# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** (Basado en análisis de archivos de GitHub al 26 de mayo de 2025)
**Fecha de Actualización del README:** 26 de mayo de 2025

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
        * [5.2.6. Métodos y Propiedades del Modelo](#526-métodos-y-propiedades-del-modelo)
        * [5.2.7. Clase Meta (UserRecordsRequest)](#527-clase-meta-userrecordsrequest)
    * [5.3. `AddressValidationFile(models.Model)`](#53-addressvalidationfilemodelsmodel)
    * [5.4. Modelos de Historial (`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`)](#54-modelos-de-historial-blockedmessage-resolvedmessage-rejectedmessage)
    * [5.5. `OperationPrice(models.Model)`](#55-operationpricemodelsmodel)
    * [5.6. `SalesforceAttachmentLog(models.Model)`](#56-salesforceattachmentlogmodelsmodel)
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

`requests_webpage` es una aplicación web integral construida sobre el framework Django. Su propósito fundamental es servir como una plataforma centralizada y eficiente para la gestión de una variedad de solicitudes y procesos operativos internos. La aplicación está diseñada para ser altamente personalizable, permitiendo la definición de diferentes tipos de solicitudes, cada una con sus propios flujos de trabajo, campos de datos específicos, y lógicas de asignación a los equipos responsables.

Las características clave incluyen la creación y seguimiento de solicitudes, asignación a operadores y agentes de QA, gestión de estados (desde 'pendiente' hasta 'completado', incluyendo 'bloqueado', 'programado', etc.), un sistema de priorización, la capacidad de adjuntar archivos o enlaces, y un historial detallado de acciones por solicitud. Funcionalidades avanzadas como la programación de solicitudes para activación futura y el cálculo de Tiempos de Respuesta (Turn Around Time - TAT) mejoran la planificación y el monitoreo de la eficiencia operativa.

Una integración significativa con Salesforce ha sido implementada para automatizar la creación de solicitudes de "Address Validation" directamente desde Opportunities en Salesforce, incluyendo la sincronización de archivos adjuntos. La plataforma utiliza `django-q2` para la gestión de tareas en segundo plano y programadas, asegurando que procesos como la activación de solicitudes o la sincronización con Salesforce no bloqueen la interfaz de usuario y se ejecuten de manera fiable.

El sistema de administración de Django se ha personalizado para facilitar la gestión de los datos y la configuración de la plataforma. La interfaz de usuario está construida con Bootstrap 5, buscando ofrecer una experiencia responsiva e intuitiva.

---

## 2. Estructura Detallada del Proyecto

El proyecto sigue una organización de archivos y directorios típica de Django, promoviendo la modularidad y la separación de responsabilidades[cite: 1].

* **Directorio Raíz del Proyecto (`requests_webpage/`)**:
    * `requests_webpage/`: Contiene los archivos de configuración a nivel de proyecto.
        * `settings.py`: Archivo principal de configuración de Django (ver sección 3.1). [cite: 4]
        * `urls.py`: Archivo principal de enrutamiento de URLs (ver sección 4.1). [cite: 2]
        * `wsgi.py` / `asgi.py`: Puntos de entrada para servidores web compatibles con WSGI y ASGI, respectivamente, para el despliegue. [cite: 2]
    * `tasks/`: Aplicación Django principal que encapsula toda la lógica de negocio de la plataforma. [cite: 3]
        * `models.py`: Define los modelos ORM de Django que representan las tablas de la base de datos (ver sección 5).
        * `views.py`: Contiene la lógica de las vistas que procesan las solicitudes HTTP y devuelven respuestas (ver sección 9).
        * `forms.py`: Define los formularios Django utilizados para la entrada y validación de datos del usuario (ver sección 8).
        * `urls.py`: Define las rutas URL específicas para la aplicación `tasks` (ver sección 4.2).
        * `admin.py`: Personaliza la interfaz del sitio de administración de Django para los modelos de la aplicación `tasks` (ver sección 12).
        * `choices.py`: Archivo centralizado para las constantes de opciones (`choices`) utilizadas en los campos de los modelos (ver sección 6).
        * `validators.py`: Contiene funciones de validación personalizadas para campos de modelos o formularios (ver sección 7).
        * `scheduled_jobs.py`: Contiene la lógica para las tareas que se ejecutan de forma programada utilizando `django-q2` (ver sección 11.1).
        * `salesforce_sync.py`: Contiene la lógica para la tarea de sincronización con Salesforce (ver sección 11.2).
        * `templatetags/`: Directorio para tags y filtros de plantillas personalizados (ej. `duration_filters.py`).
        * `templates/tasks/`: Directorio que contiene las plantillas HTML para la renderización de la interfaz de usuario de la aplicación `tasks` (ver sección 10).
        * `static/tasks/`: Directorio para archivos estáticos (CSS, JavaScript, imágenes) específicos de la aplicación `tasks`.
        * `migrations/`: Directorio que almacena los archivos de migración de la base de datos generados por Django cada vez que se realizan cambios en los modelos.
        * `apps.py`: Archivo de configuración de la aplicación `tasks`, donde también se inicializan las tareas programadas de `django-q2`.
    * `manage.py`: Una utilidad de línea de comandos que permite interactuar con el proyecto Django de diversas maneras (ej. ejecutar el servidor de desarrollo, crear migraciones, ejecutar tareas de administración). [cite: 2]
    * `.env`: (No versionado en Git) Archivo utilizado para almacenar variables de entorno sensibles como `SECRET_KEY`, credenciales de base de datos y claves API, cargadas mediante `django-environ`.
    * `requirements.txt`: Un archivo de texto que lista todas las dependencias de Python del proyecto con sus versiones exactas, permitiendo una fácil replicación del entorno.
    * `README.md`: Este archivo, que proporciona una visión general y documentación del proyecto.
    * `yender.yaml` (o `render.yaml`): Archivo de configuración específico para el despliegue en la plataforma Render. Se planea migrar a Heroku, lo que implicará el uso de un `Procfile`.

---
## 3. Configuración Central del Proyecto (`requests_webpage/settings.py`)

Este archivo es el corazón de la configuración de la aplicación Django[cite: 4].

### 3.1. Variables Esenciales de Seguridad y Despliegue
* **`SECRET_KEY`**: Una cadena larga y aleatoria utilizada por Django para la firma criptográfica, la protección contra CSRF y la gestión de sesiones. Es crucial mantenerla secreta en producción. [cite: 4]
* **`DEBUG`**: Un booleano que controla el modo de depuración. [cite: 5]
    * Si es `True` (típicamente en desarrollo): Django muestra páginas de error detalladas con rastreos de pila y recarga automáticamente el servidor cuando se detectan cambios en el código. [cite: 5]
    * Si es `False` (obligatorio en producción): Deshabilita la información de depuración sensible y mejora el rendimiento. [cite: 6]
* **`ALLOWED_HOSTS`**: Una lista de cadenas que representan los nombres de host/dominio que la aplicación Django puede servir. En producción, debe configurarse con los dominios exactos. [cite: 6] Actualmente configurado para `['127.0.0.1', 'localhost', '.onrender.com']`.
* **`CSRF_TRUSTED_ORIGINS`**: Lista de orígenes confiables para solicitudes seguras (HTTPS) al modificar datos, importante para producción (ej. `['https://*.onrender.com']`).

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`) [cite: 7]
Esta tupla lista todas las aplicaciones Django que están activas en este proyecto. Django utiliza esta lista para cargar modelos, plantillas, comandos de administración, etc.
* **Aplicaciones Estándar de Django:**
    * `django.contrib.admin`: El sitio de administración automático. [cite: 8]
    * `django.contrib.auth`: El framework de autenticación de Django. [cite: 8]
    * `django.contrib.contenttypes`: Un framework para tipos de contenido genéricos. [cite: 8]
    * `django.contrib.sessions`: El framework de sesiones. [cite: 8]
    * `django.contrib.messages`: El framework de mensajes flash. [cite: 8]
    * `django.contrib.staticfiles`: Framework para la gestión de archivos estáticos. [cite: 8]
* **Aplicación Principal del Proyecto:**
    * `tasks`: La aplicación personalizada donde reside la lógica de negocio principal de la plataforma. [cite: 8]
* **Aplicaciones de Terceros:**
    * `django_q`: Para la gestión de tareas en segundo plano y programadas (específicamente, se utiliza el fork mantenido `django-q2`). [cite: 9]

### 3.3. Middleware [cite: 10]
Define una serie de "hooks" o capas que procesan las solicitudes y respuestas HTTP secuencialmente. El orden es importante.
* `django.middleware.security.SecurityMiddleware`: Proporciona varias mejoras de seguridad.
* `whitenoise.middleware.WhiteNoiseMiddleware`: Para servir archivos estáticos eficientemente en producción.
* `django.contrib.sessions.middleware.SessionMiddleware`: Habilita el soporte de sesiones.
* `django.middleware.common.CommonMiddleware`: Añade funcionalidades comunes (ej. `APPEND_SLASH`).
* `django.middleware.csrf.CsrfViewMiddleware`: Protección contra ataques Cross-Site Request Forgery.
* `django.contrib.auth.middleware.AuthenticationMiddleware`: Asocia usuarios con solicitudes usando sesiones.
* `django.contrib.messages.middleware.MessageMiddleware`: Habilita el sistema de mensajes flash.
* `django.middleware.clickjacking.XFrameOptionsMiddleware`: Protección contra clickjacking.
* `django.middleware.locale.LocaleMiddleware`: Habilita la internacionalización basada en la solicitud. [cite: 11]

### 3.4. Modelo de Usuario Personalizado (`AUTH_USER_MODEL`)
* `AUTH_USER_MODEL = 'tasks.CustomUser'`: Le dice a Django que use el modelo `CustomUser` definido en la aplicación `tasks` como el modelo de usuario para todo el proyecto, en lugar del modelo `User` predeterminado de Django. [cite: 12]

### 3.5. Configuración de la Base de Datos (`DATABASES`)
* Utiliza `dj_database_url.config()` para configurar la base de datos a partir de la variable de entorno `DATABASE_URL`. Esto permite cambiar fácilmente entre diferentes motores de base de datos (SQLite, PostgreSQL, MySQL) según el entorno.
* Por defecto, si `DATABASE_URL` no está definida, usa SQLite (`sqlite:///db.sqlite3`) en el directorio base del proyecto. [cite: 13]
* `conn_max_age=600`: Configura la vida útil máxima de las conexiones a la base de datos.

### 3.6. Gestión de Archivos Estáticos y Multimedia
* **Archivos Estáticos (CSS, JavaScript, Imágenes de la aplicación):**
    * `STATIC_URL = 'static/'`: URL base desde la cual se servirán los archivos estáticos. [cite: 14]
    * `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`: Directorio absoluto donde `collectstatic` reunirá todos los archivos estáticos para el despliegue.
    * `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`: Utiliza WhiteNoise para servir archivos estáticos de manera eficiente en producción, incluyendo compresión y versionado.
* **Archivos Multimedia (Archivos subidos por el usuario):**
    * `MEDIA_URL = '/media/'`: URL base para los archivos subidos por los usuarios. [cite: 15]
    * `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')`: Directorio en el sistema de archivos donde se almacenarán los archivos subidos por los usuarios. [cite: 15]

### 3.7. Internacionalización (i18n) y Localización (l10n) [cite: 16]
* `LANGUAGE_CODE = 'en-us'`: Idioma por defecto de la aplicación. [cite: 16]
* `TIME_ZONE = 'UTC'`: Zona horaria interna con la que Django almacena y maneja todas las fechas y horas. [cite: 17]
* `USE_I18N = True`: Habilita el sistema de traducción de Django. [cite: 18]
* `USE_TZ = True`: Habilita el soporte de zonas horarias para los `DateTimeField`. Django almacenará las fechas y horas en UTC en la base de datos y las convertirá a la zona horaria del usuario final (o a la zona horaria activa) al mostrarlas. [cite: 18]

### 3.8. Configuración de Tareas en Segundo Plano (Django-Q2) [cite: 19]
* `Q_CLUSTER`: Un diccionario que configura el comportamiento del cluster de `django-q2`.
    * `name`: Nombre para identificar el cluster (ej. `RequestWebpageScheduler_Q2`).
    * `workers`: Número de procesos worker para ejecutar tareas.
    * `timeout`: Tiempo máximo (en segundos) que una tarea puede ejecutarse antes de ser terminada.
    * `retry`: Tiempo (en segundos) después del cual una tarea fallida se reintentará.
    * `queue_limit`: Número máximo de tareas que los workers intentarán obtener de la cola a la vez.
    * `bulk`: Número máximo de tareas que un worker procesará antes de reciclarse (para liberar memoria).
    * `orm`: Especifica la conexión de base de datos de Django a usar para almacenar las tareas y resultados (ej. 'default').
    * `catch_up`: Si es `False` (como está configurado), las tareas programadas que deberían haberse ejecutado mientras el cluster estaba caído no se ejecutarán al iniciar; solo se programarán para su próxima ejecución futura.
    * `log_level`: Nivel de logging para los workers de Django-Q.

### 3.9. Configuración de Salesforce [cite: 20]
* Se utiliza `django-environ` para cargar de forma segura las credenciales y configuraciones de Salesforce desde un archivo `.env` o variables de entorno del sistema. Esto evita tener información sensible directamente en el código.
* Variables cargadas: `SF_USERNAME`, `SF_PASSWORD`, `SF_SECURITY_TOKEN`, `SF_CONSUMER_KEY`, `SF_CONSUMER_SECRET`, `SF_DOMAIN` (ej. 'login' para producción, 'test' para sandboxes), `SF_VERSION` (versión de la API de Salesforce, default '59.0'), `SF_INSTANCE_NAME`.
* `SALESFORCE_LIGHTNING_BASE_URL`: Se construye dinámicamente usando `SF_INSTANCE_NAME` para formar la URL base de la interfaz Lightning de Salesforce, utilizada para generar enlaces directos a registros como Opportunities. [cite: 21]

### 3.10. Logging
* Configuración detallada de `LOGGING` para formatear y manejar los mensajes de log de la aplicación.
* **Formateadores (`formatters`)**: `verbose` (detallado) y `simple`.
* **Manejadores (`handlers`)**:
    * `console`: Envía logs a la consola (stderr).
    * `file_tasks`: Envía logs de la aplicación `tasks` a un archivo (`logs/tasks_app.log`).
* **Loggers (`loggers`)**:
    * `django`: Configuración para logs internos de Django (nivel INFO).
    * `django.request`: Específico para errores de request/response (nivel ERROR).
    * `tasks`: Logger para la aplicación `tasks` (nivel DEBUG, para mostrar todos los mensajes de la app).
    * `django_q`: Logger específico para `django-q2` (nivel INFO).
* `LOG_DIR`: Directorio base para los archivos de log.

### 3.11. Redirecciones y Otros Ajustes
* `LOGOUT_REDIRECT_URL = '/accounts/login/'`: Página a la que se redirige al usuario después de cerrar sesión.
* `LOGIN_REDIRECT_URL = '/portal/dashboard/'`: Página a la que se redirige al usuario después de iniciar sesión exitosamente.
* `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`: Configura el tipo de campo de clave primaria por defecto.
* `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`: Para asegurar que Django reconozca correctamente las solicitudes HTTPS detrás de un proxy.

---
## 4. Enrutamiento de URLs

### 4.1. Enrutamiento Principal (`requests_webpage/urls.py`)
Este archivo define el mapeo de las URLs de nivel superior del proyecto a las vistas o a otros archivos de configuración de URLs.
* `path('admin/', admin.site.urls)`: Mapea todas las URLs del sitio de administración de Django al prefijo `/admin/`.
* `path('accounts/', include('django.contrib.auth.urls'))`: Incluye las URLs predefinidas por Django para la autenticación de usuarios (login, logout, cambio de contraseña, etc.) bajo el prefijo `/accounts/`. [cite: 22]
* `path('portal/', include('tasks.urls', namespace='tasks'))`: Incluye todas las URLs definidas en el archivo `tasks/urls.py` bajo el prefijo `/portal/`. El argumento `namespace='tasks'` permite referenciar estas URLs en plantillas de forma unívoca (ej. `{% url 'tasks:dashboard' %}`). [cite: 23]
* `path('', tasks_views.home, name='home')`: Mapea la URL raíz del sitio (`/`) a la vista `home` definida en `tasks/views.py`. [cite: 24]
* **Servicio de Archivos Multimedia en Desarrollo**: Si `settings.DEBUG` es `True`, se añaden patrones de URL para servir archivos de `MEDIA_ROOT` a través de `MEDIA_URL`, lo cual es útil solo para desarrollo.

### 4.2. Enrutamiento de la Aplicación `tasks` (`tasks/urls.py`)
Este archivo contiene los patrones de URL específicos de la aplicación `tasks`, todos bajo el prefijo `/portal/` definido en el archivo principal de URLs.
* **Autenticación (Redefinición para plantillas personalizadas si es necesario, aunque el login se maneja en `requests_webpage.urls`):**
    * `path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login')`
    * `path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout')`
* **Vistas Principales y de Usuario:**
    * `path('dashboard/', views.portal_operations_dashboard, name='portal_dashboard')`
    * `path('profile/', views.profile, name='profile')`
    * `path('manage_prices/', views.manage_prices, name='manage_prices')` (restringido a administradores)
* **Vistas de Creación de Solicitudes:**
    * `path('create/', views.choose_request_type, name='choose_request_type')`
    * `path('create/user_records/', views.user_records_request, name='user_records_request')`
    * `path('create/deactivation_toggle/', views.deactivation_toggle_request, name='deactivation_toggle_request')`
    * `path('create/unit_transfer/', views.unit_transfer_request, name='unit_transfer_request')`
    * `path('create/generating_xml/', views.generating_xml_request, name='generating_xml_request')`
    * `path('create/address_validation/', views.address_validation_request, name='address_validation_request')`
    * `path('create/stripe_disputes/', views.stripe_disputes_request, name='stripe_disputes_request')`
    * `path('create/property_records/', views.property_records_request, name='property_records_request')`
* **Vistas de Detalle y Acciones sobre Solicitudes (usando `<int:pk>` para identificar la solicitud):**
    * `path('request/<int:pk>/', views.request_detail, name='request_detail')`
    * `path('request/<int:pk>/operate/', views.operate_request, name='operate_request')`
    * `path('request/<int:pk>/block/', views.block_request, name='block_request')`
    * `path('request/<int:pk>/send_to_qa/', views.send_to_qa_request, name='send_to_qa_request')`
    * `path('request/<int:pk>/qa/', views.qa_request, name='qa_request')`
    * `path('request/<int:pk>/complete/', views.complete_request, name='complete_request')`
    * `path('request/<int:pk>/cancel/', views.cancel_request, name='cancel_request')`
    * `path('request/<int:pk>/resolve/', views.resolve_request, name='resolve_request')`
    * `path('request/<int:pk>/reject/', views.reject_request, name='reject_request')`
    * `path('request/<int:pk>/approve_deactivation_toggle/', views.approve_deactivation_toggle, name='approve_deactivation_toggle')`
    * `path('request/<int:pk>/set_update_flag/', views.set_update_needed_flag, name='set_update_flag')`
    * `path('request/<int:pk>/clear_update_flag/', views.clear_update_needed_flag, name='clear_update_flag')`
    * `path('request/<int:pk>/uncancel/', views.uncancel_request, name='uncancel_request')`

---
## 5. Modelo de Datos Detallado (`tasks/models.py`)

Este archivo define la estructura de la base de datos a través de modelos Django.

### 5.1. `CustomUser(AbstractUser)`
Extiende el modelo `AbstractUser` de Django para personalizar la información del usuario.
* **`email = models.EmailField(unique=True)`**: El campo de email se define como único y es el `USERNAME_FIELD`, lo que significa que los usuarios inician sesión con su dirección de correo electrónico.
* **`timezone = models.CharField(max_length=100, default='UTC', choices=[(tz, tz) for tz in pytz.common_timezones])`**: Almacena la zona horaria preferida del usuario. [cite: 25] El valor por defecto es 'UTC'. Las opciones se generan dinámicamente a partir de `pytz.common_timezones`, ofreciendo una lista completa de zonas horarias válidas. [cite: 25] Esto permite que las fechas y horas se muestren en la aplicación ajustadas a la hora local del usuario. [cite: 26]
* **`REQUIRED_FIELDS = ['username']`**: Aunque el email es el campo de inicio de sesión, `username` sigue siendo un campo requerido por Django, especialmente para la creación de superusuarios a través de la línea de comandos. [cite: 27]
* El campo `receive_notifications` (BooleanField), mencionado en versiones anteriores de la documentación, no está presente en la implementación actual del modelo `CustomUser`. [cite: 26]

### 5.2. `UserRecordsRequest(models.Model)`
Es el modelo central y más complejo, diseñado para almacenar todas las solicitudes operativas de diversos tipos.

#### 5.2.1. Campos Generales y de Identificación
* **`type_of_process = models.CharField(max_length=50, choices=TYPE_CHOICES, default='user_records', db_index=True)`**: Define el tipo de solicitud (ej. 'User Records', 'Deactivation and Toggle', etc.). [cite: 28] Utiliza la constante `TYPE_CHOICES` del archivo `tasks/choices.py`. [cite: 29] Está indexado para optimizar las consultas que filtran por este campo.
* **`unique_code = models.CharField(max_length=20, unique=True, editable=False)`**: Un código único generado automáticamente para cada solicitud (ej. "User-25Q2001"). [cite: 29] No es editable una vez creado.
* **`timestamp = models.DateTimeField(default=now, db_index=True)`**: La fecha y hora exactas en que se creó la solicitud. [cite: 30] Utiliza `django.utils.timezone.now` por defecto y está indexado para búsquedas y ordenamientos eficientes.
* **`requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_requests')`**: Una clave foránea que vincula la solicitud con el `CustomUser` que la creó. [cite: 31] Si el usuario es eliminado, sus solicitudes también lo serán (`on_delete=models.CASCADE`).
* **`team = models.CharField(max_length=20, choices=TEAM_CHOICES, null=True, blank=True, db_index=True, verbose_name="Assigned Team")`**: El equipo asignado para procesar la solicitud (ej. 'Revenue', 'Support'). [cite: 31] Utiliza `TEAM_CHOICES`. Es opcional (`null=True, blank=True`) y está indexado.
* **`priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, db_index=True, verbose_name="Priority")`**: La prioridad de la solicitud ('low', 'normal', 'high'). [cite: 32] Utiliza `PRIORITY_CHOICES` y tiene 'normal' como valor por defecto. Indexado.
* **`partner_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)`**: El nombre del socio o cliente asociado con la solicitud. [cite: 32] Es opcional y está indexado. Este campo se reutiliza para diferentes tipos de procesos.
* **`properties = models.TextField(blank=True, null=True, verbose_name="Properties Affected")`**: Un campo de texto genérico para listar las propiedades afectadas por la solicitud (ej. IDs o nombres de propiedades). [cite: 33]
* **`user_groups_data = models.JSONField(null=True, blank=True)`**: Almacena datos estructurados en formato JSON, específicamente utilizado para los detalles de grupos de usuarios en las solicitudes de tipo "User Records". [cite: 33] Opcional.
* **`special_instructions = models.TextField(blank=True)`**: Un campo de texto para cualquier instrucción o comentario adicional sobre la solicitud. [cite: 34]
* **`status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)`**: El estado actual de la solicitud (ej. 'pending', 'in_progress', 'completed'). [cite: 34] Utiliza `STATUS_CHOICES` y tiene 'pending' como valor por defecto. Indexado.
* **`update_needed_flag = models.BooleanField(default=False, verbose_name="Update Needed Flag", help_text="Indicates if the requester/team needs a progress update.")`**: Una bandera booleana que, si es `True`, indica que se ha solicitado una actualización sobre el progreso de esta tarea. [cite: 35]
* **`update_requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_records_update_requested_by', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Update Requested By")`**: El usuario que activó la `update_needed_flag`.
* **`update_requested_at = models.DateTimeField(null=True, blank=True, verbose_name="Update Requested At")`**: El momento en que se activó la `update_needed_flag`.
* **`user_file = models.FileField(upload_to='user_uploads/', null=True, blank=True, validators=[validate_file_size], verbose_name='Upload File')`**: Permite adjuntar un archivo a la solicitud. [cite: 36] Los archivos se guardan en el directorio `user_uploads/` dentro de `MEDIA_ROOT`. Se aplica el validador `validate_file_size`. [cite: 36]
* **`user_link = models.URLField(max_length=200, blank=True, null=True)`**: Permite proporcionar una URL como información adicional o en lugar de un archivo. [cite: 36]

#### 5.2.2. Campos de Flujo de Trabajo y Asignación
* **`operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='operated_requests', db_index=True)`**: El agente asignado para operar/procesar la solicitud. [cite: 36] Si el usuario operador es eliminado, este campo se establece en `NULL`.
* **`qa_agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='qa_requests', db_index=True)`**: El agente asignado para realizar el control de calidad (QA) de la solicitud. [cite: 37]
* **Timestamps Específicos del Flujo:**
    * `operated_at = models.DateTimeField(null=True, blank=True, db_index=True)`: Momento en que un operador comienza a trabajar en la solicitud. [cite: 37]
    * `qa_pending_at = models.DateTimeField(null=True, blank=True)`: Momento en que la solicitud se envía a la cola de QA. [cite: 37]
    * `qa_in_progress_at = models.DateTimeField(null=True, blank=True)`: Momento en que un agente de QA comienza la revisión. [cite: 37]
    * `completed_at = models.DateTimeField(null=True, blank=True, db_index=True)`: Momento en que la solicitud se marca como completada. [cite: 37]
    * `cancelled_at = models.DateTimeField(null=True, blank=True)`: Momento en que la solicitud se cancela. [cite: 37]
* **`cancel_reason = models.TextField(blank=True, null=True)`**: Razón textual por la cual la solicitud fue cancelada. [cite: 37]
* **`cancelled = models.BooleanField(default=False)`**: Un flag que indica si la solicitud ha sido cancelada (usado en conjunto con `status='cancelled'`).
* **`cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_cancelled_by', null=True, blank=True, on_delete=models.SET_NULL)`**: Usuario que canceló la solicitud.
* **`uncanceled_at = models.DateTimeField(null=True, blank=True)`**: Momento en que una solicitud previamente cancelada fue reactivada.
* **`uncanceled_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_uncancelled_by', null=True, blank=True, on_delete=models.SET_NULL)`**: Usuario que reactivó una solicitud cancelada.
* **`scheduled_date = models.DateField(null=True, blank=True, verbose_name="Scheduled Date", help_text="Date for which the request is scheduled to become active (pending).")`**: Fecha en la que una solicitud programada debe pasar al estado 'Pending'. [cite: 38]
* **`effective_start_time_for_tat = models.DateTimeField(null=True, blank=True, verbose_name="Effective Start Time for TAT", help_text="Timestamp marking the real start of the work cycle for TAT calculation.")`**: Momento que se considera el inicio real del trabajo para calcular el TAT. [cite: 39] Puede ser el `timestamp` de creación o el momento de activación para solicitudes programadas/aprobadas.
* **`is_rejected_previously = models.BooleanField(default=False, verbose_name="Previously Rejected by QA", help_text="Indicates if the request was rejected by QA and needs re-submission to QA.")`**: Una bandera que se activa si la solicitud ha sido rechazada por QA al menos una vez. [cite: 39]

#### 5.2.3. Campos de Detalles de Operación/QA (Comunes) [cite: 40]
Estos campos son generalmente opcionales y se utilizan para registrar métricas o notas durante las fases de operación y QA.
* `num_updated_users = models.PositiveIntegerField(null=True, blank=True)`: Número de usuarios actualizados/añadidos/eliminados.
* `num_updated_properties = models.PositiveIntegerField(null=True, blank=True)`: Número de propiedades actualizadas.
* `bulk_updates = models.PositiveIntegerField(null=True, blank=True)`: Conteo de actualizaciones masivas.
* `manual_updated_properties = models.PositiveIntegerField(null=True, blank=True)`: Conteo de propiedades actualizadas manualmente.
* `manual_updated_units = models.PositiveIntegerField(null=True, blank=True, verbose_name="Manual Updated Units")`: Conteo de unidades actualizadas manualmente.
* `update_by_csv_rows = models.PositiveIntegerField(null=True, blank=True)`: Número de filas procesadas desde un CSV.
* `processing_reports_rows = models.PositiveIntegerField(null=True, blank=True)`: Número de filas procesadas desde informes.
* `operator_spreadsheet_link = models.URLField(max_length=1024, blank=True, null=True, verbose_name="Operator Spreadsheet Link")`: Enlace a una hoja de cálculo utilizada por el operador.
* `operating_notes = models.TextField(blank=True, null=True)`: Notas del operador o del agente de QA.
    * *Nota: El campo `qa_resolved` (BooleanField) existía previamente pero su funcionalidad se integra ahora con el modelo `RejectedMessage` y el flag `is_rejected_previously` en `UserRecordsRequest`. [cite: 41]*

#### 5.2.4. Campos Específicos por `type_of_process`
Todos estos campos son `null=True` y `blank=True` para permitir que el modelo `UserRecordsRequest` sea genérico. Su relevancia y obligatoriedad se manejan en los formularios y vistas correspondientes a cada tipo de proceso.

* **Para `type_of_process = 'deactivation_toggle'`**: [cite: 42]
    * `deactivation_toggle_type = models.CharField(max_length=50, choices=DEACTIVATION_TOGGLE_CHOICES)`: Tipo específico de desactivación o toggle (ej. 'Partner Deactivation', 'Toggle on invites').
    * `deactivation_toggle_active_policies = models.BooleanField()`: Indica si hay pólizas activas en las propiedades afectadas.
    * `deactivation_toggle_properties_with_policies = models.TextField()`: Lista las propiedades que tienen pólizas activas.
    * `deactivation_toggle_context = models.TextField()`: Contexto o justificación para la solicitud.
    * `deactivation_toggle_leadership_approval = models.CharField(max_length=50, choices=LEADERSHIP_APPROVAL_CHOICES)`: Quién del liderazgo aprobó (si aplica).
    * `deactivation_toggle_marked_as_churned = models.BooleanField()`: Indica si el socio fue marcado como "churned" en Salesforce.
    * *Nota: El campo `deactivation_toggle_properties` mencionado en el PDF fue reemplazado por el campo genérico `properties`.* [cite: 42]
* **Para `type_of_process = 'unit_transfer'`**: [cite: 43]
    * `unit_transfer_type = models.CharField(max_length=50, choices=UNIT_TRANSFER_TYPE_CHOICES)`: Tipo de transferencia (ej. 'Partner to Prospect').
    * `unit_transfer_new_partner_prospect_name = models.CharField(max_length=255)`: Nombre del socio o prospecto destino.
    * `unit_transfer_receiving_partner_psm = models.CharField(max_length=255)`: PSM del socio receptor (opcional).
    * `unit_transfer_new_policyholders = models.TextField()`: Nuevos titulares de póliza (opcional).
    * `unit_transfer_user_email_addresses = models.TextField()`: Emails de usuarios para el nuevo socio (opcional).
    * `unit_transfer_prospect_portfolio_size = models.PositiveIntegerField()`: Tamaño del portafolio del prospecto (si aplica).
    * `unit_transfer_prospect_landlord_type = models.CharField(max_length=50, choices=UNIT_TRANSFER_LANDLORD_TYPE_CHOICES)`: Tipo de propietario del prospecto (si aplica).
    * `unit_transfer_proof_of_sale = models.URLField()`: Enlace a la prueba de venta (opcional).
    * *Nota: El campo `unit_transfer_properties` mencionado en el PDF fue reemplazado por el campo genérico `properties`.* [cite: 43]
* **Para `type_of_process = 'generating_xml'`**: [cite: 44]
    * `xml_state = models.CharField(max_length=2, choices=XML_STATE_CHOICES)`: Estado para el cual generar el XML.
    * `xml_carrier_rvic = models.BooleanField(default=False)`: Si se debe generar para el carrier RVIC.
    * `xml_carrier_ssic = models.BooleanField(default=False)`: Si se debe generar para el carrier SSIC.
    * `xml_rvic_zip_file = models.FileField(upload_to='xml_zip_files/', validators=[validate_file_size])`: Archivo ZIP para RVIC (requerido para ciertos estados).
    * `xml_ssic_zip_file = models.FileField(upload_to='xml_zip_files/', validators=[validate_file_size])`: Archivo ZIP para SSIC (requerido para ciertos estados).
    * Campos de Salida de Operación:
        * `operator_rvic_file_slot1`, `operator_rvic_file_slot2`, `operator_ssic_file_slot1`, `operator_ssic_file_slot2` (`FileField`): Para los archivos XML/ZIP generados por el operador.
* **Para `type_of_process = 'address_validation'`**:
    * `address_validation_policyholders = models.TextField()`: Titulares de póliza (entrada manual).
    * `address_validation_opportunity_id = models.CharField(max_length=255)`: ID de la Opportunity (entrada manual o desde SF).
    * `address_validation_user_email_addresses = models.TextField()`: Emails de usuario (entrada manual).
* **Para `type_of_process = 'stripe_disputes'`**: [cite: 44]
    * `stripe_premium_disputes = models.PositiveIntegerField(verbose_name="Rhino Super Premium Disputes")`: Número de disputas premium.
    * `stripe_ri_disputes = models.PositiveIntegerField(verbose_name="Rhino Super RI Disputes")`: Número de disputas RI.
* **Para `type_of_process = 'property_records'`**: [cite: 45]
    * `property_records_type = models.CharField(max_length=50, choices=PROPERTY_RECORDS_TYPE_CHOICES)`: Tipo específico de actualización de registro de propiedad.
    * `property_records_new_names = models.TextField()`: Nuevos nombres de propiedad.
    * `property_records_new_pmc = models.CharField(max_length=255)`: Nueva compañía de gestión de propiedades.
    * `property_records_new_policyholder = models.TextField()`: Nuevo titular de póliza.
    * `property_records_corrected_address = models.TextField()`: Dirección corregida.
    * `property_records_updated_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)`: Tipo de propiedad actualizado.
    * `property_records_units = models.TextField()`: Unidades de propiedad.
    * `property_records_coverage_type = models.CharField(max_length=50, choices=COVERAGE_TYPE_CHOICES)`: Tipo de cobertura.
    * `property_records_coverage_multiplier = models.CharField(max_length=10, choices=COVERAGE_MULTIPLIER_CHOICES)`: Multiplicador de cobertura.
    * `property_records_coverage_amount = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(Decimal('330.00')), MaxValueValidator(Decimal('200000000.00'))])`: Monto de cobertura.
    * `property_records_integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPE_CHOICES)`: Tipo de integración.
    * `property_records_integration_codes = models.TextField()`: Códigos de integración.
    * `property_records_bank_details = models.TextField()`: Detalles bancarios.
    * *Nota: El campo `property_records_properties` mencionado en el PDF fue reemplazado por el campo genérico `properties`.* [cite: 45]

#### 5.2.5. Campos para Integración con Salesforce
Estos campos son específicamente para solicitudes de `type_of_process='address_validation'` que se originan o se vinculan con Salesforce.
* **Información de la Opportunity de Salesforce:** [cite: 46]
    * `salesforce_standard_opp_id = models.CharField(max_length=18, verbose_name="Salesforce Standard Opportunity ID", help_text="The standard 18-character ID of the Opportunity in Salesforce.")`: ID estándar de 18 caracteres de la Opportunity.
    * `salesforce_opportunity_name = models.CharField(max_length=255, verbose_name="Salesforce Opportunity Name")`
    * `salesforce_number_of_units = models.PositiveIntegerField(verbose_name="Salesforce Number of Units")`
    * `salesforce_link = models.URLField(max_length=1024, verbose_name="Salesforce Opportunity Link")`
    * `salesforce_account_manager = models.CharField(max_length=255, verbose_name="Salesforce Account Manager")`
    * `salesforce_closed_won_date = models.DateField(verbose_name="Salesforce Closed Won Date")`
    * `salesforce_leasing_integration_software = models.CharField(max_length=255, verbose_name="Salesforce Leasing Integration Software")`
    * `salesforce_information_needed_for_assets = models.TextField(verbose_name="Salesforce Information Needed For Assets")`
* **Parámetros de Salida/Operación para la Integración con Salesforce (Address Validation):**
    * `assets_uploaded = models.BooleanField(default=False, verbose_name="Assets Uploaded (AV)")`: Indica si los activos se subieron a Salesforce.
    * `av_number_of_units = models.PositiveIntegerField(verbose_name="Number of Units (AV Operation)")`: Número de unidades procesadas en la operación de AV.
    * `av_number_of_invalid_units = models.PositiveIntegerField(default=0, verbose_name="Number of Invalid Units (AV Operation)")`: Número de unidades inválidas encontradas.
    * `link_to_assets = models.URLField(max_length=1024, verbose_name="Link to Assets (AV)")`: Enlace a la hoja de cálculo con los activos.
    * `success_output_link = models.URLField(max_length=1024, verbose_name="Success Output Link (AV)")`: Enlace al resultado de unidades procesadas exitosamente.
    * `failed_output_link = models.URLField(max_length=1024, verbose_name="Failed Output Link (AV)")`: Enlace al resultado de unidades fallidas.
    * `rhino_accounts_created = models.BooleanField(default=False, verbose_name="Rhino Accounts Created? (AV)")`: Indica si se crearon cuentas Rhino.

#### 5.2.6. Métodos y Propiedades del Modelo
* **`get_type_prefix(self)`**: Devuelve un prefijo de cadena (ej. "User", "Deac", "AV") basado en `self.type_of_process`, utilizado para generar el `unique_code`. [cite: 47]
* **`save(self, *args, **kwargs)`**:
    * Sobrescrito para generar automáticamente el `unique_code` si la instancia es nueva y no tiene uno. [cite: 48]
    * El formato del código es `TIPO-AÑOQTRNUMERO` (ej. `User-25Q2001`), donde el número es secuencial para ese tipo y ese trimestre/año.
    * Establece `status` a 'pending' por defecto si es una nueva instancia y no tiene estado.
    * *Nota: La lógica para `effective_start_time_for_tat` se maneja principalmente en las vistas o tareas programadas al cambiar el estado a 'pending' o al resolver un bloqueo, no directamente aquí de forma generalizada.* [cite: 48]
* **`local_timestamp` (propiedad)**: Devuelve el `timestamp` de la solicitud convertido a la zona horaria preferida del `requested_by`. [cite: 49] Si la zona horaria del usuario es desconocida o inválida, recurre a UTC.
* **`calculated_turn_around_time` (propiedad)**: Calcula y devuelve la diferencia (como `timedelta`) entre `completed_at` y `effective_start_time_for_tat`, solo si la solicitud está 'completed' y ambos timestamps existen. [cite: 49] Devuelve `None` en otros casos.

#### 5.2.7. Clase Meta (`UserRecordsRequest`) [cite: 50]
* `verbose_name = 'Request'`
* `verbose_name_plural = 'Requests'`
* `ordering = ['-timestamp']`: Ordena las solicitudes por defecto por fecha de creación descendente (las más nuevas primero).

### 5.3. `AddressValidationFile(models.Model)` [cite: 51]
Modelo diseñado para permitir la subida de múltiples archivos asociados a una única solicitud de "Address Validation".
* **`request = models.ForeignKey(UserRecordsRequest, related_name='address_validation_files', on_delete=models.CASCADE)`**: Enlace a la solicitud `UserRecordsRequest` principal. [cite: 52] El `related_name` permite acceder a estos archivos desde una instancia de `UserRecordsRequest` (ej. `user_request_instance.address_validation_files.all()`).
* **`uploaded_file = models.FileField(upload_to='address_validation_uploads/', validators=[validate_file_size])`**: El archivo subido. [cite: 52] Se almacena en `media/address_validation_uploads/`. Utiliza el validador `validate_file_size`.
* **`uploaded_at = models.DateTimeField(auto_now_add=True)`**: Timestamp de cuándo se subió el archivo. [cite: 52]
* **Meta:**
    * `ordering = ['uploaded_at']`
    * `verbose_name = "Address Validation File"`
    * `verbose_name_plural = "Address Validation Files"`

### 5.4. Modelos de Historial (`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`) [cite: 53]
Estos modelos registran eventos clave en el ciclo de vida de una solicitud, proporcionando un rastro de auditoría y contexto. [cite: 54]
* **`BlockedMessage`**:
    * `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='blocked_messages'`).
    * `blocked_by`: `ForeignKey` a `CustomUser` (quién bloqueó).
    * `blocked_at`: `DateTimeField` (cuándo se bloqueó, `default=now`).
    * `reason`: `TextField` (por qué se bloqueó).
    * Meta: `ordering = ['-blocked_at']`.
* **`ResolvedMessage`**: [cite: 55]
    * `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='resolved_messages'`).
    * `resolved_by`: `ForeignKey` a `CustomUser` (quién resolvió).
    * `resolved_at`: `DateTimeField` (cuándo se resolvió, `default=now`).
    * `message`: `TextField` (mensaje de resolución).
    * `resolved_file`: `FileField` (archivo adjunto a la resolución, opcional).
    * `resolved_link`: `URLField` (enlace adjunto a la resolución, opcional).
    * Meta: `ordering = ['-resolved_at']`.
* **`RejectedMessage`**: [cite: 55]
    * `request`: `ForeignKey` a `UserRecordsRequest` (`related_name='rejected_messages'`).
    * `rejected_by`: `ForeignKey` a `CustomUser` (quién rechazó).
    * `rejected_at`: `DateTimeField` (cuándo se rechazó, `default=now`).
    * `reason`: `TextField` (por qué se rechazó).
    * `is_resolved_qa`: `BooleanField` (indica si el rechazo de QA fue resuelto por QA, aunque esta lógica parece más relacionada con el flujo que con el mensaje en sí).
    * Meta: `ordering = ['-rejected_at']`.

### 5.5. `OperationPrice(models.Model)` [cite: 56]
Un modelo Singleton (se espera una única instancia con `pk=1`) para almacenar y gestionar los precios que se cobran al cliente y los costos internos asociados con las diferentes métricas de las operaciones y el control de calidad (QA).
* **Campos de Precios al Cliente**: [cite: 57]
    * `user_update_price`, `property_update_price`, `bulk_update_price`, `manual_update_price`, `csv_update_price`, `processing_report_price` (todos `DecimalField(max_digits=10, decimal_places=4, default=0.0000)`).
* **Campos de Costos de Operación**: [cite: 57]
    * `user_update_operate_cost`, `property_update_operate_cost`, `bulk_update_operate_cost`, `manual_update_operate_cost`, `csv_update_operate_cost`, `processing_report_operate_cost` (todos `DecimalField`).
* **Campos de Costos de QA**: [cite: 57]
    * `user_update_qa_cost`, `property_update_qa_cost`, `bulk_update_qa_cost`, `manual_update_qa_cost`, `csv_update_qa_cost`, `processing_report_qa_cost` (todos `DecimalField`).
* **Meta:** `verbose_name = "Operation Price and Cost"`, `verbose_name_plural = "Operation Prices and Costs"`. [cite: 58]

### 5.6. `SalesforceAttachmentLog(models.Model)` [cite: 59]
Modelo para rastrear metadatos de archivos adjuntos recuperados de Salesforce y asociados con una `UserRecordsRequest` creada a través de la sincronización.
* **`request = models.ForeignKey(UserRecordsRequest, related_name='salesforce_attachments', on_delete=models.CASCADE, verbose_name="Associated Request")`**: Enlace a la solicitud principal.
* **`file_name = models.CharField(max_length=255, verbose_name="File Name")`**: Nombre del archivo tal como aparece en Salesforce.
* **`file_extension = models.CharField(max_length=50, blank=True, null=True, verbose_name="File Extension")`**: Extensión del archivo.
* **`salesforce_file_link = models.URLField(max_length=1024, verbose_name="Salesforce File Link")`**: Enlace directo para ver/descargar el archivo desde Salesforce.
* **Meta:** `verbose_name = "Salesforce Attachment Log"`, `verbose_name_plural = "Salesforce Attachment Logs"`, `ordering = ['-request__timestamp', 'file_name']`.

---
## 6. Archivo de Opciones (`tasks/choices.py`)

Este archivo centraliza todas las tuplas de `choices` utilizadas en los campos `CharField` de los modelos, mejorando la mantenibilidad y consistencia. Define constantes para tipos de proceso, equipos, prioridades, estados, tipos de solicitud de grupo de usuarios, niveles de acceso, tipos de desactivación/toggle, aprobación de liderazgo, tipos de transferencia de unidades, tipos de propietario, estados para XML, tipos de registros de propiedad, tipos de propiedad, tipos de cobertura, multiplicadores de cobertura y tipos de integración.

Algunos ejemplos clave incluyen:
* `TYPE_CHOICES`: Para `UserRecordsRequest.type_of_process`.
* `TEAM_CHOICES`: Para `UserRecordsRequest.team`.
* `PRIORITY_CHOICES`: Para `UserRecordsRequest.priority`.
* `STATUS_CHOICES`: Para `UserRecordsRequest.status`.
* Constantes individuales como `TEAM_REVENUE`, `PRIORITY_NORMAL`.

---
## 7. Validadores Personalizados (`tasks/validators.py`) [cite: 329]

Contiene funciones de validación personalizadas.
* **`validate_file_size(value)`**: [cite: 330]
    * Valida que el tamaño de un archivo subido (`value`, que es un objeto `FieldFile` o `UploadedFile`) no exceda un límite predefinido (actualmente 10MB). [cite: 330, 331]
    * Lanza una `ValidationError` con un mensaje detallado si el archivo es demasiado grande. [cite: 331]
    * Se aplica a `UserRecordsRequest.user_file`, `UserRecordsRequest.xml_rvic_zip_file`, `UserRecordsRequest.xml_ssic_zip_file`, `UserRecordsRequest.operator_*_file_slot*` y `AddressValidationFile.uploaded_file`. [cite: 332]

---
## 8. Formularios Detallados (`tasks/forms.py`) [cite: 60]

Define los formularios Django para la entrada y validación de datos, utilizando `forms.Form` y `forms.ModelForm`. [cite: 61]

### 8.1. Formularios de Usuario [cite: 62]
* **`CustomUserChangeForm(UserChangeForm)`**: Para editar datos básicos del usuario (`username`, `email`, `first_name`, `last_name`, `timezone`). [cite: 63] Omite `password`. [cite: 64] Usa widgets Bootstrap. [cite: 65] Incluye `clean_email` para validar unicidad. [cite: 66]
* **`CustomPasswordChangeForm(PasswordChangeForm)`**: Para cambiar la contraseña (`old_password`, `new_password1`, `new_password2`). [cite: 67] Usa widgets Bootstrap y `validate_password`. [cite: 68]

### 8.2. `UserGroupForm(forms.Form)` [cite: 69]
Formulario no vinculado a modelo para un grupo de usuarios en "User Records".
* **Campos**: `type_of_request` (`REQUEST_TYPE_CHOICES`), `user_email_addresses` (múltiples emails), `access_level` (`ACCESS_LEVEL_CHOICES`, condicionalmente requerido), `properties` (múltiples propiedades). [cite: 70]
* **`__init__`**: Hace `access_level` no requerido si `type_of_request` es 'remove'. [cite: 71]
* **`clean_user_email_addresses` / `clean_properties`**: Procesan entrada de texto (separada por comas/saltos de línea) en listas. [cite: 72]
* Usado con `formset_factory` en la vista `user_records_request` para múltiples grupos. [cite: 73]

### 8.3. `UserRecordsRequestForm(forms.Form)` [cite: 74]
Formulario no basado en modelo para la creación de "User Records".
* **Campos**: `partner_name`, `special_instructions`, `user_file` (opcional), `user_link` (opcional), `priority` (`RadioSelect`). [cite: 75]
* **Campos de Programación**: `schedule_request` (`BooleanField`), `scheduled_date` (`DateField`). [cite: 77, 78]
* **`clean()`**: Valida que `scheduled_date` se provea si `schedule_request` está marcado[cite: 79], y que `scheduled_date` sea futura (mínimo mañana) según la zona horaria del usuario. [cite: 80]
* *Nota: El campo `team_selection` ha sido eliminado; la lógica de equipo se maneja en la vista.* [cite: 76]

### 8.4. Formularios de Acción Simples (`BlockForm`, `ResolveForm`, `RejectForm`) [cite: 86]
Heredan de `forms.Form`.
* **`BlockForm`**: Campo `reason` (`Textarea`) para bloquear una solicitud. [cite: 86]
* **`ResolveForm`**: Campos `message` (`Textarea`), `resolved_file` (`FileField` opcional), `resolved_link` (`URLField` opcional). [cite: 87]
* **`RejectForm`**: Campo `reason` (`Textarea`) para rechazar una solicitud.

### 8.5. `OperateForm(forms.ModelForm)` [cite: 82]
`ModelForm` para `UserRecordsRequest`, usado en `send_to_qa_request` y `complete_request` para que los agentes registren detalles de la operación. [cite: 82]
* **Campos Incluidos**: `num_updated_users`, `num_updated_properties`, `bulk_updates`, `manual_updated_properties`, `manual_updated_units`, `update_by_csv_rows`, `processing_reports_rows`, `operator_spreadsheet_link`, `operating_notes`. También incluye campos específicos para 'Address Validation' (`assets_uploaded`, `av_number_of_units`, etc.) y 'Stripe Disputes' (`stripe_premium_disputes`, `stripe_ri_disputes`). [cite: 83]
* **Widgets**: Personalizados con clases Bootstrap y `min="0"` para campos numéricos.
* **Labels**: Mejorados para mayor claridad.
* **`__init__(self, *args, **kwargs)`**:
    * **Lógica Condicional de Campos**: Dinámicamente elimina campos del formulario o ajusta su obligatoriedad (`required`) basado en el `type_of_process` de la instancia de la solicitud que se está operando.
        * **Address Validation**: Oculta campos no relevantes (ej. `processing_reports_rows`), hace obligatorios `av_number_of_units`, `av_number_of_invalid_units`, `link_to_assets`, `operating_notes`. Pre-llena `av_number_of_units` con `instance.salesforce_number_of_units` si está disponible y no hay datos POST.
        * **Stripe Disputes**: Oculta campos no relevantes, hace obligatorios `stripe_premium_disputes`, `stripe_ri_disputes`, y `operating_notes`.
        * **Generating XML**: Este formulario base no se usa; se usa `GeneratingXmlOperateForm`.
        * **Otros Tipos**: Para User Records, Deactivation/Toggle, Unit Transfer, Property Records, los campos numéricos de operación son opcionales. `operating_notes` y `operator_spreadsheet_link` son opcionales por defecto.
    * Asegura que todos los campos `IntegerField` o `DecimalField` tengan un `MinValueValidator(0)`.
    * Por defecto, la mayoría de los campos numéricos y URL se marcan como `required=False`, a menos que la lógica específica del tipo de proceso los requiera.

### 8.6. `OperationPriceForm(forms.ModelForm)` [cite: 88]
`ModelForm` para el modelo Singleton `OperationPrice`.
* `fields = '__all__'` para incluir todos los campos de precios y costos. [cite: 88]
* Widgets `NumberInput` con `step='0.0001'` para campos decimales.
* Permite la edición de estos valores. [cite: 89]

### 8.7. Formularios Específicos por Tipo de Proceso [cite: 90]
Heredan de `forms.ModelForm` y están vinculados a `UserRecordsRequest`. Incluyen campos genéricos (`special_instructions`, `priority`, `schedule_request`, `scheduled_date`) y campos específicos del tipo de proceso. [cite: 91] La selección de equipo (`team_selection`) fue eliminada de estos formularios; la lógica se maneja en la vista.

* **8.7.1. `DeactivationToggleRequestForm`**: [cite: 92]
    * Campos: `deactivation_toggle_type`, `partner_name`, `properties`, `deactivation_toggle_active_policies`, etc.
    * `clean()`: Valida condicionalmente `properties` (req. para 'property\_deactivation') y `deactivation_toggle_properties_with_policies` (req. si `active_policies` está marcado). [cite: 93] Limpia campos no aplicables a `None` según `deactivation_toggle_type`.
    * Incluye validación para `scheduled_date`. [cite: 94]
* **8.7.2. `UnitTransferRequestForm`**: [cite: 95]
    * Campos: `unit_transfer_type`, `partner_name` (origen), `unit_transfer_new_partner_prospect_name` (destino), `properties` (cond. req.), etc.
    * `clean()`: Valida campos de "Partner to Prospect" y `properties` (req. si no hay `user_file`/`user_link`). [cite: 96]
    * Incluye validación para `scheduled_date`. [cite: 97]
* **8.7.3. `GeneratingXmlRequestForm`**: [cite: 106]
    * Campos: `xml_state`, `xml_carrier_rvic`, `xml_carrier_ssic`, `user_file` (obligatorio), `xml_rvic_zip_file` (cond.), `xml_ssic_zip_file` (cond.).
    * `priority` se asigna 'normal' por defecto en la vista (eliminado de `Meta.fields`). [cite: 107, 108]
    * No incluye campos de programación. [cite: 108]
    * `clean()`: Valida selección de carrier y ZIPs condicionales. [cite: 109]
* **8.7.4. `AddressValidationRequestForm`**: [cite: 98]
    * Campos: `partner_name`, `address_validation_policyholders`, `address_validation_opportunity_id`, `user_link`, `address_validation_user_email_addresses`.
    * `clean()`: Valida `address_validation_opportunity_id` (req. si no hay archivos múltiples subidos en la vista ni `user_link`). [cite: 100]
    * Incluye validación para `scheduled_date`. [cite: 101]
* **8.7.5. `StripeDisputesRequestForm`**: [cite: 110]
    * Campos: `stripe_premium_disputes`, `stripe_ri_disputes`, `user_file` (obligatorio).
    * `priority` se asigna 'normal' por defecto en la vista (eliminado de `Meta.fields`). [cite: 111]
    * No incluye campos de programación. [cite: 112]
    * `clean()`: Valida que al menos un tipo de disputa sea > 0.
* **8.7.6. `PropertyRecordsRequestForm`**: [cite: 102]
    * Campos: `property_records_type`, `partner_name`, `properties` (cond. req.), y varios campos `property_records_*`.
    * `clean()`: Lógica de validación compleja para campos `property_records_*` según `property_records_type` y si no hay `user_file`/`user_link`. [cite: 104] Limpia campos no aplicables a `None`.
    * Incluye validación para `scheduled_date`. [cite: 105]
* **8.7.7. `GeneratingXmlOperateForm`**:
    * `ModelForm` para `UserRecordsRequest`, específico para operar solicitudes "Generating XML".
    * **Campos Definidos**: `operating_notes` (`CharField`, opcional) y `qa_needs_file_correction` (`BooleanField`, opcional, para el flujo de QA).
    * **Campos Dinámicos de Archivo**: En `__init__`, se añaden dinámicamente `FileField`s al formulario basados en el `xml_state` de la instancia y si `xml_carrier_rvic` y/o `xml_carrier_ssic` estaban seleccionados en la solicitud original. Estos campos se mapean a los campos `operator_rvic_file_slot1`, `operator_rvic_file_slot2`, `operator_ssic_file_slot1`, `operator_ssic_file_slot2` del modelo. Por ejemplo, si `xml_state` es 'UT' y `xml_carrier_rvic` es `True`, se añadirán campos para "Operator: UT RVIC CSV File" y "Operator: UT RVIC ZIP File".
    * **`save(self, commit=True)`**: Sobrescrito para asegurar que `operating_notes` se guarde y para iterar sobre los campos de archivo dinámicos definidos en `_dynamic_file_fields_mapping`. Si se proporciona un archivo en el formulario para un campo dinámico, se actualiza el campo correspondiente en el modelo. Si el widget `ClearableFileInput` indica que el archivo debe borrarse (el valor es `False`), el campo del modelo se establece en `None`.

---
## 9. Vistas Detalladas (`tasks/views.py`) [cite: 113]

Contienen la lógica de negocio, manejan solicitudes HTTP, interactúan con modelos y formularios, y renderizan plantillas.

### 9.1. Funciones Auxiliares de Permisos [cite: 194]
Estas funciones ayudan a controlar el acceso a diferentes partes de la aplicación.
* `is_admin(user)`: Retorna `True` si el usuario es autenticado y `is_superuser` o `is_staff`. [cite: 194]
* `is_leadership(user)`: Retorna `True` si el usuario autenticado pertenece al grupo "Leaderships". [cite: 194] Maneja `Group.DoesNotExist`.
* `is_agent(user)`: Retorna `True` si el usuario autenticado pertenece al grupo "Agents". [cite: 194]
* `user_in_group(user, group_name)`: Función genérica que verifica si un usuario autenticado pertenece a un grupo específico por su nombre. [cite: 196] Maneja `Group.DoesNotExist`.
* `can_view_request(user, user_request)`: Determina si el `user` tiene permiso para ver la `user_request`. [cite: 197] Permite al creador (`requested_by`), agentes, miembros de "Leaderships", y administradores.
* `can_cancel_request(user, user_request)`: Determina si el `user` puede cancelar la `user_request`. [cite: 198] Permite a agentes, administradores, o miembros de "Leaderships" si el estado de la solicitud está en una lista predefinida de estados cancelables (ej., 'pending', 'scheduled', 'blocked', 'in_progress', 'qa_pending', 'pending_approval').
* `user_belongs_to_revenue_or_support(user)`: Usada con `@user_passes_test`. Verifica si el usuario pertenece al grupo 'Revenue' o 'Support'. [cite: 199] Lanza `PermissionDenied` si no pertenece, lo que previene el acceso a la vista decorada (típicamente vistas de creación de solicitudes). [cite: 200]
* `user_belongs_to_compliance(user)`: Similar al anterior, para el grupo 'Compliance'. [cite: 199, 200]
* `user_belongs_to_accounting(user)`: Similar, para el grupo 'Accounting'. [cite: 199, 200]

### 9.2. Vistas Generales y de Autenticación
* **`home(request)`**:
    * Vista para la página de inicio (`/`). [cite: 114]
    * Requiere que el usuario esté autenticado (`@login_required`). [cite: 115]
    * Renderiza la plantilla `tasks/home.html`. [cite: 115]
* **`profile(request)`**:
    * Permite a los usuarios autenticados ver y actualizar su información de perfil y cambiar su contraseña. [cite: 116]
    * Utiliza `CustomUserChangeForm` para los datos del perfil y `CustomPasswordChangeForm` para la contraseña. [cite: 117]
    * Maneja solicitudes GET (mostrar formularios) y POST (procesar cambios). [cite: 117]
    * Si se intenta cambiar la contraseña (si `new_password1` o `new_password2` tienen valor), valida el formulario de contraseña.
    * Guarda los cambios y muestra mensajes de éxito o error usando `django.contrib.messages`. [cite: 118]
    * Redirige a la misma página de perfil tras una actualización exitosa. [cite: 118]
    * Renderiza `tasks/profile.html`. [cite: 119]
* **`choose_request_type(request)`**:
    * Vista para que los usuarios seleccionen el tipo de solicitud a crear. [cite: 119]
    * Requiere autenticación.
    * Renderiza `tasks/choose_request_type.html`, que contiene enlaces a los formularios de creación. [cite: 120]

### 9.3. Vistas de Creación de Solicitudes [cite: 121]
Estas vistas manejan la creación de nuevas instancias `UserRecordsRequest`. Todas requieren `@login_required`. La asignación de `requested_by` es al `request.user`.
* **Lógica Común de Asignación de Equipo y Programación:**
    * Para tipos de solicitud que pueden ser creados por usuarios en 'Revenue' o 'Support' (User Records, Deactivation/Toggle, Unit Transfer, Address Validation, Property Records):
        * Se verifica si el usuario pertenece a `TEAM_REVENUE` y `TEAM_SUPPORT` simultáneamente. Si es así, se muestra un mensaje de error y se redirige, ya que el usuario debe pertenecer solo a uno para la creación de estas solicitudes.
        * El campo `team` de la solicitud se asigna basado en el único grupo operativo al que pertenece el usuario.
    * Para la programación:
        * Se obtienen `schedule_request` y `scheduled_date` del formulario.
        * Si `schedule_request` es `True` y `scheduled_date` es válida (futura):
            * `req_instance.status = 'scheduled'`
            * `req_instance.scheduled_date = scheduled_date_value`
            * `req_instance.effective_start_time_for_tat = None`
        * Si no se programa:
            * `req_instance.status = 'pending'` (o 'pending_approval' para ciertos tipos de Deactivation/Toggle)
            * `req_instance.scheduled_date = None`
            * `req_instance.effective_start_time_for_tat = creation_timestamp` (a menos que sea 'pending_approval')
    * Se muestra un mensaje de éxito indicando el código de la solicitud, el equipo asignado y, si aplica, la fecha de programación.
* **`user_records_request(request)`**: [cite: 122]
    * Usa `UserRecordsRequestForm` y `formset_factory` con `UserGroupForm`. [cite: 123]
    * El `formset` es requerido si no se proporciona `user_file` ni `user_link`. [cite: 124]
    * Los datos de `group_data` del formset se guardan en `user_groups_data` (JSON).
    * `type_of_process='user_records'`. [cite: 125] Asigna `team` y `priority`. [cite: 125, 126]
    * Lógica de programación como se describe arriba. [cite: 127, 128]
    * Renderiza `tasks/user_records.html`. [cite: 128]
* **`deactivation_toggle_request(request)`**: [cite: 129]
    * Decorada con `@user_passes_test(user_belongs_to_revenue_or_support)`.
    * Usa `DeactivationToggleRequestForm`. `type_of_process='deactivation_toggle'`. [cite: 129]
    * Asigna `team` y `priority`. [cite: 130]
    * **Lógica de Estado Específica**:
        * Determina si `deactivation_toggle_type` requiere aprobación (`types_requiring_approval`).
        * Si se programa y requiere aprobación (y el usuario no es líder): `status='pending_approval'`, `effective_start_time_for_tat = None`. [cite: 132]
        * Si se programa y no requiere aprobación (o el usuario es líder): `status='scheduled'`, `effective_start_time_for_tat = None`. [cite: 132]
        * Si no se programa y requiere aprobación (y el usuario no es líder): `status='pending_approval'`, `effective_start_time_for_tat = None`. [cite: 133]
        * Si no se programa y no requiere aprobación (o el usuario es líder): `status='pending'`, `effective_start_time_for_tat = creation_timestamp`. [cite: 134]
    * Renderiza `tasks/deactivation_toggle_request.html`.
* **`unit_transfer_request(request)`**: [cite: 135]
    * Decorada con `@user_passes_test(user_belongs_to_revenue_or_support)`.
    * Usa `UnitTransferRequestForm`. `type_of_process='unit_transfer'`.
    * Asigna `team` y `priority`.
    * Lógica de programación estándar. [cite: 136]
    * Renderiza `tasks/unit_transfer_request.html`.
* **`address_validation_request(request)`**: [cite: 137]
    * Decorada con `@user_passes_test(user_belongs_to_revenue_or_support)`.
    * Usa `AddressValidationRequestForm`. `type_of_process='address_validation'`. [cite: 137]
    * Asigna `team` y `priority`. [cite: 138]
    * Lógica de programación estándar. [cite: 138]
    * Maneja la subida de múltiples archivos (`request.FILES.getlist('request_files')`) y crea instancias `AddressValidationFile` asociadas dentro de una `transaction.atomic()`. [cite: 139, 140]
    * Valida que se proporcione `address_validation_opportunity_id` si no se suben archivos ni se proporciona `user_link` (esto se hace en `form.clean()`). [cite: 141]
    * Renderiza `tasks/address_validation_request.html`.
* **`property_records_request(request)`**: [cite: 142]
    * Decorada con `@user_passes_test(user_belongs_to_revenue_or_support)`.
    * Usa `PropertyRecordsRequestForm`. `type_of_process='property_records'`.
    * Asigna `team` y `priority`. [cite: 143]
    * Lógica de programación estándar. [cite: 143]
    * Llama a `form.save_m2m()` después de `prop_request.save()` si el formulario tiene campos ManyToMany (actualmente no los tiene explícitamente, pero es una buena práctica si se añaden).
    * Renderiza `tasks/property_records_request.html`.
* **`generating_xml_request(request)`**: [cite: 144]
    * Decorada con `@user_passes_test(user_belongs_to_compliance)`.
    * Usa `GeneratingXmlRequestForm`. `type_of_process='generating_xml'`.
    * Fija `status='pending'`, `priority=PRIORITY_NORMAL`, `team=TEAM_COMPLIANCE`. [cite: 144]
    * No se programa: `scheduled_date = None`, `effective_start_time_for_tat = creation_timestamp`. [cite: 145]
    * Renderiza `tasks/generating_xml_request.html`.
* **`stripe_disputes_request(request)`**: [cite: 146]
    * Decorada con `@user_passes_test(user_belongs_to_accounting)`.
    * Usa `StripeDisputesRequestForm`. `type_of_process='stripe_disputes'`.
    * Fija `status='pending'`, `priority=PRIORITY_NORMAL`, `team=TEAM_ACCOUNTING`. [cite: 147]
    * No se programa: `scheduled_date = None`, `effective_start_time_for_tat = creation_timestamp`. [cite: 148]
    * Renderiza `tasks/stripe_disputes_request.html`.

### 9.4. Vistas de Dashboard y Detalles de Solicitud
* **`portal_operations_dashboard(request)`**: [cite: 149]
    * `@login_required`.
    * Recupera `UserRecordsRequest` con `select_related('requested_by', 'operator', 'qa_agent')`. [cite: 150]
    * Filtra por `type` (type_of_process), `status` (incluye 'Scheduled'), `team`, `start_date`, `end_date` (convirtiendo fechas a UTC y manejando la zona horaria del usuario para la entrada). [cite: 149]
    * Ordena por `-timestamp`. Paginación con `Paginator` (25 por página). [cite: 151]
    * Pasa `TYPE_CHOICES`, `STATUS_CHOICES`, `TEAM_CHOICES` y los filtros actuales al contexto. [cite: 152]
    * Renderiza `tasks/portal_operations_dashboard.html`. [cite: 152]
* **`request_detail(request, pk)`**: [cite: 153]
    * `@login_required`. Obtiene `UserRecordsRequest` por `pk` o 404.
    * Verifica permisos con `can_view_request(user, user_request)`. [cite: 154]
    * Recupera historial: `blocked_messages`, `resolved_messages`, `rejected_messages` (ordenados). [cite: 155]
    * **Procesamiento Específico del Tipo:**
        * **User Records:** Procesa `user_groups_data` para visualización (convierte `access_level` a display value) y cuenta `total_user_records_emails`. [cite: 156] Si no hay `user_file` pero sí emails en grupos, `prefill_user_count` se establece con este total.
        * **Unit Transfer:** Cuenta emails de `unit_transfer_user_email_addresses` y establece `prefill_user_count`. [cite: 157]
        * **Address Validation:** Recupera archivos asociados (`user_request.address_validation_files.all()`). [cite: 157]
    * **Variables de Contexto para Botones:** `is_agent_user`, `is_leadership_user`, `can_reject_request`, `can_request_update_action`, `can_clear_update_flag_action`, `update_needed` (valor de `user_request.update_needed_flag`), `can_cancel_request`, `can_uncancel_request`. [cite: 158]
        * `can_reject_request` permite rechazar si el estado es 'qa_in_progress' o 'completed' y el usuario es admin, líder, el QA asignado, o el solicitante.
        * `can_request_update_action` permite si el usuario es del equipo/admin/líder y el flag está apagado y estado es activo.
        * `can_clear_update_flag_action` permite si el usuario es agente y el flag está encendido y estado es activo.
        * `can_cancel_request` / `can_uncancel_request` se basan en si el usuario es del equipo/admin/líder y el estado de la solicitud.
    * **Mapeo de Plantillas:** Un diccionario `template_map` selecciona la plantilla de detalle correcta (`user_records_detail.html`, `deactivation_toggle_detail.html`, etc.) según `user_request.type_of_process`. [cite: 159]
    * **Formulario para Modal (Generating XML):** Si `type_of_process == 'generating_xml'`, se instancia `GeneratingXmlOperateForm(instance=user_request)` y se pasa al contexto como `form_for_modal`. Esto permite que los modales "Send to QA" y "Complete" usen este formulario específico.

### 9.5. Vistas de Acciones de Flujo de Trabajo [cite: 160, 161]
Todas requieren `@login_required` y validan permisos/estado. Redirigen a `tasks:request_detail` después de la acción.

* **`operate_request(request, pk)`**: [cite: 162]
    * Permiso: `is_agent(request.user)`.
    * No opera si está 'scheduled'.
    * Si estado es 'pending' o 'completed' (para reabrir después de un rechazo, por ejemplo):
        * Si estaba 'pending' y fue descancelada (`uncanceled_by` no es `None`), limpia `uncanceled_by` y `uncanceled_at`.
        * `status = 'in_progress'`, `operator = request.user`, `operated_at = timezone.now()`. [cite: 163]
        * Limpia `qa_agent`, `qa_pending_at`, `qa_in_progress_at`, `completed_at`.
* **`block_request(request, pk)`**: [cite: 165]
    * Permiso: `is_agent(request.user)`.
    * Solo si estado es 'pending' o 'in_progress'.
    * Usa `BlockForm`. Si es válido:
        * Crea `BlockedMessage` (con `reason`, `blocked_by`).
        * `user_request.status = 'blocked'`. [cite: 166]
        * **Integración Salesforce (si 'address_validation' y `salesforce_standard_opp_id` existe):**
            * Intenta conectar a Salesforce.
            * Actualiza `Opportunity` en SF: `Invisible_Status__c = 'Escalated'`, `Invisible_Comments__c` con detalles del bloqueo. [cite: 167]
            * Maneja `SalesforceError` y otras excepciones, mostrando mensajes de advertencia si SF falla pero Django tuvo éxito.
    * Renderiza `tasks/block_form.html` si es GET o el formulario es inválido.
* **`resolve_request(request, pk)`**:
    * Permiso: `is_agent` O el `requested_by` es de `TEAM_REVENUE` o `TEAM_SUPPORT` O `is_admin` O `is_leadership`.
    * Solo si `status == 'blocked'`.
    * Usa `ResolveForm`. Si es válido:
        * Crea `ResolvedMessage` (con `message`, `resolved_file`, `resolved_link`, `resolved_by`). [cite: 168]
        * `user_request.status = 'pending'`. [cite: 169]
        * `user_request.effective_start_time_for_tat = timezone.now()` (reinicia TAT). [cite: 169]
        * **Integración Salesforce (si 'address_validation' y `salesforce_standard_opp_id` existe):**
            * Intenta conectar a Salesforce.
            * Actualiza `Opportunity` en SF: `Invisible_Status__c = 'In Progress'`, `Invisible_Comments__c` con detalles de la resolución.
            * Maneja errores de Salesforce.
    * Renderiza `tasks/resolve_form.html` si es GET o el formulario es inválido.
* **`send_to_qa_request(request, pk)`**: [cite: 170]
    * Permiso: `is_agent(request.user)` Y `user_request.operator == request.user`.
    * Solo si `status == 'in_progress'`.
    * Determina `CurrentFormClass` (`GeneratingXmlOperateForm` si es 'generating_xml', sino `OperateForm`).
    * Si es `GeneratingXmlOperateForm` y `qa_needs_file_correction` existe en el form, se oculta y no se requiere (el operador no decide esto).
    * Si el formulario es válido:
        * Guarda el formulario (que puede incluir archivos si es `GeneratingXmlOperateForm`).
        * `saved_instance.status = 'qa_pending'`, `saved_instance.qa_pending_at = timezone.now()`.
        * `saved_instance.is_rejected_previously = False`. [cite: 172]
        * Guarda la instancia solo con los campos de estado y fecha actualizados.
    * Redirige a detalle; GET no debería llegar aquí desde el modal.
* **`qa_request(request, pk)`**: [cite: 173]
    * Permiso: `is_agent(request.user)`.
    * Solo si `status == 'qa_pending'`.
    * `user_request.status = 'qa_in_progress'`, `user_request.qa_agent = request.user`, `user_request.qa_in_progress_at = timezone.now()`. [cite: 174]
* **`complete_request(request, pk)`**: [cite: 175]
    * Permiso: `is_agent(request.user)` Y `status == 'qa_in_progress'` Y `user_request.qa_agent == request.user`.
    * Determina `CurrentFormClass` (`GeneratingXmlOperateForm` o `OperateForm`).
    * Si el formulario es válido:
        * Guarda el formulario. `updated_instance.status = 'completed'`, `updated_instance.completed_at = timezone.now()`. [cite: 176]
        * Define `fields_to_update_django` para el `save()` (incluye campos de `form.Meta.fields` si es `GeneratingXmlOperateForm` o campos del `cleaned_data` para `OperateForm`).
        * **Integración Salesforce (si 'address_validation' y `salesforce_standard_opp_id` existe):**
            * Actualiza `Opportunity` en SF con campos de `OperateForm` (ej. `Assets_Uploaded__c`, `Number_of_Units__c`, `Link_to_Assets__c`, etc.) y `Invisible_Status__c = 'Completed'`.
            * Maneja `Assets_Uploaded_Date__c`.
            * Maneja errores de Salesforce.
    * Redirige a detalle.
* **`cancel_request(request, pk)`**: [cite: 177]
    * Permiso: `can_cancel_request(user, user_request)`.
    * `user_request.cancelled = True`, `user_request.cancelled_by = request.user`, `user_request.status = 'cancelled'`, `user_request.cancelled_at = timezone.now()`.
    * Si `scheduled_date` existía, se limpia. [cite: 178]
* **`reject_request(request, pk)`**: [cite: 179]
    * Permiso: `can_reject_request` (QA asignado, o solicitante/admin/líder, si estado es 'qa_in_progress' o 'completed').
    * Usa `RejectForm`. Si válido:
        * Crea `RejectedMessage`. [cite: 180]
        * `user_request.status = 'in_progress'`. [cite: 181]
        * Limpia `qa_agent`, `qa_pending_at`, `qa_in_progress_at`, `completed_at`. [cite: 182]
        * `user_request.is_rejected_previously = True`. [cite: 182]
    * Renderiza `tasks/reject_form.html` si es GET o el formulario es inválido.
* **`approve_deactivation_toggle(request, pk)`**: [cite: 183]
    * Permiso: `@user_passes_test(is_leadership)`.
    * Solo si `type_of_process == 'deactivation_toggle'` y `status == 'pending_approval'`.
    * Si `user_request.scheduled_date` existe y es futura: `status = 'scheduled'`, `effective_start_time_for_tat` no cambia (sigue `None`). [cite: 184]
    * Si `scheduled_date` es hoy/pasada o no existe: `status = 'pending'`, `effective_start_time_for_tat = approval_time`. [cite: 186]
* **`set_update_needed_flag(request, pk)`**: [cite: 187]
    * Permiso: (Miembro del equipo de la solicitud O Admin O Leadership) Y (estado activo: no 'completed', 'cancelled', 'scheduled') Y (`update_needed_flag` está apagada).
    * `user_request.update_needed_flag = True`, `user_request.update_requested_by = request.user`, `user_request.update_requested_at = timezone.now()`.
* **`clear_update_needed_flag(request, pk)`**: [cite: 188]
    * Permiso: `is_agent(user)` Y (`update_needed_flag` está encendida) Y (estado no es 'scheduled').
    * `user_request.update_needed_flag = False`.
* **`uncancel_request(request, pk)`**: [cite: 189]
    * Permiso: (Miembro del equipo de la solicitud O Admin O Leadership) Y (`status == 'cancelled'`).
    * `user_request.cancelled = False`, `cancelled_by = None`, `cancelled_at = None`, `uncanceled_by = request.user`, `uncanceled_at = timezone.now()`, `status = 'pending'`, `cancel_reason = None`.
    * *Nota: `effective_start_time_for_tat` no se actualiza explícitamente aquí; se espera que la transición a 'pending' (si es un nuevo inicio) o la lógica de `operate_request` lo manejen.* [cite: 190]

### 9.6. Vista de Administración de Precios
* **`manage_prices(request)`**: [cite: 191]
    * Permiso: `@user_passes_test(is_admin)`.
    * Usa `OperationPriceForm` para gestionar la instancia Singleton de `OperationPrice`. [cite: 192]
    * `OperationPrice.objects.get_or_create(pk=1)` para asegurar una única instancia. [cite: 193]
    * Renderiza `tasks/manage_prices.html`.

---
## 10. Plantillas Detalladas (`tasks/templates/tasks/`) [cite: 201]
Definen la estructura HTML y presentación, usando plantillas Django y Bootstrap 5. [cite: 202]

### 10.1. Plantilla Base (`base.html`) [cite: 203]
Estructura HTML común.
* **`<head>`**: [cite: 204]
    * Charset UTF-8, viewport responsivo. [cite: 204]
    * `{% block title %}` (default "Requests Platform"). [cite: 205]
    * Bootstrap 5 CSS (CDN). [cite: 206]
    * `{% block extra_css %}`. [cite: 207]
    * Estilos para footer fijo y `padding-top` en `body` para navbar fija. [cite: 208]
* **`<body>`**: [cite: 209]
    * **Barra de Navegación (`<nav>`):** `navbar-dark bg-primary fixed-top`. [cite: 209]
        * Marca "RequestApp" enlaza a `home`. [cite: 210] Botón "toggler". [cite: 211]
        * Enlaces Izquierda: "Home", "Dashboard", "New Request" (autenticados). [cite: 212, 213] "Manage Prices" (admin/staff). [cite: 214] Clase `active` dinámica. [cite: 215]
        * Enlaces Derecha: Menú desplegable de usuario (nombre/email, "Profile", "Logout" con form POST). [cite: 216] Enlace "Login" si no autenticado. [cite: 217]
    * **Contenido Principal (`<main class="container">`):** [cite: 218]
        * Muestra mensajes flash de Django (`alert-dismissible`). [cite: 219, 220]
        * `{% block content %}`. [cite: 221]
    * **Pie de Página (`<footer>`):** Copyright. [cite: 222]
    * **JavaScript:** Bootstrap 5 bundle (CDN). [cite: 223] `{% block extra_js %}`. [cite: 224]

### 10.2. Plantillas de Páginas Generales y Autenticación
* **`home.html`**: [cite: 225] "Jumbotron" de bienvenida. [cite: 226] Botones a Dashboard y New Request. [cite: 227] Enlaces a Profile y placeholder para Soporte. [cite: 228]
* **`profile.html`**: [cite: 229] Formularios `CustomUserChangeForm` y `CustomPasswordChangeForm`. [cite: 229] Muestra errores y mensajes. [cite: 230]
* **`choose_request_type.html`**: [cite: 231] Selección de tipo de solicitud. [cite: 231] Enlaces a formularios de creación en tarjetas Bootstrap, organizadas por equipo. [cite: 232, 233]
* **`registration/login.html`**: Formulario de inicio de sesión personalizado. Muestra errores de formulario y mensajes informativos (`next`).
* **`registration/logged_out.html`**: Mensaje de cierre de sesión exitoso con enlace para volver a iniciar sesión.

### 10.3. Plantillas de Creación de Solicitudes [cite: 234, 235, 236]
Renderizan los formularios de creación, heredan de `base.html`, usan Bootstrap.
* **`user_records.html`**: [cite: 236] `UserRecordsRequestForm` y `UserGroupFormSet`. [cite: 237] JS para: deshabilitar formset si hay `user_file`/`user_link`[cite: 238]; añadir/eliminar forms del formset[cite: 239]; `access_level` condicionalmente requerido[cite: 240]; visibilidad/obligatoriedad de `scheduled_date`. [cite: 241] Muestra errores. [cite: 242]
* **`deactivation_toggle_request.html`**: [cite: 243] `DeactivationToggleRequestForm`. Campos `priority`, `schedule_request`, `scheduled_date`. [cite: 244] JS para: `properties_with_policies` condicional[cite: 244]; visibilidad/obligatoriedad de otros campos según `deactivation_toggle_type`[cite: 245]; lógica de programación. [cite: 246]
* **`unit_transfer_request.html`**: [cite: 247] `UnitTransferRequestForm`. Campos `priority`, `schedule_request`, `scheduled_date`. [cite: 248] JS para: `properties` opcional[cite: 248]; campos "Partner to Prospect" condicionales[cite: 249, 250]; lógica de programación.
* **`address_validation_request.html`**: [cite: 251] `AddressValidationRequestForm`. Input `request_files` (`multiple`). [cite: 252] Campos `priority`, `schedule_request`, `scheduled_date`. [cite: 253] JS para: `opportunity_id` condicional[cite: 253]; lógica de programación. [cite: 254]
* **`property_records_request.html`**: [cite: 255] `PropertyRecordsRequestForm`. Campos `priority`, `schedule_request`, `scheduled_date`. [cite: 255] JS complejo para: campos `property_records_*` condicionales según `property_records_type`[cite: 256]; opcionales si hay `user_file`/`user_link`[cite: 257]; lógica anidada para "Coverage Type/Amount"[cite: 258]; `properties` obligatorio si no hay `user_file`/`user_link`[cite: 259]; lógica de programación.
* **`generating_xml_request.html`**: [cite: 260] `GeneratingXmlRequestForm`. Sin `priority` (default en vista). [cite: 261] Sin programación. JS para ZIPs condicionales. [cite: 262]
* **`stripe_disputes_request.html`**: [cite: 264] `StripeDisputesRequestForm`. Sin `priority` (default en vista). [cite: 265] Sin programación. Sin JS condicional complejo (validación en backend). [cite: 266]

### 10.4. Plantilla del Dashboard (`portal_operations_dashboard.html`) [cite: 267]
* Tabla responsiva: `unique_code`, `timestamp` (y `scheduled_date` si aplica [cite: 268]), tipo, equipo, `priority` (badge [cite: 268]), solicitante, partner, `status` (badge, incl. 'Scheduled' [cite: 268]), operador, QA, TAT (`format_timedelta` [cite: 268]).
* Filtros GET (botones radio): tipo, estado, equipo, rango de fechas. [cite: 269] JS `applyFilters()`. [cite: 270]
* Paginación. [cite: 271] Botón "New Request". [cite: 271]
    * *El PDF mencionaba exportación CSV, no presente actualmente.* [cite: 272]

### 10.5. Plantillas de Detalle de Solicitud (Genéricas y Específicas) [cite: 273]
Renderizadas por `request_detail` según `type_of_process`.
* **Estructura Común:** [cite: 274]
    * Cabecera: `unique_code`, `status` (badge con estilos para 'Scheduled', 'Pending for Approval'). [cite: 274]
    * **Indicadores Visuales (Alertas):** [cite: 275]
        * `update_needed_flag` activo (y estado no final/espera). [cite: 275]
        * `status == 'blocked'` (con razón del último bloqueo). [cite: 276]
        * `is_rejected_previously == True` y estado `in_progress`/`pending` (con razón del último rechazo). [cite: 277]
        * `status == 'scheduled'` o `status == 'pending_approval'` con `scheduled_date` (indicando fecha de activación). [cite: 278]
    * **Info General (Col. Izquierda):** `<dl>` con `priority` (badge), tipo, equipo, solicitante, timestamps (`timestamp`, `operated_at`, `completed_at`, `scheduled_date`, `effective_start_time_for_tat`, etc.) localizados con `{% timezone %}`. [cite: 279, 280] TAT con `format_timedelta`. [cite: 281]
    * **Detalles Específicos de Submisión (Col. Derecha):** Campos del `type_of_process`, `user_file`/`user_link`. [cite: 282]
        * Para "Address Validation": Lista `address_files`. [cite: 283]
        * Para "Generating XML": Enlaces a archivos `operator_*_file_slot*`.
        * Para "Stripe Disputes": Conteos de disputas.
    * **Detalles de Operación:** Tarjeta separada si hay datos (`num_updated_users`, `operating_notes`, etc.). [cite: 284]
        * Para "Address Validation": Campos específicos como `av_number_of_units`, `link_to_assets`, etc.
    * **Sección Salesforce (para Address Validation):**
        * "Salesforce Opportunity Information": Muestra `salesforce_opportunity_name`, `address_validation_opportunity_id`, `salesforce_standard_opp_id`, `salesforce_link`, `salesforce_account_manager`, `salesforce_number_of_units`, `salesforce_closed_won_date`, `salesforce_leasing_integration_software`, `salesforce_information_needed_for_assets`.
        * "Salesforce Attachments": Lista los archivos de `SalesforceAttachmentLog` con enlaces a Salesforce.
    * **Historial de Acciones:** Secciones para `BlockedMessage`, `ResolvedMessage`, `RejectedMessage`. [cite: 285]
    * **Botones de Acción:** Visibilidad controlada por `status`, `type_of_process`, y roles. [cite: 286] Consideración para estados 'scheduled'/'pending_approval'. [cite: 287]
    * **Modales para Acciones:** Bootstrap. IDs con sufijos (`_ur`, `_dt`, etc.). [cite: 288, 289]
        * Modales "Send to QA" y "Complete":
            * Para User Records, Unit Transfer, Address Validation, Property Records: Usan `OperateForm` con campos numéricos de operación. [cite: 291]
            * **Para Generating XML:** Usa `GeneratingXmlOperateForm` (pasado como `form_for_modal`). JS maneja visibilidad de campos de archivo basados en `qa_needs_file_correction` (checkbox para QA) y si es un rechazo previo (para operador). [cite: 292]
            * **Para Stripe Disputes:** Muestra campos `stripe_premium_disputes`, `stripe_ri_disputes`, `operating_notes`. JS valida obligatoriedad. [cite: 292]
            * Para Deactivation/Toggle: Simplificado, muestra principalmente `operating_notes`. [cite: 292]
        * JS para validación en modales. [cite: 293]

### 10.6. Plantillas de Formularios de Acción Simples [cite: 294]
* `block_form.html`, `resolve_form.html`, `reject_form.html`: Renderizan `BlockForm`, `ResolveForm`, `RejectForm`. [cite: 294] (Actualmente se usan modales). [cite: 295]
* `operate_form.html`, `complete_form.html`: Renderizan `OperateForm`. Para vistas separadas si no se usa modal. [cite: 296]

---
## 11. Lógica de Tareas en Segundo Plano (Django-Q2) [cite: 297]
Utiliza `django-q2` para procesos asíncronos y programados.

### 11.1. Activación de Solicitudes Programadas (`tasks/scheduled_jobs.py`) [cite: 298]
* **`process_scheduled_requests()`**:
    * Busca `UserRecordsRequest` con `status='scheduled'` y `scheduled_date <= today_utc`. [cite: 299]
    * Cambia `status` a `pending`. [cite: 300]
    * Establece `effective_start_time_for_tat = current_time_utc`. [cite: 300]
    * Registra logs de las activaciones.

### 11.2. Sincronización con Salesforce (`tasks/salesforce_sync.py`)
* **`sync_salesforce_opportunities_task()`**:
    * **Implementada y probada.**
    * Obtiene credenciales de Salesforce desde `settings.py`.
    * Conecta a Salesforce usando `simple_salesforce`.
    * Ejecuta consulta SOQL para Opportunities con criterios específicos (StageName = '5-Closed Won', OwnerId != '005f40000052NHqAAM' (Invisible User), Exclude\_from\_reporting\_\_c = false, assets\_uploaded\_\_c = false, Assets\_Converted\_\_c = false, Send\_Opportunity\_to\_Jetty\_\_c = 'No', Invisible\_Status\_\_c = 'New', Closed\_Won\_Date\_\_c >= 2022-06-01, y ciertos RecordTypeIds y Types).
    * Para cada Opportunity:
        * Omite si no tiene `Opportunity_ID__c`.
        * Obtiene o crea un `CustomUser` del sistema (`SALESFORCE_SYSTEM_USER_EMAIL`).
        * Dentro de una `transaction.atomic()`:
            * Crea una `UserRecordsRequest` de `type_of_process='address_validation'`, mapeando campos de la Opportunity (Partner Name, Opportunity ID, SF Standard ID, SF Opp Name, Number of Units, Link, Account Manager, Closed Won Date, Leasing Integration Software, Info for Assets).
            * Establece `status='pending'`, `priority=PRIORITY_NORMAL`, `team=TEAM_REVENUE`.
            * Obtiene `ContentDocumentLink` y luego `ContentVersion` para encontrar adjuntos de la Opportunity.
            * Crea registros `SalesforceAttachmentLog` para cada adjunto, almacenando nombre, extensión y enlace al archivo en Salesforce.
            * Actualiza el campo `Invisible_Status__c` de la Opportunity en Salesforce a 'In Progress'.
    * Registra logs detallados del proceso y maneja errores.

### 11.3. Configuración y Ejecución del Cluster (`tasks/apps.py`)
* El método `ready()` de `TasksConfig(AppConfig)`:
    * Verifica si `django_q` está en `INSTALLED_APPS`.
    * Crea/verifica la tarea programada `process_scheduled_requests` para ejecutarse diariamente a la 1:00 PM UTC (`Schedule.DAILY`). [cite: 301, 302]
    * Crea/verifica la tarea programada `sync_salesforce_opportunities_task` para ejecutarse tres veces al día (1 PM, 4 PM, 7 PM UTC) usando `schedule_type=Schedule.CRON` y la expresión cron `0 13,16,19 * * *`. [cite: 303, 342]
* Para ejecutar las tareas, el cluster `python manage.py qcluster` debe estar activo. [cite: 305] La configuración `Q_CLUSTER` en `settings.py` (con `catch_up: False`) define su comportamiento. [cite: 307]

---
## 12. Administración de Django (`tasks/admin.py`) [cite: 308]
Personalización del sitio de administración para una gestión eficiente.
* **`CustomUserAdmin(UserAdmin)`**: Extiende `UserAdmin`. Incluye `timezone` en `fieldsets`, `list_display`, y `list_filter`. [cite: 309, 310]
* **Inlines para `UserRecordsRequestAdmin`**: [cite: 311]
    * `BlockedMessageInline`, `ResolvedMessageInline`, `RejectedMessageInline`: `admin.TabularInline` para ver historiales (solo lectura). [cite: 311]
    * `AddressValidationFileInline`: Muestra archivos de "Address Validation" con enlace (`file_link_display`). [cite: 312]
* **`UserRecordsRequestAdmin(admin.ModelAdmin)`**: [cite: 313]
    * `list_display`: Muestra campos clave como `unique_code`, `type_of_process`, `requested_by_link`, `partner_name`, `priority`, `team`, `status`, `operator_link`, `qa_agent_link`, `timestamp`, `completed_at`. [cite: 314]
    * `list_filter`: Permite filtrar por `status`, `type_of_process`, `team`, `priority`, `timestamp`, `operator`, `qa_agent`, `requested_by`. [cite: 315]
    * `search_fields`: Búsqueda por `unique_code`, `partner_name`, emails de usuarios, `team`, `priority`, `special_instructions`. [cite: 315]
    * `readonly_fields`: Lista extensa incluyendo `unique_code`, timestamps de flujo, datos generados (ej. `user_groups_data_display`), campos específicos de tipo, detalles de operación, y campos de Salesforce, para asegurar modificaciones a través del flujo de la app. [cite: 316, 317]
    * `fieldsets`: Organiza campos en secciones colapsables: Request Info, Status & Assignment, Request Data, detalles por tipo de proceso (Deactivation/Toggle, Unit Transfer, Generating XML, Address Validation, Stripe Disputes, Property Records), Operation Details Recorded, Salesforce Opportunity Information, Workflow Timestamps. [cite: 318]
    * `inlines`: `AddressValidationFileInline`, `BlockedMessageInline`, `ResolvedMessageInline`, `RejectedMessageInline`. [cite: 319]
    * **Métodos de Display Personalizados**: `requested_by_link`, `operator_link`, `qa_agent_link` (enlaces a perfiles de usuario); `user_file_link`, `user_link_display` (enlaces a archivos/links); `user_groups_data_display` (formatea JSON). [cite: 319, 320]
    * **Acciones de Admin**:
        * `trigger_salesforce_sync_action`: Encola la tarea `tasks.salesforce_sync.sync_salesforce_opportunities_task`.
        * `trigger_scheduled_jobs_action`: Encola la tarea `tasks.scheduled_jobs.process_scheduled_requests`.
* **`HistoryMessageAdmin(admin.ModelAdmin)`**: Clase base para `BlockedMessageAdmin`, `ResolvedMessageAdmin`, `RejectedMessageAdmin`. [cite: 321]
    * Define `list_display` común (`request_link`, `actor_email`, `timestamp_with_tz`, `short_reason`), `search_fields`. [cite: 322]
    * Campos mayormente de solo lectura; sin permisos de añadir/cambiar desde admin. [cite: 323]
* **`BlockedMessageAdmin`, `ResolvedMessageAdmin`, `RejectedMessageAdmin`**: Heredan de `HistoryMessageAdmin`. Personalizan `list_filter` y `timestamp_order_field`. `RejectedMessageAdmin` también muestra `is_resolved_qa`. [cite: 324, 325]
* **`AddressValidationFileAdmin(admin.ModelAdmin)`**: Para `AddressValidationFile`. `list_display` con `file_link_display`. Solo lectura, sin permisos de añadir/cambiar. [cite: 325]
* **`OperationPriceAdmin(admin.ModelAdmin)`**: Para `OperationPrice`. [cite: 326] `fieldsets` para precios y costos. Permite crear solo una instancia; deshabilita borrado. [cite: 327]
* **`SalesforceAttachmentLogAdmin(admin.ModelAdmin)`**: Para `SalesforceAttachmentLog`. `list_display` con `request_link_admin`, `file_name`, `salesforce_file_link_display`. Solo lectura, sin permisos de añadir/cambiar.

---
## 13. Configuración del Entorno de Desarrollo
*(Igual que la versión anterior del README. Asegúrate de tener Python, Git, y pip instalados.)*

1.  **Clonar Repositorio:** `git clone <URL_DEL_REPOSITORIO>`
2.  **Entorno Virtual:** `python -m venv venv`, luego activar (`venv\Scripts\activate` o `source venv/bin/activate`).
3.  **Instalar Dependencias:** `pip install -r requirements.txt`.
4.  **Archivo `.env`:** Crear en la raíz con `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=True`. Añadir credenciales de Salesforce si se probará la sincronización.
5.  **Migraciones:** `python manage.py migrate`.
6.  **Superusuario:** `python manage.py createsuperuser`.
7.  **Servidor de Desarrollo:** `python manage.py runserver`.
8.  **Cluster Django-Q2 (otra terminal):** `python manage.py qcluster`.

---
## 14. Despliegue (Heroku)
*(Igual que la versión anterior del README. Consideraciones clave repetidas abajo.)*

1.  **`Procfile`**:
    ```Procfile
    release: python manage.py migrate
    web: gunicorn requests_webpage.wsgi --log-file -
    worker: python manage.py qcluster
    ```
2.  **`runtime.txt`**: Especificar versión de Python (ej. `python-3.10.12`).
3.  **`requirements.txt`**: Debe incluir `gunicorn`, `psycopg2-binary`.
4.  **Variables de Entorno en Heroku**: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DATABASE_URL`, credenciales de Salesforce.
5.  **Buildpack**: `heroku/python`.
6.  **Add-ons**: Heroku Postgres.

---
## 15. Próximos Pasos y Mejoras Futuras [cite: 333]

* **Pruebas Exhaustivas**: Pruebas unitarias y de integración para todos los flujos, incluyendo la lógica de Salesforce y las nuevas adaptaciones de `OperateForm`. [cite: 337]
* **Internacionalización Completa**: Generar y traducir archivos `.po` para todos los idiomas soportados. [cite: 338]
* **Notificaciones por Correo Electrónico**: Implementar sistema de notificaciones para eventos clave. [cite: 345]
* **Refinamiento Continuo de la UI/UX**: Basado en feedback. [cite: 346]
* **Documentación para el Usuario Final**: Guías y tutoriales. [cite: 347]
* **Optimización y Seguridad para Producción**: Configuraciones avanzadas de Gunicorn/Nginx, base de datos, etc. [cite: 348]
