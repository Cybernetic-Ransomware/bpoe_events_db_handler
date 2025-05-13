from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI

from src.config.conf_logger import setup_logger
from src.config.config import DEBUG, MONGO_COLLECTION, MONGO_DB
from src.core.documentstorage.utils import MongoAsynchConnector

# from src.core.relationaldb.migration_connector.utils import ensure_hypertables
from src.core.relationaldb.psycopg2_con.utils import AsyncPGConnector, get_pg_connector

logger = setup_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")

    try:
        connector = MongoAsynchConnector(mongo_db=MONGO_DB, mongo_collection=MONGO_COLLECTION)
        await connector._perform_startup_checks()
        app.state.mongo_connector = connector

    except Exception as e:
        logger.critical(f"Failed to initialize MongoDB connector during startup: {e}", exc_info=True)
        raise RuntimeError("Application startup failed due to MongoDB connector initialization error.") from e

    pgpool_connector: AsyncPGConnector | None = None
    try:
        pgpool_connector = cast(AsyncPGConnector, get_pg_connector(mode='async'))
        logger.info("Connecting to PostgreSQL...")
        await pgpool_connector.connect()
        logger.info("PostgreSQL pool connection initiated.")

        # actual_pool = pgpool_connector.get_pool()
        #
        # logger.info("Ensuring hypertables exist...")
        # await ensure_hypertables(actual_pool)
        # logger.info("Hypertables checked/created.")

        app.state.postgres_pool_connector = pgpool_connector
        logger.info("PostgreSQL connector initialized successfully.")

    except Exception as e:
        if pgpool_connector and pgpool_connector._pool:
            try:
                logger.info("Attempting to close PostgreSQL pool due to startup error...")
                await pgpool_connector.close_postgres()
                logger.info("PostgreSQL pool closed after startup error.")
            except Exception as close_e:
                logger.error(f"Failed to close PostgreSQL pool during error handling: {close_e}", exc_info=True)
        logger.critical(f"Failed to initialize Postgres/Alembic during startup: {e}", exc_info=True)
        raise RuntimeError("Application startup failed due to Postgres/Alembic initialization error.") from e

    else:
        logger.info(f"Started with {DEBUG=}")
    yield  # Separates code before the application starts and after it stops
    try:
        await app.state.postgres_pool.close_postgres()
    except Exception as e:
        logger.critical(f"Failed to close postgres connection: {e}", exc_info=True)
    logger.info("Application shutdown...")
