from .base import *

import dj_database_url


VCAP_SERVICES = env('VCAP_SERVICES')

DEFAULT_DATABASE_URL = VCAP_SERVICES['postgres'][0]['credentials']['url']
TARIFF_DATABASE_URL = VCAP_SERVICES['postgres'][1]['credentials']['url']

REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['url']


DATABASES = {
    'default': dj_database_url.config(env=DEFAULT_DATABASE_URL, engine='django.db.backends.postgresql'),
    'tariff': dj_database_url.config(env=TARIFF_DATABASE_URL, engine='django.db.backends.postgresql'),
}


CELERY_BROKER_URL = f'{REDIS_URL}/{CELERY_REDIS_INDEX}'
