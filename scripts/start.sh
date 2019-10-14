#!/bin/bash

source ./scripts/functions.sh

run "pipenv lock"
run "pipenv --rm"
run "pipenv install --dev --system"

if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    export PORT=8000
fi

run "./scripts/start_cf.sh"

if [[ -z "${DEVELOPMENT_SERVER}" ]];
then
    :
else
    run "sleep infinity"
fi
