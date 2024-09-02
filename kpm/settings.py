import os
import sys
from pathlib import Path
import dotenv
import psycopg2
from datetime import timedelta
import logging

PROJECT_ROOT = os.path.dirname(__file__)
DOTENV_PATH = os.path.join(PROJECT_ROOT, '../.env')

dotenv.load_dotenv(DOTENV_PATH)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'apps'))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG") == 'TRUE'
UNIVERSAL = os.environ.get("UNIVERSAL_PASSWORD")

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'works.apps.WorksConfig',
    'themes.apps.ThemesConfig',
    'grades.apps.GradesConfig',
    'messages.apps.MessagesConfig',
    'stats.apps.StatsConfig',
    'ratings.apps.RatingsConfig',
    'groups.apps.GroupsConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework',
    'drf_yasg',
    'whitenoise',
    'django_celery_beat',
    'django_celery_results',
    'storages'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kpm.urls'

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'kpm.wsgi.application'

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_USER_PASSWORD = os.environ.get("DB_USER_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_USER_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TIME_ZONE': 'Europe/Moscow',
    }
}

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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

ACCESS_TOKEN_LIFETIME = timedelta(minutes=1) if DEBUG else timedelta(minutes=60)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': ACCESS_TOKEN_LIFETIME,
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY + 'jwtoken',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('kpm',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

LOGIN_URL = '/api/user/login'

SWAGGER_SETTINGS = {
    'DEFAULT_MODEL_RENDERING': 'example',
    'SECURITY_DEFINITIONS': {
            'api_key': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            }
        },
}

MEDIA_HOST_PATH = f'{os.environ.get("S3_DOMAIN")}/{os.environ.get("AWS_STORAGE_BUCKET_NAME")}/media'

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            'access_key': os.environ.get("AWS_ACCESS_KEY_ID"),
            'secret_key': os.environ.get("AWS_SECRET_ACCESS_KEY"),
            'bucket_name': os.environ.get("AWS_STORAGE_BUCKET_NAME"),
            'default_acl': 'public-read',
            'object_parameters': {
                'CacheControl': 'max-age=86400',
            },
            'location': 'media/',
            'endpoint_url': os.environ.get("S3_DOMAIN"),
            'region_name': 'ru-1',
        },
    },
    'staticfiles': {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            'access_key': os.environ.get("AWS_ACCESS_KEY_ID"),
            'secret_key': os.environ.get("AWS_SECRET_ACCESS_KEY"),
            'bucket_name': os.environ.get("AWS_STORAGE_BUCKET_NAME"),
            'default_acl': 'public-read',
            'object_parameters': {
                'CacheControl': 'max-age=86400',
            },
            'endpoint_url': os.environ.get("S3_DOMAIN"),
            'location': 'static/',
            'region_name': 'ru-1'
        }
    }
}

STATIC_URL = 'static/'

MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'users.User'

DEFAULT_CHARSET = 'utf-8'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
CELERY_CACHE_BACKEND = "default"
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,
}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

LOGGER = logging.getLogger('log')
LOGGER.setLevel(logging.INFO)
LOGFILE = os.environ.get('LOGFILE')
file_handler = logging.FileHandler(LOGFILE)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)

TG_SUPPORT_CHAT = os.environ.get("TG_SUPPORT_CHAT")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")