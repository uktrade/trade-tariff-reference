#!/bin/bash

UK_FILE=./sql/tariff_uk.backup
if [ -f "$UK_FILE" ]; then
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h trade_application_db -U postgres -c 'DROP DATABASE tariff_uk' || true
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h trade_application_db -U postgres -c 'CREATE DATABASE tariff_uk'
    PGPASSWORD=${POSTGRES_PASSWORD} pg_restore -h trade_application_db -U postgres -d tariff_uk -c $UK_FILE || true
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h trade_application_db -U postgres -d tariff_uk  -c 'drop event trigger reassign_owned' || true
else
    echo "The sql file [$UK_FILE] for the UK database does not exist"
fi
