#!/bin/bash

source ./scripts/functions.sh

run "./scripts/setup.sh skipsuperuser"
run "python manage.py create_all_fta_documents --force"
run "./scritps/compile_assets.sh"