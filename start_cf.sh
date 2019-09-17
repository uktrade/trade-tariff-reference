#!/bin/bash

source ./functions.sh

run "./compile_assets.sh"
run "python manage.py migrate --noinput"
run "python manage.py migrate --database tariff --noinput"


if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    waitress-serve --port=$PORT config.wsgi:application
fi