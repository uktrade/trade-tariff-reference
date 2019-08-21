#!/bin/bash -xe

if [ -z "$1" ]; then
    python manage.py createsuperuser
fi

python manage.py loaddata agreement extendedquotas latin_terms special_notes seasonalquota seasonalquotaseasons
python manage.py create_all_fta_documents --force --background
