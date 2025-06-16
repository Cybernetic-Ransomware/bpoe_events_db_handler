from asyncpg import Pool

CREATE_HYPERTABLE_SQL = """
DO
$$
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
"""

async def ensure_hypertables(conn_pool: Pool):
    async with conn_pool.acquire() as conn:
        await conn.execute(CREATE_HYPERTABLE_SQL)
