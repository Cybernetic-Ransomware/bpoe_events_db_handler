#!/bin/sh

echo "Running database migrations..."
alembic -c src/core/relationaldb/migration_connector/alembic.ini upgrade head

if [ $? -ne 0 ]; then
    echo "Migrations failed. Exiting."
    exit 1
fi

echo "Migrations applied successfully."

exec "$@"