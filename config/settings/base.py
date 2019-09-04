"""
Django settings for trade_tariff_reference project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ

from django.urls import reverse_lazy
from datetime import datetime

from celery.schedules import crontab

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l_tl&(!%sb&077o#g70^h_61w6gr$b9%dpr+va=b%w=5q^0$r#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost').split(',')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'trade_tariff_reference.core',
    'trade_tariff_reference.schedule',
    'trade_tariff_reference.tariff',
    'trade_tariff_reference.documents',
    'trade_tariff_reference.api',
    'sass_processor',
    'authbroker_client',
]

MIDDLEWARE = [
    'trade_tariff_reference.core.middleware.TimezoneMiddleware',
    'trade_tariff_reference.core.middleware.HealthCheckMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'authbroker_client.middleware.ProtectAllViewsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authbroker_client.backends.AuthbrokerBackend',
]

LOGIN_URL = reverse_lazy('authbroker:login')

LOGIN_REDIRECT_URL = reverse_lazy('core:homepage')


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

ASSETS_FOLDER = os.path.join(BASE_DIR, 'assets')

STATIC_ROOT = ASSETS_FOLDER

STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    ('tariff', STATIC_FOLDER),
]

SASS_PROCESSOR_INCLUDE_DIRS = [
    STATIC_FOLDER,
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'


GENERATED_DOCUMENT_LOCATION = os.path.join(ASSETS_FOLDER, 'tariff/documents')


SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r'^.+\.scss$'

MANAGE_TARIFF_DATABASE = False

SASS_OUTPUT_STYLE = 'compressed'


TARIFF_MANAGEMENT_URL = env.url('TARIFF_MANAGEMENT_URL')

SCHEDULE = 'schedule'
CLASSIFICATION = 'classification'


CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)

CELERY_REDIS_INDEX = '1'

CELERY_BROKER_URL = f'redis://trade_application_redis:6379/{CELERY_REDIS_INDEX}'

CELERY_BEAT_SCHEDULE = {}

if env.bool('ENABLE_DAILY_REFRESH_OF_DOCUMENTS', False):
    CELERY_BEAT_SCHEDULE['refresh-fta-documents'] = {
        'task': 'trade_tariff_reference.documents.tasks.generate_all_fta_documents',
        'schedule': crontab(minute='3', hour='1'),
        'args': (False, False),
    }
    CELERY_BEAT_SCHEDULE['refresh-mfn-schedule-document'] = {
        'task': 'trade_tariff_reference.documents.tasks.generate_mfn_document',
        'schedule': crontab(minute='3', hour='2'),
        'args': (SCHEDULE, False),
    }
    CELERY_BEAT_SCHEDULE['refresh-mfn-classification-document'] = {
        'task': 'trade_tariff_reference.documents.tasks.generate_mfn_document',
        'schedule': crontab(minute='45', hour='2'),
        'args': (CLASSIFICATION, False),
    }

# authbroker config
AUTHBROKER_URL = env('AUTHBROKER_URL', default='http://localhost')
AUTHBROKER_CLIENT_ID = env('AUTHBROKER_CLIENT_ID')
AUTHBROKER_CLIENT_SECRET = env('AUTHBROKER_CLIENT_SECRET')

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
AWS_DEFAULT_ACL = None
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'eu-west-2'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] [%(name)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

DATABASE_ROUTERS = [
    'trade_tariff_reference.core.router.Router',
]

SASS_PROCESSOR_ENABLED = False
SASS_PROCESSOR_AUTO_INCLUDE = False

BREXIT_VALIDITY_START_DATE = datetime(2019, 3, 29, 0, 0, 0)  # datetime(2018, 1, 1, 0, 0, 0) - Date from database views
BREXIT_VALIDITY_END_DATE = datetime(2019, 12, 31, 0, 0, 0)

BREXIT_VALIDITY_START_DATE_STRING = BREXIT_VALIDITY_START_DATE.strftime("%Y-%m-%d")
BREXIT_VALIDITY_END_DATE_STRING = BREXIT_VALIDITY_END_DATE.strftime("%Y-%m-%d")
