#!/bin/bash -xe

./compile_assets.sh
python manage.py migrate --noinput
python manage.py migrate --database tariff --noinput

if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    waitress-serve --port=$PORT config.wsgi:application
fi