#!/bin/sh

echo "Generating initial Alembic migration..."
cd core/relationaldb/migration_alembic/

if [ ! -d "migrations/versions" ]; then
    mkdir -p migrations/versions
fi

alembic revision --autogenerate -m "initial"

echo "Applying Alembic migrations..."
alembic upgrade head

echo "Database initialized and migrations applied successfully."
cd /src

exec "$@"
