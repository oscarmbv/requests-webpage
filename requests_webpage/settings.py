from pathlib import Path
import os
import environ
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    SF_VERSION=(str, '59.0') # Default para la versión de API de Salesforce
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

ALLOWED_HOSTS_STRING = env('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost')
ALLOWED_HOSTS = ALLOWED_HOSTS_STRING.split(',') + ['.herokuapp.com']

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
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=env('DJANGO_DB_SSL_REQUIRE', cast=bool, default=False), # SSL para DB en Heroku
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}' # [cite: 13]
    )
}

if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# Seguridad extra para producción
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
    # --- CONFIGURACIÓN PARA PRODUCCIÓN (Amazon S3) ---
    # Usa el backend de S3 de django-storages para todos los FileField.
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # Credenciales y configuración de S3 cargadas desde variables de entorno.
    # Asegúrate de configurar estas variables en Heroku (Settings -> Config Vars).
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default=None)
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default=None)
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default=None)  # ej: 'us-east-1'

    # (Opcional) Un subdirectorio dentro de tu bucket para organizar los archivos.
    AWS_LOCATION = env('AWS_S3_LOCATION_MEDIA', default='media')

    # Construcción de la URL pública para tus archivos.
    # Esta es la URL base que Django usará para generar el atributo .url de tus FileField.
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{AWS_LOCATION}/'

    # (Opcional) Política de acceso por defecto para nuevos archivos subidos.
    # 'public-read' es común si los archivos deben ser visibles públicamente en tu web.
    AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL', default='public-read')

    # (Opcional) Otros parámetros que quieras añadir a los archivos subidos a S3.
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # Cache por 1 día en el navegador del cliente.
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
    # Configura CSRF_TRUSTED_ORIGINS con tu dominio de Heroku en las variables de entorno
    # DJANGO_CSRF_TRUSTED_ORIGINS=https://tu-app.herokuapp.com,https://www.tudominio.com
    CSRF_TRUSTED_ORIGINS_STRING = env('DJANGO_CSRF_TRUSTED_ORIGINS', default='')
    if CSRF_TRUSTED_ORIGINS_STRING:
        CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS_STRING.split(',')