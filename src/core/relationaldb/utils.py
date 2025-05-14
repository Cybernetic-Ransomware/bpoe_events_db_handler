from core.relationaldb.psycopg2_con.utils import get_pg_connector


def get_db_via_psycopg2_connector():
    connector = get_pg_connector(mode="sync")
    connector.connect()
    with connector.get_cursor() as cursor:
        yield cursor

async def get_db_via_asyncpg_connector():
    connector = get_pg_connector(mode="async")
    await connector.connect()
    async with connector.get_connection() as conn:
        yield conn
