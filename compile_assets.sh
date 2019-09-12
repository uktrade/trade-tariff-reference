#!/bin/bash -xe

npm ci
npm run-script build
node -v
python manage.py compilescss --delete-files
python manage.py compilescss
python manage.py collectstatic --ignore=*.scss --ignore=*.sass --ignore=package.json --ignore=package-lock.json --noinput
