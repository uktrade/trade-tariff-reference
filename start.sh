#!/bin/bash -xe

pip install --no-cache-dir -r requirements.txt
./compile_assets.sh
python manage.py migrate --noinput

if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    waitress-serve --port=8000 config.wsgi:application
else
    sleep infinity
fi
