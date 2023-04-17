#!/bin/sh
HERE=$(dirname $0)
source "${HERE}/prettify.sh"

info 'Waiting for redis to start...'
${PROJECT_DIR}/scripts/wait-for.sh redis:6379 -t 60 -- echo 'Redis is up'

info "Generating .pot file for translations..."
xgettext -k_ -o ${PROJECT_DIR}/translations/prompts.pot ${PROJECT_DIR}/src/prompts/*.py

info "Starting Python application..."
python ${PROJECT_DIR}/src/app.py