from .base import *

DEBUG = env.bool('DEBUG')

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
    },
    'tariff': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('UK_TARIFF_DB'),
        'USER': env('UK_TARIFF_USER'),
        'PASSWORD': env('UK_TARIFF_PASSWORD'),
        'HOST': env('UK_TARIFF_HOST'),
    }
}

SASS_OUTPUT_STYLE = 'nested'
