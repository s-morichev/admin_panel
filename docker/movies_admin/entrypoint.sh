#!/bin/bash
set -e

echo "Waiting for PosgreSQL"
/opt/wait-for postgres:5432 --timeout=0 -- echo "PostgreSQL is up"

source /opt/pysetup/.venv/bin/activate

exec "$@"