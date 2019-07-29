#!/bin/bash -xe

python manage.py migrate

if [ -z "$1" ]; then
    python manage.py createsuperuser
fi

python manage.py loaddata agreement extendedquotas
