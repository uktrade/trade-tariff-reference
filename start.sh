#!/bin/bash

source ./functions.sh

run "pip install --no-cache-dir -r requirements.txt"

if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    export PORT=8080
fi

run "./start_cf.sh"

if [[ -z "${DEVELOPMENT_SERVER}" ]];
then
    :
else
    sleep infinity
fi
