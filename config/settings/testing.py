from .development import *

MANAGE_TARIFF_DATABASE = True

DATABASES['tariff']['HOST'] = env('POSTGRES_HOST')

WHITENOISE_AUTOREFRESH = True

DEBUG = False

STATIC_ROOT = '/app/test_assets'

GENERATED_DOCUMENT_LOCATION = '/app/test_assets/tariff/documents'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
