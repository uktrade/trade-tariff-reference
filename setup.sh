#!/bin/bash -xe

python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata agreement quotabalance
