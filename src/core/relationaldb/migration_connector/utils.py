from asyncpg import Pool

CREATE_HYPERTABLE_SQL = """
DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables
        WHERE hypertable_name = 'event'
    ) THEN
        PERFORM create_hypertable('event', 'opened_at', if_not_exists => TRUE);
    END IF;
END
$$;
"""

async def ensure_hypertables(conn_pool: Pool):
    async with conn_pool.acquire() as conn:
        await conn.execute(CREATE_HYPERTABLE_SQL)
