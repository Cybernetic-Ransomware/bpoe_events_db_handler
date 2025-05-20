#!/bin/sh

echo "Generating initial Alembic migration..."
cd core/relationaldb/migration_alembic/

if [ ! -d "migrations/versions" ]; then
    mkdir -p migrations/versions
fi

if [ -z "$(find migrations/versions -maxdepth 1 -type f -name '*.py')" ]; then
    echo "Versions folder is empty. Creating initial migration..."
    alembic revision --autogenerate -m "initial"
else
    echo "Migration already exists. Skipping initial generation."
fi

echo "Applying Alembic migrations..."
alembic upgrade head

echo "Database initialized and migrations applied successfully."
cd /src

exec "$@"
