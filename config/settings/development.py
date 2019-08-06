from .base import *

import dj_database_url


def sort_database_config(database_list):
    config = {}
    for database in database_list:
        config[database['name']] = database['credentials']['uri']
    return config


VCAP_SERVICES = env.json('VCAP_SERVICES')

VCAP_DATABASES = sort_database_config(VCAP_SERVICES['postgres'])

DEFAULT_DATABASE_URL = VCAP_DATABASES[env('POSTGRES_DB')]
TARIFF_DATABASE_URL = VCAP_DATABASES[env('UK_TARIFF_DB')]

REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']


DATABASES = {
    'default': dj_database_url.parse(DEFAULT_DATABASE_URL),
    'tariff': dj_database_url.parse(TARIFF_DATABASE_URL)
}


CELERY_BROKER_URL = f'{REDIS_URL}/{CELERY_REDIS_INDEX}'
