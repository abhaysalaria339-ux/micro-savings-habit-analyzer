#!/usr/bin/env sh
set -eu

if [ "$#" -eq 0 ]; then
    exec alembic upgrade head
fi

exec alembic "$@"
