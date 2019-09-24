#!/bin/bash

source ./scripts/functions.sh

run "./scripts/compile_assets.sh"
run "python manage.py migrate --noinput"
run "python manage.py migrate --database tariff --noinput"


if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    waitress-serve --port=$PORT config.wsgi:application
fi