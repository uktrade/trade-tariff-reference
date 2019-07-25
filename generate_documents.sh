#!/usr/bin/env bash

./setup.sh skipsuperuser
python manage.py create_all_fta_documents --force
./compile_assets.sh