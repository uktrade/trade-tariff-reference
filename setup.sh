#!/bin/bash -xe

python manage.py migrate
python manage.py createsuperuser
