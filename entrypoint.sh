#!/bin/sh

wait-for-it.sh $DATABASE_HOST:$DATABASE_PORT --timeout=120
aerich migrate

exec "$@"
