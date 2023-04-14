#!/bin/sh

wait-for-it.sh $DATABASE_HOST:$DATABASE_PORT --timeout=30
aerich migrate

exec "$@"
