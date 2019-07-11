from .base import *

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DATABASE', 'default'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
    },
    'tariff': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_TARIFF_DATABASE', 'tariff'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
    }
}


DATABASE_ROUTERS = [
    'trade_tariff_reference.core.router.Router',
]

SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_AUTO_INCLUDE = True

SASS_OUTPUT_STYLE = 'nested'
