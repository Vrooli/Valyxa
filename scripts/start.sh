#!/bin/sh
HERE=`dirname $0`
. "${HERE}/prettify.sh"

info 'Waiting for redis to start...'
${PROJECT_DIR}/scripts/wait-for.sh redis:6379 -t 60 -- echo 'Redis is up'
pip freeze
info "Starting Python application..."
exec gunicorn -b :${VIRTUAL_PORT} -w 1 -t 60 src.app:app
