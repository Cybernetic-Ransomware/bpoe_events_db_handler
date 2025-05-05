from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.conf_logger import setup_logger
from src.config.config import DEBUG, MONGO_COLLECTION, MONGO_DB
from src.core.documentstorage.utils import MongoAsynchConnector
from src.core.relationaldb.psycopg2_con.utils import AsyncPGConnector

logger = setup_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    print(f"{DEBUG=}", flush=True)

    try:
        connector = MongoAsynchConnector(mongo_db=MONGO_DB, mongo_collection=MONGO_COLLECTION)
        await connector._perform_startup_checks()
        app.state.mongo_connector = connector

    except Exception as e:
        logger.critical(f"Failed to initialize MongoDB connector during startup: {e}", exc_info=True)
        raise RuntimeError("Application startup failed due to MongoDB connector initialization error.") from e

    try:
        pgpool = AsyncPGConnector()
        await pgpool.connect()
        app.state.postgres_pool = pgpool
    except Exception as e:
        logger.critical(f"Failed to initialize Postgres connector during startup: {e}", exc_info=True)
        raise RuntimeError("Application startup failed due to Postgres connector initialization error.") from e

    else:
        logger.info(f"Started with {DEBUG=}")
    yield  # Separates code before the application starts and after it stops
    try:
        await app.state.postgres_pool.close_postgres()
    except Exception as e:
        logger.critical(f"Failed to close postgres connection: {e}", exc_info=True)
    logger.info("Application shutdown...")
