from fastapi import Request

from src.api.exceptions import ServerInitError
from src.core.documentstorage.utils import MongoAsynchConnector
from src.core.relationaldb.psycopg2_con.utils import AsyncPGConnector


async def get_mongo_connector(request: Request) -> MongoAsynchConnector:
    if not hasattr(request.app.state, "mongo_connector"):
        raise ServerInitError(message="Internal server error: MongoDB connector not available")

    connector_instance = request.app.state.mongo_connector

    if not isinstance(connector_instance, MongoAsynchConnector):
        raise ServerInitError(message="Internal server error: Invalid DB connector type")

    return connector_instance


async def get_pg_connector(request: Request):
    if not hasattr(request.app.state, "postgres_pool_connector"):
        raise ServerInitError(message="Internal server error: PostgreSQL connector not available")

    connector = request.app.state.postgres_pool_connector

    if not isinstance(connector, AsyncPGConnector):
        raise ServerInitError(message="Internal server error: Invalid PostgreSQL DB connector type")

    pool = connector.get_pool()
    async with pool.acquire() as conn:
        yield conn
