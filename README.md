# Plataforma de Gestión de Solicitudes (requests_webpage)

**Versión del Código Fuente:** Analizado el 6 de junio de 2025
**Fecha de Actualización del README:** 6 de junio de 2025
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
    * [3.6. Gestión de Archivos Estáticos y Multimedia (Dual: Local y S3)](#36-gestión-de-archivos-estáticos-y-multimedia-dual-local-y-s3)
    * [3.7. Internacionalización (i18n) y Localización (l10n)](#37-internacionalización-i18n-y-localización-l10n)
    * [3.8. Tareas en Segundo Plano (Django-Q2)](#38-tareas-en-segundo-plano-django-q2)
    * [3.9. Integración con Salesforce](#39-integración-con-salesforce)
    * [3.10. Configuración de Logging (Dual: Archivo y Consola)](#310-configuración-de-logging-dual-archivo-y-consola)
    * [3.11. Procesadores de Contexto de Plantillas](#311-procesadores-de-contexto-de-plantillas)
    * [3.12. Configuración de Email y Telegram para Notificaciones](#312-configuración-de-email-y-telegram-para-notificaciones)
4.  [Enrutamiento de URLs (`urls.py`)](#4-enrutamiento-de-urls-urlspy)
5.  [Modelo de Datos Detallado (`tasks/models.py`)](#5-modelo-de-datos-detallado-tasksmodelspy)
6.  [Definición Centralizada de Opciones (`tasks/choices.py`)](#6-definición-centralizada-de-opciones-taskschoicespy)
7.  [Formularios Detallados (`tasks/forms.py`)](#7-formularios-detallados-tasksformspy)
8.  [Lógica de las Vistas (`tasks/views.py`)](#8-lógica-de-las-vistas-tasksviewspy)
9.  [Módulo de Notificaciones (`tasks/notifications.py`)](#9-módulo-de-notificaciones-tasksnotificationspy)
10. [Estructura y Contenido de las Plantillas (`tasks/templates/`)](#10-estructura-y-contenido-de-las-plantillas-taskstemplates)
11. [Tareas Programadas y en Segundo Plano (`django-q2`)](#11-tareas-programadas-y-en-segundo-plano-django-q2)
12. [Interfaz de Administración de Django (`tasks/admin.py`)](#12-interfaz-de-administración-de-django-tasksadminpy)
13. [Configuración del Entorno de Desarrollo](#13-configuración-del-entorno-de-desarrollo)
14. [Despliegue (Heroku)](#14-despliegue-heroku)
15. [Consideraciones Adicionales y Próximos Pasos](#15-consideraciones-adicionales-y-próximos-pasos)

---

## 1. Introducción y Propósito

La plataforma `requests_webpage` es una aplicación web integral, desarrollada sobre el robusto framework Django, concebida como una solución centralizada y altamente adaptable para la gestión eficiente de una diversidad de procesos y solicitudes operativas internas. El sistema permite a los usuarios la creación, el seguimiento detallado y la administración de múltiples tipos de solicitudes, cada una con flujos de trabajo, campos de datos específicos y lógicas de asignación a los equipos responsables.

Las funcionalidades clave incluyen:
* **Gestión Completa de Solicitudes:** Cubre el ciclo de vida completo desde la creación hasta la finalización, pasando por estados intermedios como "En Progreso", "Pendiente de QA", "Bloqueado" y "Cancelado".
* **Integración con Salesforce:** Automatiza la creación de solicitudes a partir de Oportunidades en Salesforce, manteniendo la sincronización entre ambas plataformas.
* **Cálculo de Costos y TAT:** Mide y almacena de forma persistente los costos de cliente, costos operativos y Tiempos de Respuesta (TAT) para cada solicitud.
* **Reportes Avanzados:** Ofrece un **Reporte de Resumen de Costos y Rendimiento** mejorado que ahora incluye métricas clave como el recuento total de solicitudes, el costo promedio y el TAT promedio, tanto a nivel general como desglosado por equipo y tipo de proceso. Esta vista también permite al usuario alternar la visualización de fechas entre su hora local y **UTC (la zona horaria estándar para facturación)**.
* **Sistema de Notificaciones por Eventos:** Un completo sistema notifica a los usuarios relevantes sobre 13 eventos clave en el ciclo de vida de una solicitud a través de correo electrónico (vía SendGrid) y Telegram. El envío de correos es **configurable por evento desde el panel de administración de Django**.
* **Almacenamiento de Archivos Flexible:** La aplicación está configurada para un manejo dual de archivos: utiliza el sistema de archivos local durante el desarrollo y se integra con **Amazon S3** para un almacenamiento de objetos persistente y escalable en producción.
* **Nuevas Funcionalidades de Flujo de Trabajo:**
    * **Descuentos:** Los administradores pueden aplicar un **descuento por porcentaje** a cualquier solicitud completada directamente desde el admin de Django. El precio final con descuento se refleja en la página de detalle y se utiliza para todos los cálculos en el reporte de facturación.
    * **Desasignación (Unassign):** Los agentes (Operadores y Agentes de QA) pueden desasignarse de una tarea en progreso, devolviéndola a la cola de "Pendiente" correspondiente, para ser tomada por otro agente. Esta acción está controlada por permisos específicos.

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
        * `hooks.py`: Contiene funciones hook para las tareas de `django-q2` que registran el resultado de las tareas asíncronas.
        * `models.py`: Define los modelos ORM de Django, que representan la estructura de las tablas de la base de datos.
        * `notifications.py`: Nuevo archivo que centraliza toda la lógica para construir y enviar las 13 tipos de notificaciones por correo electrónico y Telegram.
        * `salesforce_sync.py`: Contiene la lógica específica para la tarea de sincronización con Salesforce, ahora también llama a la función de notificación.
        * `scheduled_jobs.py`: Define las funciones que se ejecutan como tareas programadas. Ahora también llama a la función de notificación correspondiente.
        * `tests.py`: Contiene pruebas unitarias y de integración para la aplicación `tasks`.
        * `urls.py`: Define los patrones de URL específicos para la aplicación `tasks`.
        * `validators.py`: Contiene validadores personalizados para campos de modelos o formularios.
        * `migrations/`: Directorio que almacena los archivos de migración de la base de datos.
        * `static/tasks/`: Directorio para archivos estáticos (CSS, JavaScript, imágenes).
        * `templates/tasks/`: Directorio que contiene las plantillas HTML para la interfaz de usuario.
            * `emails/`: Nuevo directorio que contiene las plantillas para las notificaciones por correo electrónico.
            * `registration/`: Contiene plantillas personalizadas para el flujo de autenticación.
        * `templatetags/`: Contiene tags y filtros de plantillas personalizados.
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
* **`ALLOWED_HOSTS`**: Lista de nombres de host/dominio permitidos para servir la aplicación.
* **`CSRF_TRUSTED_ORIGINS`**: Lista de orígenes confiables para solicitudes seguras (HTTPS).

### 3.2. Aplicaciones Instaladas (`INSTALLED_APPS`)
* Aplicaciones estándar de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, etc.
* Aplicaciones de terceros:
    * `'whitenoise.runserver_nostatic'`: Para servir archivos estáticos durante el desarrollo.
    * `'storages'`: Para la integración con almacenamientos externos como Amazon S3.
    * `'django_q'`: (`django-q2`) para la gestión de tareas en segundo plano.
* Aplicación principal del proyecto: `'tasks'`.

### 3.3. Middleware
Define las capas que procesan las solicitudes y respuestas.
* `whitenoise.middleware.WhiteNoiseMiddleware`: Para servir archivos estáticos eficientemente en producción.
* `django.middleware.locale.LocaleMiddleware`: Habilita la internacionalización.
* Y otros middlewares estándar de Django para seguridad, sesiones y autenticación.

### 3.4. Autenticación y Modelo de Usuario
* `AUTH_USER_MODEL = 'tasks.CustomUser'`: Se utiliza el modelo `CustomUser` personalizado.
* `LOGOUT_REDIRECT_URL` y `LOGIN_REDIRECT_URL`: Definen las redirecciones tras cerrar e iniciar sesión.

### 3.5. Configuración de Base de Datos
* `DATABASES`: Configurada usando `dj_database_url.config()`, permitiendo leer desde `DATABASE_URL` (ideal para Heroku) con un fallback a SQLite para desarrollo local.

### 3.6. Gestión de Archivos Estáticos y Multimedia (Dual: Local y S3)
La configuración de archivos ha sido refactorizada para un manejo dual, adaptándose automáticamente al entorno basado en `DEBUG`.
* **En Desarrollo (`DEBUG=True`):**
    * `DEFAULT_FILE_STORAGE` se establece en `'django.core.files.storage.FileSystemStorage'`.
    * Los archivos subidos por los usuarios (`MEDIA`) se guardan en un directorio `media/` local. El servidor de desarrollo está configurado en `urls.py` para servir estos archivos.
* **En Producción (`DEBUG=False`):**
    * `DEFAULT_FILE_STORAGE` se establece en `'storages.backends.s3boto3.S3Boto3Storage'`, indicando a Django que use Amazon S3 para todos los `FileField`.
    * Las credenciales y configuración de S3 se cargan desde variables de entorno.
    * Los archivos estáticos (`STATIC`) siguen siendo gestionados eficientemente por `WhiteNoise`.

### 3.7. Internacionalización (i18n) y Localización (l10n)
* `LANGUAGE_CODE = 'en-us'` y `TIME_ZONE = 'UTC'`. `USE_I18N` y `USE_TZ` están habilitados, asegurando que todos los timestamps se manejen internamente en UTC.

### 3.8. Tareas en Segundo Plano (Django-Q2)
* `Q_CLUSTER`: Diccionario que configura el cluster de `django-q2`, incluyendo nombre, workers, timeout, reintentos, y nivel de log.

### 3.9. Integración con Salesforce
* Las credenciales (`SF_USERNAME`, `SF_PASSWORD`, etc.) se cargan desde el entorno.

### 3.10. Configuración de Logging (Dual: Archivo y Consola)
De manera similar al almacenamiento de archivos, el sistema de logging ahora es dual:
* **En Desarrollo (`DEBUG=True`):** Los logs se envían tanto a la consola como a un archivo local (`logs/tasks_app.log`) para una depuración más sencilla.
* **En Producción (`DEBUG=False`):** Los logs se envían únicamente a la consola (`stdout`/`stderr`), que es la práctica recomendada para plataformas como Heroku.

### 3.11. Procesadores de Contexto de Plantillas
* `'tasks.context_processors.user_role_permissions'` añadido para hacer disponibles `is_admin_user` e `is_leadership_user` globalmente en las plantillas.

### 3.12. Configuración de Email y Telegram para Notificaciones
* **Email (SendGrid):** `EMAIL_BACKEND` y las credenciales del host SMTP se cargan desde variables de entorno.
* **Telegram:** `TELEGRAM_BOT_TOKEN` y `TELEGRAM_DEFAULT_CHAT_ID` se cargan desde variables de entorno.
* **`SITE_DOMAIN`**: Variable de entorno (ej. `SITE_DOMAIN='https://tu-app.herokuapp.com'`) utilizada para construir URLs absolutas en las notificaciones.

---
## 4. Enrutamiento de URLs (`urls.py`)

La gestión de las rutas de la aplicación se divide en dos niveles, siguiendo las mejores prácticas de Django para la modularidad.

### 4.1. Enrutador Principal del Proyecto
**Archivo:** `requests_webpage/urls.py`

Este archivo es el punto de entrada principal para todas las URLs del sitio.
* `path('admin/', admin.site.urls)`: Activa el sitio de administración de Django.
* `path('accounts/', include('django.contrib.auth.urls'))`: Incluye las URLs predefinidas de Django para la autenticación de usuarios (login, logout, cambio de contraseña, etc.).
* `path('rhino/', include('tasks.urls', namespace='tasks'))`: La ruta más importante. Delega todas las URLs que comienzan con `/rhino/` al archivo de URLs de la aplicación `tasks`. El `namespace='tasks'` permite usar nombres de URL cualificados como `tasks:rhino_dashboard`, evitando colisiones de nombres.
* `path('', tasks_views.home, name='home')`: Define la vista para la página de inicio del sitio en la URL raíz.

### 4.2. Enrutador de la Aplicación `tasks`
**Archivo:** `tasks/urls.py`

Este archivo contiene los patrones de URL específicos para la aplicación `tasks`, todos ellos bajo el prefijo `/rhino/`.
* `app_name = 'tasks'`: Define el nombre de la aplicación para el enrutamiento.
* **Autenticación:** Rutas personalizadas para `login` y `logout`.
* **Vistas Principales y de Usuario:** Rutas para el `rhino_dashboard`, `profile`, `manage_prices`, `client_cost_summary` y `choose_request_type`.
* **Vistas de Generación de Reportes CSV:** Rutas para `revenue_support_report`, `compliance_xml_report`, y `accounting_stripe_report`.
* **Vistas de Creación de Solicitudes:** Rutas dedicadas para cada uno de los 7 tipos de proceso (ej. `/new_user_records/`, `/new_deactivation_toggle/`, etc.).
* **Vistas de Detalle y Acciones:**
    * `path('request/<int:pk>/', views.request_detail, name='request_detail')`: La vista central para mostrar los detalles de una solicitud específica.
    * Rutas para cada acción posible sobre una solicitud, usando el `pk` de la solicitud (ej. `operate`, `block`, `send_to_qa`, `complete`, `cancel`, `approve_deactivation_toggle`, etc.).
    * **Nueva URL de Acción:** Se ha añadido la ruta `path('request/<int:pk>/unassign/', views.unassign_agent, name='unassign_agent')` para manejar la nueva funcionalidad de desasignación de agentes.

---
## 5. Modelo de Datos Detallado (`tasks/models.py`)

Describe la estructura de la base de datos de la aplicación `tasks`.

### 5.1. `CustomUser(AbstractUser)`
Modelo de usuario personalizado que extiende `AbstractUser` de Django.
* **Campos Principales:**
    * `email`: `EmailField(unique=True)`. Se utiliza como `USERNAME_FIELD` para la autenticación.
    * `timezone`: `CharField(max_length=100, default='UTC', choices=...)`. Almacena la zona horaria preferida del usuario, con `choices` generadas a partir de `pytz.common_timezones`.

### 5.2. `UserRecordsRequest(models.Model)`
Es el modelo central que representa todas las solicitudes operativas. Es un modelo extenso y flexible que incluye los siguientes grupos de campos:
* **Identificación y Estado:** `type_of_process`, `unique_code`, `timestamp`, `requested_by`, `team`, `priority`, `status`, etc.
* **Flujo de Trabajo y Asignación:** `operator`, `qa_agent`, `update_needed_flag`, `scheduled_date`, `effective_start_time_for_tat`, etc.
* **Detalles de Operación y QA:** `num_updated_users`, `operating_notes`, etc.
* **Campos Específicos por Proceso:** Un amplio conjunto de campos opcionales (`null=True, blank=True`) para cada uno de los 7 tipos de proceso, cuya relevancia se maneja en los formularios y vistas.
* **Integración con Salesforce:** Campos para almacenar IDs y metadatos de las Oportunidades de Salesforce.
* **Costos Calculados:** Campos `DecimalField` que "congelan" los costos de cliente, operación y QA cuando una solicitud se completa.

#### 5.2.1. Funcionalidad de Descuento
El modelo ha sido extendido para soportar descuentos aplicables por administradores.
* **`discount_percentage`**: `DecimalField`. Nuevo campo para almacenar el porcentaje de descuento (de 0.00 a 100.00) que un administrador puede aplicar.
* **`final_price_client_completed`**: `DecimalField`. Nuevo campo que almacena el precio final para el cliente **después** de aplicar el descuento. Este valor se calcula y se guarda automáticamente cada vez que se modifica la solicitud a través del método `save()` sobrescrito.
* **Propiedades de Cálculo (`@property`):**
    * `calculated_discount_amount`: Calcula el monto monetario del descuento (`grand_total * (percentage / 100)`).
    * `final_price_after_discount`: Calcula el precio final (`grand_total - discount_amount`). Esta propiedad es utilizada por el método `save()` para poblar `final_price_client_completed` y por las plantillas de detalle y dashboard para mostrar el desglose de precios de forma clara.

### 5.3. Modelos de Historial y Soporte
* **`BlockedMessage`, `ResolvedMessage`, `RejectedMessage`**: Modelos que registran eventos clave (bloqueos, resoluciones, rechazos) con detalles como el usuario actor, la fecha y la razón/mensaje.
* **`AddressValidationFile`**: Almacena archivos múltiples para las solicitudes de "Address Validation".
* **`SalesforceAttachmentLog`**: Registra metadatos de los adjuntos de Salesforce.

### 5.4. Modelos de Configuración y Precios

* **`OperationPrice(models.Model)`**: Modelo Singleton que centraliza los precios y costos unitarios para todas las operaciones, permitiendo una gestión de precios centralizada.
* **`ScheduledTaskToggle(models.Model)`**: Permite habilitar o pausar tareas programadas (como la sincronización con Salesforce) desde el admin.

#### 5.4.1. `NotificationToggle`
**Nuevo Modelo.** Permite controlar individualmente desde el panel de administración si se envían notificaciones por correo electrónico para cada uno de los 13 tipos de eventos de notificación definidos.
* `event_key`: `CharField(unique=True, primary_key=True)`. Clave única que identifica el evento (ej. `'new_request_created'`).
* `is_email_enabled`: `BooleanField(default=True)`. Si es `True`, se envían correos para este evento; si es `False`, se omiten, permitiendo una gestión flexible del uso de servicios como SendGrid.

---
## 6. Definición Centralizada de Opciones (`tasks/choices.py`)

Este archivo es crucial para mantener la consistencia de las opciones utilizadas en los modelos y formularios.

### 6.1. Opciones de Modelos y Formularios
Contiene todas las tuplas `choices` (valor en BD, etiqueta legible) para campos como:
* `TYPE_CHOICES`: Los 7 tipos de procesos.
* `TEAM_CHOICES`, `PRIORITY_CHOICES`, `STATUS_CHOICES`: Equipos, prioridades y estados.
* Constantes y choices específicas para cada tipo de proceso: `DEACTIVATION_TOGGLE_CHOICES`, `UNIT_TRANSFER_TYPE_CHOICES`, `XML_STATE_CHOICES`, `PROPERTY_RECORDS_TYPE_CHOICES`, etc.

### 6.2. Claves de Eventos de Notificación
**Nueva sección.** Se han añadido constantes de cadena para las 13 claves de eventos de notificación. Estas claves son utilizadas por el modelo `NotificationToggle` y las funciones en `tasks/notifications.py` para identificar cada evento de forma única y consistente.
* **Ejemplos:**
    * `EVENT_KEY_NEW_REQUEST_CREATED = 'new_request_created'`
    * `EVENT_KEY_REQUEST_APPROVED = 'request_approved'`
    * `EVENT_KEY_REQUEST_COMPLETED = 'request_completed'`
* También se incluye un diccionario `ALL_NOTIFICATION_EVENT_KEYS` que mapea estas claves a descripciones legibles, utilizado en `apps.py` para la creación inicial de los `NotificationToggle`. Esto evita el uso de "cadenas mágicas" en el código, haciéndolo más mantenible.

---
## 7. Formularios Detallados (`tasks/forms.py`)

Este archivo define todos los formularios Django utilizados en la aplicación `tasks` para la entrada y validación de datos. Todos los `label` y `help_text` están en inglés. Los widgets de formulario están configurados con clases de Bootstrap para una mejor integración visual.

### 8.1. Formularios de Gestión de Usuario
* **`CustomUserChangeForm(UserChangeForm)`**: Para editar la información básica del perfil de usuario (`username`, `email`, `first_name`, `last_name`, `timezone`). No maneja el cambio de contraseña.
* **`CustomPasswordChangeForm(PasswordChangeForm)`**: Formulario especializado para que los usuarios cambien su propia contraseña, incluyendo la validación de la contraseña antigua y la confirmación de la nueva.

### 8.2. Formularios para la Creación de Solicitudes
* **`UserGroupForm(forms.Form)`**: Sub-formulario (utilizado en un `formset_factory`) para capturar detalles de grupos de usuarios dentro de una solicitud de tipo "User Records".
* **`UserRecordsRequestForm(forms.Form)`**: Formulario principal (no `ModelForm`) para crear solicitudes de tipo "User Records".
* **`DeactivationToggleRequestForm(forms.ModelForm)`**: Para crear solicitudes de "Deactivation and Toggle". Implementa lógica condicional para la obligatoriedad de campos basados en el `deactivation_toggle_type`.
* **`UnitTransferRequestForm(forms.ModelForm)`**: Para solicitudes de "Unit Transfer".
* **`GeneratingXmlRequestForm(forms.ModelForm)`**: Para solicitudes de "Generating XML files".
* **`AddressValidationRequestForm(forms.ModelForm)`**: Para crear solicitudes de "Address Validation".
* **`StripeDisputesRequestForm(forms.ModelForm)`**: Para solicitudes de "Stripe Disputes".
* **`PropertyRecordsRequestForm(forms.ModelForm)`**: Formulario complejo con muchos campos condicionales para solicitudes de "Property Records".

### 8.3. Formularios para Acciones de Flujo de Trabajo y Operación
* **Formularios de Acción Simples**:
    * `BlockForm(forms.Form)`: Un campo `reason` para bloquear una solicitud.
    * `ResolveForm(forms.Form)`: Campos `message`, `resolved_file`, `resolved_link` para resolver una solicitud bloqueada.
    * `RejectForm(forms.Form)`: Un campo `reason` para rechazar una solicitud.
* **`OperateForm(forms.ModelForm)`**: Formulario genérico para capturar detalles de operación cuando una solicitud se envía a QA o se completa. Su `__init__` personaliza dinámicamente los campos visibles y su obligatoriedad según el `type_of_process`.
* **`GeneratingXmlOperateForm(forms.ModelForm)`**: Hereda de `OperateForm` pero es específico para operar y completar solicitudes de "Generating XML files".
* **`OperationPriceForm(forms.ModelForm)`**: Formulario para editar la única instancia del modelo `OperationPrice`, permitiendo a los administradores gestionar los precios y costos.

### 8.4. Formulario para Proveer Actualización (`ProvideUpdateForm`)
* **`ProvideUpdateForm(forms.Form)`**: **Nuevo formulario**. Contiene un único campo `update_message` (`CharField` con `Textarea`) que es `required=True`. Este formulario se presenta en un modal cuando un usuario hace clic en el botón "Provide Update". El mensaje ingresado se pasa a la función de notificación `notify_update_provided` y no se almacena en la base de datos.

---
## 8. Lógica de las Vistas (`tasks/views.py`)

El archivo `tasks/views.py` contiene la lógica de negocio principal para manejar las solicitudes HTTP, interactuar con los modelos y formularios, y renderizar las plantillas.

### 8.1. Funciones Auxiliares y Control de Permisos
Se utilizan varias funciones helper para verificar los roles y permisos de los usuarios (ej. `is_admin`, `is_leadership`, `is_agent`, `can_cancel_request`, etc.). Estas funciones se usan frecuentemente con el decorador `@user_passes_test` o directamente en las vistas para controlar el acceso a funcionalidades.

### 8.2. Vistas de Creación y Visualización
* **Vistas de Creación:** Existen vistas dedicadas para cada uno de los 7 tipos de proceso (ej. `user_records_request`). Todas estas vistas, después de guardar exitosamente una nueva solicitud, ahora encolan una tarea asíncrona para llamar a la función de notificación correspondiente (`notify_new_request_created` o `notify_pending_approval_request`).
* **Vistas de Visualización:**
    * **`portal_operations_dashboard(request)`**: Muestra una tabla paginada de todas las solicitudes con filtros. La columna "Total Price" ha sido actualizada para mostrar el precio original tachado y el precio final con descuento si se ha aplicado uno, usando las propiedades del modelo.
    * **`request_detail(request, pk)`**: Muestra los detalles completos de una solicitud. La lógica de esta vista ha sido extendida para pasar al contexto una nueva variable booleana, `can_unassign`, que controla la visibilidad del nuevo botón "Unassign".

### 8.3. Vista de Resumen de Costos y Rendimiento (`client_cost_summary_view`)
Esta vista ha sido significativamente refactorizada para incorporar nuevas métricas y funcionalidades:
* **Cálculos Basados en Precio Final:** Todos los cálculos de costos (total, promedio, por equipo, por proceso) y los datos para los gráficos ahora utilizan el campo pre-calculado `final_price_client_completed` del modelo `UserRecordsRequest`. Esto se hace para reflejar con precisión los precios con descuento para la facturación. La vista ya no realiza cálculos complejos de descuento, sino que confía en el valor ya almacenado en la base de datos.
* **Nuevas Métricas de Rendimiento:** La vista ahora calcula y pasa a la plantilla:
    * **Recuento Total de Solicitudes:** El número de solicitudes completadas en el período.
    * **Costo Promedio por Solicitud:** El costo total dividido por el número de solicitudes.
    * **TAT Promedio:** El Tiempo de Respuesta promedio para todas las solicitudes en el período, calculado a nivel de base de datos para mayor eficiencia.
* **Manejo de Zona Horaria:** La vista procesa un parámetro GET `timezone_display` para determinar si los datos deben prepararse para ser mostrados en la hora local del usuario o en UTC. Pasa esta preferencia y el nombre de la zona horaria del usuario a la plantilla para que el JavaScript pueda configurar los gráficos dinámicamente.

### 8.4. Vistas de Acciones del Flujo de Trabajo
Las vistas que manejan cambios de estado ahora también disparan notificaciones asíncronas.

#### 8.4.1. Nueva Vista de Acción (`unassign_agent`)
* Se ha añadido una nueva vista, `unassign_agent`, que maneja la lógica para desasignar un agente de una tarea.
* **Permisos:** La acción solo está permitida para el agente actualmente asignado (Operador o Agente de QA) o para un administrador. Los usuarios del grupo "Leaderships" no pueden realizar esta acción.
* **Lógica:**
    * Si el estado de la solicitud es `'in_progress'`, cambia el estado a `'pending'` y limpia el campo `operator`.
    * Si el estado es `'qa_in_progress'`, cambia el estado a `'qa_pending'` y limpia el campo `qa_agent`.
    * El TAT (`effective_start_time_for_tat`) no se reinicia.

---
## 9. Módulo de Notificaciones (`tasks/notifications.py`)

Este **nuevo archivo** es el centro de toda la lógica de envío de notificaciones por correo electrónico y Telegram. Está diseñado para ser modular y extensible.

* **Funciones Helper de Notificación:**
    * **`send_request_notification_email(...)`**: Función genérica para enviar correos. Renderiza plantillas HTML y de texto plano y utiliza `django.core.mail.send_mail`.
    * **`send_telegram_message(...)`**: Envía mensajes de Telegram usando la API HTTP con la librería `requests`. Soporta `parse_mode='MarkdownV2'`.
    * **`is_email_notification_enabled(event_key_param)`**: Consulta el modelo `NotificationToggle` para verificar si las notificaciones por correo para un evento específico están habilitadas en el admin. Esta es la función clave para el control de envío de correos.

* **Funciones Específicas de Notificación por Evento:**
    * Se han implementado 13 funciones, una para cada evento del ciclo de vida de una solicitud (ej. `notify_new_request_created`, `notify_request_approved`, `notify_request_blocked`, etc.).
    * Cada función es responsable de:
        1.  Definir su `event_key` única.
        2.  Obtener los objetos de la base de datos necesarios.
        3.  **Verificar si el envío de correo está habilitado** llamando a `is_email_notification_enabled()`.
        4.  Si está habilitado, construye el `subject`, el `context` y la lista de destinatarios para el correo, y llama a `send_request_notification_email`.
        5.  Construir el mensaje específico para Telegram y llamar a `send_telegram_message`.
* **Uso Asíncrono:** Todas estas funciones de notificación están diseñadas para ser llamadas como tareas en segundo plano a través de `async_task` de `django-q2` desde las vistas y tareas programadas, asegurando que el envío de notificaciones no retrase la respuesta al usuario.

---
## 10. Estructura y Contenido de las Plantillas (`tasks/templates/`)

La aplicación `tasks` utiliza el sistema de plantillas de Django para generar la interfaz de usuario. Las plantillas están organizadas y aprovechan la herencia de plantillas y los tags personalizados para ser eficientes y mantenibles.

### 10.1. Plantillas de Detalle de Solicitud (`*_detail.html`)
Existen 7 plantillas de detalle específicas, una para cada `type_of_process` (ej. `user_records_detail.html`, `generating_xml_detail.html`). La vista `request_detail` selecciona dinámicamente la plantilla correcta para renderizar.
* **Estructura Común:**
    * Muestran información general de la solicitud (ID, estado, timestamps, prioridad, equipo, TAT).
    * Detalles de la sumisión (partner, archivos/enlaces, instrucciones especiales).
    * Detalles específicos del tipo de proceso.
    * Historial de acciones (Blocked, Resolved, Rejected messages).
    * **Botones de Acción Condicionales:** Un conjunto de botones que aparecen o se ocultan según el estado de la solicitud y los permisos del usuario actual.
* **Nuevas Funcionalidades en Plantillas de Detalle:**
    * **Botón "Unassign":** Se ha añadido un nuevo botón "Unassign" en la sección de acciones. Es visible condicionalmente para el agente asignado (Operador o QA) o un administrador (pero no para "Leaderships"), permitiéndoles liberarse de una tarea y devolverla a la cola pendiente.
    * **Desglose de Descuento:** La sección "Price Breakdown" (visible para admin/leadership en solicitudes completadas) ahora muestra condicionalmente el desglose del descuento. Si se aplica uno, la plantilla muestra el "Grand Total (Before Discount)", la línea del "Discount" (con porcentaje y monto), y el "Final Price". Si no hay descuento, la vista es la misma de antes.
    * **Modal para "Provide Update":** El botón para marcar una actualización como provista ahora abre un modal que contiene el `ProvideUpdateForm`, permitiendo al agente escribir un mensaje que se incluirá en la notificación.

### 10.2. Plantilla de Resumen de Costos (`cost_summary.html`)
Esta plantilla ha sido rediseñada para ser un potente dashboard de Business Intelligence:
* **Selector de Zona Horaria:** Se ha añadido un grupo de botones que permite al usuario cambiar la visualización de todas las fechas y gráficos entre su hora local y UTC (etiquetada como "Billing Timezone").
* **Tarjetas de Resumen (KPIs):** Muestra métricas clave: "Grand Total Cost" (con descuento), "Total Completed Requests", "Average Cost per Request", y "Average Turn Around Time".
* **Tablas de Datos Mejoradas:** Las tablas de resumen "By Team" y "By Process Type" ahora incluyen columnas para "Count", "Avg. Cost", y "Avg. TAT", además del costo total.
* **Gráficos:** Presenta gráficos de tarta (pie charts) para la distribución de costos y gráficos de dispersión (scatter/line charts) para las tendencias de costos a lo largo del tiempo. El JavaScript de la plantilla está configurado para respetar la selección de zona horaria del usuario.

### 10.3. Plantillas de Correo Electrónico
**Nuevo directorio:** `tasks/templates/tasks/emails/`
Este directorio contiene plantillas HTML y de texto plano separadas para cada uno de los 13 eventos de notificación (ej. `new_request_created.html`, `request_approved_notification.txt`, `update_provided_notification.html`, etc.). Estas plantillas renderizan mensajes dinámicos y formateados para las notificaciones por correo.

---
## 11. Tareas Programadas y en Segundo Plano (`django-q2`)

La aplicación utiliza `django-q2` para manejar tareas que deben ejecutarse en segundo plano (asíncronas) o de forma programada.

* **Tareas Asíncronas:** Todas las 13 funciones de notificación se ejecutan como tareas asíncronas usando `async_task`. Esto asegura que el envío de correos y mensajes de Telegram no retrase la respuesta al usuario que realiza una acción en la web.
* **`tasks/scheduled_jobs.py`**:
    * **`process_scheduled_requests()`**: Esta función se ejecuta diariamente. Busca solicitudes con estado 'scheduled' y cuya fecha de programación ha llegado, las activa cambiando su estado a 'pending', y ahora también **dispara la notificación** correspondiente (`notify_scheduled_request_activated`).
* **`tasks/salesforce_sync.py`**:
    * **`sync_salesforce_opportunities_task()`**: Se ejecuta múltiples veces al día. Se conecta a Salesforce, busca Oportunidades elegibles, y crea `UserRecordsRequest` de tipo "Address Validation". Ahora, después de crear cada solicitud, **dispara la notificación** `notify_new_request_created` para informar sobre la creación automática.
* **`tasks/apps.py` (Método `ready()`):**
    * Se encarga de configurar las tareas programadas al inicio de la aplicación, creando los objetos `Schedule` en la base de datos de Django Q si no existen.
    * También se encarga de crear las instancias iniciales del nuevo modelo `NotificationToggle` para los 13 eventos, asegurando que los controles estén disponibles en el admin desde el primer momento.
* **`tasks/hooks.py`**: Contiene la función `print_task_result(task)`, que se utiliza como un "hook" en las tareas asíncronas para registrar en los logs el resultado final (éxito o fallo) de cada tarea de notificación.

---
## 12. Interfaz de Administración de Django (`tasks/admin.py`)

Se han realizado personalizaciones significativas en el admin de Django para facilitar la gestión de los datos de la aplicación.
* **`CustomUserAdmin`**: Muestra campos personalizados del usuario.
* **`UserRecordsRequestAdmin`**: Ofrece una vista detallada y organizada para `UserRecordsRequest`.
    * Utiliza `fieldsets` para agrupar lógicamente la gran cantidad de campos del modelo.
    * Muestra modelos relacionados (como `BlockedMessage`) como "inlines".
    * **Gestión de Descuentos:** Se ha modificado para incluir una sección condicional "Discount Management (Admin Only)", visible y editable solo para superusuarios. Esta sección contiene el campo `discount_percentage`, permitiendo a los administradores aplicar descuentos de forma segura.
* **`NotificationToggleAdmin`**:
    * **Nueva Clase Admin.** Se ha registrado el modelo `NotificationToggle`.
    * La interfaz permite ver una lista de los 13 eventos de notificación.
    * Permite a los administradores **activar o desactivar (`is_email_enabled`) el envío de correos electrónicos para cada evento individualmente** directamente desde la vista de lista, para una gestión rápida y sin necesidad de cambios en el código.
	
---
## 13. Configuración del Entorno de Desarrollo

Para configurar el proyecto en un entorno de desarrollo local, sigue estos pasos:

1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd requests_webpage
    ```

2.  **Crear y Activar un Entorno Virtual:**
    Es una práctica recomendada aislar las dependencias del proyecto.
    ```bash
    # Crear el entorno virtual
    python -m venv .venv

    # Activar en Windows
    .\.venv\Scripts\activate

    # Activar en macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instalar Dependencias:**
    Instala todas las librerías de Python necesarias.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno (`.env`):**
    Crea un archivo llamado `.env` en la raíz del proyecto (junto a `manage.py`). Este archivo no se sube al repositorio Git y contiene las credenciales y configuraciones sensibles. Debe contener las siguientes variables:
    ```dotenv
    # Django Core Settings
    DJANGO_SECRET_KEY="tu_clave_secreta_aqui_muy_larga_y_aleatoria"
    DJANGO_DEBUG=True
    DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
    SITE_DOMAIN="[http://127.0.0.1:8000](http://127.0.0.1:8000)"

    # Database (para desarrollo local con SQLite)
    DATABASE_URL="sqlite:///db.sqlite3"

    # Salesforce Credentials
    SF_USERNAME="tu_usuario_sf@dominio.com"
    SF_PASSWORD="tu_password_sf"
    SF_SECURITY_TOKEN="tu_token_de_seguridad_sf"
    SF_CONSUMER_KEY="tu_consumer_key_sf"
    SF_CONSUMER_SECRET="tu_consumer_secret_sf"
    SF_INSTANCE_NAME="sayrhino" # O el nombre de tu instancia

    # SendGrid Email Settings
    EMAIL_HOST="smtp.sendgrid.net"
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER="apikey"
    EMAIL_HOST_PASSWORD="tu_api_key_de_sendgrid"
    DEFAULT_FROM_EMAIL="tu_email_verificado@dominio.com"

    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN="el_token_de_tu_bot_de_telegram"
    TELEGRAM_DEFAULT_CHAT_ID="tu_chat_id_para_pruebas"

    # AWS S3 Settings (Opcional para desarrollo local, pero necesario para probar S3)
    # Si DEBUG=True, estos no se usarán por defecto, pero es bueno tenerlos para pruebas.
    AWS_ACCESS_KEY_ID="tu_aws_access_key"
    AWS_SECRET_ACCESS_KEY="tu_aws_secret_key"
    AWS_STORAGE_BUCKET_NAME="tu-nombre-de-bucket-s3"
    AWS_S3_REGION_NAME="tu-region-de-aws" # ej. us-east-1
    AWS_DEFAULT_ACL="public-read"
    ```

5.  **Aplicar Migraciones:**
    Crea la estructura de la base de datos.
    ```bash
    python manage.py migrate
    ```

6.  **Crear un Superusuario:**
    Crea una cuenta de administrador para acceder al panel de admin de Django.
    ```bash
    python manage.py createsuperuser
    ```

7.  **Ejecutar los Servidores:**
    Necesitas dos terminales separadas, ambas con el entorno virtual activado.
    * **En la Terminal 1 (Servidor de Desarrollo):**
      ```bash
      python manage.py runserver
      ```
    * **En la Terminal 2 (Cluster de Tareas Asíncronas):**
      ```bash
      python manage.py qcluster
      ```
    El `qcluster` es esencial para que las notificaciones, la sincronización con Salesforce y las tareas programadas se procesen.

---
## 14. Despliegue (Heroku)

La aplicación está configurada para ser desplegable en Heroku.

* **`Procfile`**: Necesario para Heroku. Debe contener al menos:
    ```
    release: python manage.py migrate
    web: gunicorn requests_webpage.wsgi --log-file -
    worker: python manage.py qcluster
    ```
    * `release`: Ejecuta las migraciones en cada despliegue.
    * `web`: Inicia el servidor web `gunicorn` para atender las solicitudes HTTP.
    * `worker`: Inicia el cluster de `django-q2` en un dyno separado para procesar tareas en segundo plano.

* **`runtime.txt`**: Especifica la versión de Python a usar (ej. `python-3.12.10`).

* **Dependencias (`requirements.txt`):** Asegúrate de que incluya `gunicorn` y `psycopg2-binary` (para PostgreSQL).

* **Variables de Entorno en Heroku (Config Vars)**: Todas las variables del archivo `.env` deben configurarse en el panel de Heroku (Settings > Config Vars). Esto es crucial.
    * `DJANGO_DEBUG` debe ser `False`.
    * `DJANGO_SECRET_KEY` debe ser una clave segura y única para producción.
    * `DATABASE_URL` será proporcionado automáticamente por el add-on Heroku Postgres.
    * `SITE_DOMAIN` debe ser la URL de tu aplicación en Heroku (ej. `https://tu-app.herokuapp.com`).
    * Todas las credenciales de **Salesforce**, **SendGrid**, **Telegram** y **AWS S3** deben estar configuradas.

* **Buildpacks**: Se necesitará el buildpack de Python (`heroku/python`).

* **Add-ons**:
    * **Heroku Postgres**: Para la base de datos.
    * **Heroku Redis**: Una opción común como "message broker" para `django-q2` en producción.

* **Permisos del Bucket S3:** Como se decidió que los archivos sean públicos, asegúrate de que la configuración de tu bucket S3 en la consola de AWS permita la lectura pública. Esto usualmente implica desactivar la opción "Block all public access" y añadir una política de bucket que permita la acción `s3:GetObject`.

---
## 15. Consideraciones Adicionales y Próximos Pasos

* **Pruebas Exhaustivas:** Continuar con pruebas de regresión y de nuevas funcionalidades, incluyendo todos los flujos de notificación, la activación/desactivación de correos desde el admin, la funcionalidad de "Unassign" y la correcta aplicación de descuentos en el reporte de costos.
* **Gestión Avanzada de Destinatarios de Notificación:**
    * Implementar una interfaz para que los usuarios (o administradores) definan sus preferencias de notificación (qué eventos recibir y por qué canal).
    * Añadir un campo `telegram_chat_id` al modelo `CustomUser` y lógica para que los usuarios lo puedan registrar/actualizar de forma segura.
    * Permitir la configuración de listas de correo o `chat_id` de grupos de Telegram para equipos específicos (ej. notificar a todo el "QA Team" cuando una solicitud se envía a QA).
* **Toggle para Notificaciones de Telegram:** Considerar añadir `is_telegram_enabled` a `NotificationToggle` para un control similar sobre los mensajes de Telegram.
* **Refinar la Lógica de Descuentos:** Considerar si se necesitan más controles sobre los descuentos, como registrar quién lo aplicó y la fecha, o limitar el porcentaje máximo por tipo de solicitud.
* **Optimización de Almacenamiento y Entrega:** Para una aplicación de producción de alto tráfico, considerar el uso de un CDN (Content Delivery Network) como Amazon CloudFront delante de tu bucket S3 para una entrega más rápida y económica de los archivos.
* **Refactorización de `apps.py`:** Para una inicialización aún más robusta, la lógica de creación de `Schedule` y `NotificationToggle` en el método `ready()` podría moverse a una función conectada a la señal `post_migrate` de Django.
* **Seguridad:** Realizar revisiones de seguridad periódicas, especialmente en cuanto al manejo de credenciales, permisos, y la interacción con APIs externas.
* **Autenticación de Dominio para SendGrid:** Una vez que se disponga de un dominio propio para producción, configurar la "Autenticación de Dominio" (SPF, DKIM) en SendGrid para mejorar significativamente la entregabilidad de los correos y la reputación del remitente.
* **Documentación para Usuarios Finales:** Desarrollar guías detalladas para los diferentes roles de usuario sobre cómo utilizar todas las funcionalidades de la plataforma.