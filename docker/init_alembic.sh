#!/bin/sh

set -e

echo "Generating initial Alembic migration..."
cd core/relationaldb/migration_alembic/

if [ ! -d "migrations/versions" ]; then
    mkdir -p migrations/versions
fi

alembic revision --autogenerate -m "initial"

echo "Applying Alembic migrations..."
alembic upgrade head

echo "Current directory: $(pwd)"
echo "Listing contents of /src/core/relationaldb/migration_alembic/migrations/versions/"
ls /src/core/relationaldb/migration_alembic/migrations/versions/

if [ ! -d "/src/core/relationaldb/migration_alembic/migrations/versions" ]; then
    mkdir -p /src/core/relationaldb/migration_alembic/migrations/versions
fi

LATEST_FILE=$(ls /src/core/relationaldb/migration_alembic/migrations/versions/*.py -t | head -n1)
echo "Latest migration file: $LATEST_FILE"

echo "Injecting TimescaleDB hypertable statement into $LATEST_FILE..."
cat <<'EOF' >> "$LATEST_FILE"

from alembic import op

def upgrade() -> None:
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM timescaledb_information.hypertables
            WHERE hypertable_name = 'eventtransaction'
        ) THEN
            PERFORM create_hypertable(
                'eventtransaction',
                'timestamp',
                chunk_time_interval => interval '7 days',
                if_not_exists => TRUE,
                migrate_data => TRUE
            );
        END IF;
    END
    $$;
    """)
EOF

echo "Database initialized and migrations applied successfully."
cd /src

exec "$@"
