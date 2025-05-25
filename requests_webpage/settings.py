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
else:
    pass


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='una_key_por_defecto_muy_segura_si_no_esta_en_env_y_no_deberia_usarse_en_produccion')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DJANGO_DEBUG')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']

LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/portal/dashboard/'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tasks',
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}'
    )
}

# Seguridad extra para producción
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
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

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Mantener los loggers por defecto de Django
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'qcluster': { # Formato específico para qcluster si quieres diferenciarlo
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG', # Nivel mínimo para el handler de consola
            'class': 'logging.StreamHandler', # Envía a stderr (consola)
            'formatter': 'verbose', # Usa el formato 'verbose'
        },
        # Puedes añadir un handler de archivo si quieres guardar logs en un archivo:
    'file_tasks': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'logs/tasks_app.log', # Asegúrate que la carpeta 'logs' exista
        'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': { # Configuración para los loggers internos de Django
            'handlers': ['console'],
            'level': 'INFO', # No mostrar DEBUG de Django a menos que sea necesario
            'propagate': True,
        },
        'django.request': { # Específico para errores de request/response
            'handlers': ['console'], # O un handler de mail para errores 500 en producción
            'level': 'ERROR',
            'propagate': False,
        },
        'tasks': { # Logger para tu aplicación 'tasks' completa
            'handlers': ['console'], # , 'file_tasks' si habilitas el handler de archivo
            'level': 'DEBUG',     # <--- MUESTRA DEBUG, INFO, WARNING, ERROR, CRITICAL de tu app
            'propagate': False,   # No propagar a loggers padres si ya lo manejaste aquí
        },
        'django_q': { # Logger específico para Django-Q
            'handlers': ['console'],
            'level': 'INFO', # Coincide con tu Q_CLUSTER['log_level']
            'propagate': False,
        },
        # Puedes añadir loggers más específicos si es necesario:
        # 'tasks.salesforce_sync': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
    },
    # Opcional: Configurar el logger raíz como un "catch-all"
    # 'root': {
    #     'handlers': ['console'],
    #     'level': 'WARNING', # No ser demasiado verboso con el raíz por defecto
    # },
}

Q_CLUSTER = {
    'name': 'RequestWebpageScheduler_Q2',
    'workers': 2,
    'timeout': 180,
    'retry': 200,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
    'catch_up': False,
    'log_level': 'INFO',
}

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