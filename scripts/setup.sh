#!/bin/bash

source ./scripts/functions.sh

if [ -z "$1" ]; then
    run "python manage.py createsuperuser"
fi

run "python manage.py loaddata agreement extendedquotas latin_terms special_notes chapters chapter_notes"
run "./scripts/generate_documents.sh"
