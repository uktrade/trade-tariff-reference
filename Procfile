web: bash scripts/start_cf.sh
worker: celery worker -A config -l info  -O fair --prefetch-multiplier 1 -Q celery
celerybeat: celery beat -A config -l info
