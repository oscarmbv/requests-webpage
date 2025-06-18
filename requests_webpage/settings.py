from pathlib import Path
import os
import environ
import dj_database_url
import sentry_sdk

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    SF_VERSION=(str, '59.0') # Default para la versión de API de Salesforce
)

SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Activa el monitoreo de rendimiento para identificar cuellos de botella.
        enable_tracing=True,
    )

ENV_PATH = os.path.join(BASE_DIR, '.env')
if os.path.exists(ENV_PATH):
    environ.Env.read_env(ENV_PATH)

LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Configuracion base de formatters
LOGGING_FORMATTERS = {
    'verbose': {
        'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
        'style': '{',
    },
    'simple': {
        'format': '{levelname} {message}',
        'style': '{',
    },
    'qcluster': {
        'format': '{levelname} {asctime} {module} {message}',
        'style': '{',
    }
}

# Configuracion base de handlers
LOGGING_HANDLERS = {
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
    # Se añadira el 'file_tasks' handler condicionalmente abajo
}

# Configuracion base de loggers
LOGGING_LOGGERS = {
    'django': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    },
    'django.request': {
        'handlers': ['console'],
        'level': 'ERROR',
        'propagate': False,
    },
    'tasks': {
        'handlers': ['console'], # Por defecto, solo consola
        'level': env('DJANGO_LOG_LEVEL_TASKS', default='INFO'),
        'propagate': False,
    },
    'django_q': {
        'handlers': ['console'], # Por defecto, solo consola
        'level': 'INFO',
        'propagate': False,
    },
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='una_key_por_defecto_muy_segura_si_no_esta_en_env_y_no_deberia_usarse_en_produccion')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DJANGO_DEBUG')

# Obtiene el nombre de la app desde la variable de entorno que Fly.io provee automáticamente
FLY_APP_NAME = env('FLY_APP_NAME', default='localhost')
CUSTOM_DOMAIN = env.str('CUSTOM_DOMAIN', default=None)

# Define los hosts permitidos.
# Añadimos el dominio de fly.dev, y también los de desarrollo local.
ALLOWED_HOSTS = [f"{FLY_APP_NAME}.fly.dev", 'localhost', '127.0.0.1']
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)
CSRF_TRUSTED_ORIGINS = [f"https://{FLY_APP_NAME}.fly.dev"]
if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{CUSTOM_DOMAIN}")

LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/rhino/dashboard/'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'storages',
    'tasks',
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

AUTH_USER_MODEL = 'tasks.CustomUser'

ROOT_URLCONF = 'requests_webpage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tasks.context_processors.user_role_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'requests_webpage.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}')
}

# Seguridad extra para producción
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    # --- CONFIGURACIÓN PARA DESARROLLO LOCAL ---
    # Usa el sistema de archivos de Django por defecto para guardar archivos subidos.
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    # URL base desde donde se servirán los archivos multimedia en desarrollo.
    MEDIA_URL = '/media/'

    # Directorio en tu PC donde se guardarán los archivos subidos durante el desarrollo.
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

else:
    # --- NUEVA CONFIGURACIÓN PARA PRODUCCIÓN (Cloudflare R2) ---

    # django-storages usa estas variables estándar de AWS, pero las apuntaremos a R2.
    AWS_ACCESS_KEY_ID = env('CLOUDFLARE_R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('CLOUDFLARE_R2_BUCKET_NAME')

    # Esta es la URL del endpoint de R2. La construiremos a partir de tu Account ID.
    # Ejemplo: https://<TU_ACCOUNT_ID>.r2.cloudflarestorage.com
    AWS_S3_ENDPOINT_URL = env('CLOUDFLARE_R2_ENDPOINT_URL')

    # Configuraciones adicionales para asegurar la compatibilidad
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None  # R2 no usa ACLs como S3, es mejor dejarlo en None.
    AWS_S3_VERIFY = True

    # Definimos la ubicación de los archivos de medios (subidos por usuarios) y estáticos.
    PUBLIC_MEDIA_LOCATION = 'media'
    STATIC_LOCATION = 'static'

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "location": PUBLIC_MEDIA_LOCATION,
                "file_overwrite": AWS_S3_FILE_OVERWRITE,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "location": STATIC_LOCATION,
            },
        },
    }

# Usar esta configuración base para LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': LOGGING_FORMATTERS,
    'handlers': LOGGING_HANDLERS,
    'loggers': LOGGING_LOGGERS,
}

if DEBUG:
    # 1. Asegurarse de que el directorio de logs exista localmente
    os.makedirs(LOG_DIR, exist_ok=True)

    # 2. Añadir el handler para archivos de log
    LOGGING['handlers']['file_tasks'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': os.path.join(LOG_DIR, 'tasks_app.log'),
        'formatter': 'verbose',
    }

    # 3. Hacer que el logger de la app 'tasks' también escriba al archivo
    LOGGING['loggers']['tasks']['handlers'].append('file_tasks')
    # Podrías hacer lo mismo para 'django_q' si quieres sus logs en un archivo
    # LOGGING['loggers']['django_q']['handlers'].append('file_tasks')

Q_CLUSTER = {
    'name': 'RequestWebpageScheduler_Heroku',
    'workers': env.int('DJANGO_Q_WORKERS', default=2),
    'timeout': 180,
    'retry': 200,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
    'catch_up': False,
    'log_level': env('DJANGO_Q_LOG_LEVEL', default='INFO'),
}

#Telegram Bot Settings
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default=None)
TELEGRAM_DEFAULT_CHAT_ID = env('TELEGRAM_DEFAULT_CHAT_ID', default=None)

#Email (SendGrid) Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

SITE_DOMAIN = env('SITE_DOMAIN', default='http://localhost:8000')

# --- Credenciales y Configuraciones de Salesforce ---
SF_USERNAME = env('SF_USERNAME', default=None)
SF_PASSWORD = env('SF_PASSWORD', default=None)
SF_SECURITY_TOKEN = env('SF_SECURITY_TOKEN', default=None)
SF_CONSUMER_KEY = env('SF_CONSUMER_KEY', default=None)
SF_CONSUMER_SECRET = env('SF_CONSUMER_SECRET', default=None)
SF_DOMAIN = env('SF_DOMAIN', default='login')
SF_VERSION = env('SF_VERSION')
SF_INSTANCE_NAME = env('SF_INSTANCE_NAME', default='sayrhino')
SALESFORCE_LIGHTNING_BASE_URL = f"https://{SF_INSTANCE_NAME}.lightning.force.com/lightning/r"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = env.bool('DJANGO_SESSION_COOKIE_SECURE', default=True)
    CSRF_COOKIE_SECURE = env.bool('DJANGO_CSRF_COOKIE_SECURE', default=True)
    SECURE_HSTS_SECONDS = env.int('DJANGO_SECURE_HSTS_SECONDS', default=31536000) # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
    SECURE_HSTS_PRELOAD = env.bool('DJANGO_SECURE_HSTS_PRELOAD', default=True)