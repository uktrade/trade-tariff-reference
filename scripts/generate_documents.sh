#!/bin/bash

source ./scripts/functions.sh

run "python manage.py create_all_fta_documents --force"
run "python manage.py create_mfn_document classification --force"
run "python manage.py create_mfn_document schedule --force"