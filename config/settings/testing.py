from .development import *

MANAGE_TARIFF_DATABASE = True

DATABASES['tariff']['HOST'] = env('POSTGRES_HOST')
