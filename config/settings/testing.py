from .local import *

MANAGE_TARIFF_DATABASE = True

DATABASES['tariff']['HOST'] = env('POSTGRES_HOST')

WHITENOISE_AUTOREFRESH = True

DEBUG = False

STATIC_ROOT = '/app/test_assets'

GENERATED_DOCUMENT_LOCATION = '/app/test_assets/tariff/documents'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# authbroker config
AUTHBROKER_URL = 'http://localhost'
AUTHBROKER_CLIENT_ID = ''
AUTHBROKER_CLIENT_SECRET = ''

AWS_STORAGE_BUCKET_NAME = 'fake-bucket'
AWS_SECRET_ACCESS_KEY = 'fake-secret'
AWS_ACCESS_KEY_ID = 'fake-key'
