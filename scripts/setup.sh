#!/bin/bash

source ./scripts/functions.sh

if [ -z "$1" ]; then
    run "python manage.py createsuperuser"
fi

run "python manage.py loaddata agreement extendedquotas latin_terms special_notes chapters chapter_notes"
run "python manage.py create_all_fta_documents --force"
run "python manage.py create_mfn_document classification --force"
run "python manage.py create_mfn_document schedule --force"
