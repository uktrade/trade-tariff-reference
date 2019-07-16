from .development import *

MANAGE_TARIFF_DATABASE = True

DATABASES['tariff']['HOST'] = os.environ.get('POSTGRES_HOST')
