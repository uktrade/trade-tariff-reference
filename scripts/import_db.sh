#!/bin/bash

UK_FILE=./sql/tariff_uk.sql
if [ -f "$UK_FILE" ]; then
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U postgres -c 'DROP DATABASE tariff_uk' || true
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U postgres -c 'CREATE DATABASE tariff_uk'
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U postgres tariff_uk < $UK_FILE
else
    echo "The sql file [$UK_FILE] for the UK database does not exist"
fi

EU_FILE=./sql/tariff_eu.sql
if [ -f "$EU_FILE" ]; then
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U postgres -c 'DROP DATABASE tariff_eu' || true
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U postgres -c 'CREATE DATABASE tariff_eu'
    PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U postgres tariff_eu < $EU_FILE
else
    echo "The sql file [$EU_FILE] for the EU database does not exist"
fi
