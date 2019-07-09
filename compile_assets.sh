#!/usr/bin/env bash


python manage.py compilescss --delete-files
python manage.py compilescss
python manage.py collectstatic --ignore=*.scss --ignore=*.sass
python manage.py compilescss --delete-files

