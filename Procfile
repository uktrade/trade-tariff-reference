web: python manage.py migrate --noinput && waitress-serve --port=80 config.wsgi:application
celeryworker: celery worker -A config -l info -Q celery
