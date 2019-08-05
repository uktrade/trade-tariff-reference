from .base import *

import dj_database_url
import json


JSON_VCAP_SERVICES = env('VCAP_SERVICES')
VCAP_SERVICES = json.loads(JSON_VCAP_SERVICES)

DEFAULT_DATABASE_URL = VCAP_SERVICES['postgres'][0]['credentials']['uri']
TARIFF_DATABASE_URL = VCAP_SERVICES['postgres'][1]['credentials']['uri']

REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']


DATABASES = {
    'default': dj_database_url.parse(DEFAULT_DATABASE_URL),
    'tariff': dj_database_url.parse(TARIFF_DATABASE_URL)
}


CELERY_BROKER_URL = f'{REDIS_URL}/{CELERY_REDIS_INDEX}'
