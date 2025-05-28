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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='una_key_por_defecto_muy_segura_si_no_esta_en_env_y_no_deberia_usarse_en_produccion')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DJANGO_DEBUG')

ALLOWED_HOSTS_STRING = env('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost')
ALLOWED_HOSTS = ALLOWED_HOSTS_STRING.split(',') + ['.herokuapp.com']

LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/portal/dashboard/'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
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

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
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
    },
    'handlers': {
        'console': {
            'level': 'INFO', # Nivel mínimo para el handler de consola
            'class': 'logging.StreamHandler', # Envía a stderr (consola)
            'formatter': 'verbose', # Usa el formato 'verbose'
        },
        # Puedes añadir un handler de archivo si quieres guardar logs en un archivo:
    'file_tasks': {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': os.path.join(LOG_DIR, 'tasks_app.log'),
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
        'tasks': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL_TASKS', default='INFO'),
            'propagate': False,
        },
        'django_q': { # Logger específico para Django-Q
            'handlers': ['console'],
            'level': 'INFO', # Coincide con tu Q_CLUSTER['log_level']
            'propagate': False,
        },
    },
}

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