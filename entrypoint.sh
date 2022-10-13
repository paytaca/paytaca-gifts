#!/bin/sh

wait-for-it.sh $DATABASE_HOST:$DATABASE_PORT --timeout=60

exec "$@"
