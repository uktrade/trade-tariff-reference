web: bash start_cf.sh
worker: celery worker -A config -l info -Q celery
celerybeat: celery beat -A config -l info
