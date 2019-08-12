web: python manage.py migrate --noinput && python manage.py migrate --database tariff --noinput && waitress-serve --port=$PORT config.wsgi:application
worker: celery worker -A config -l info -Q celery
