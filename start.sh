#!/bin/bash

source ./functions.sh

run "pipenv lock"
run "pipenv --rm"
run "pipenv install --dev --system"

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
