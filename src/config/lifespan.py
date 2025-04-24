from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.conf_logger import setup_logger
from src.config.config import DEBUG

logger = setup_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{DEBUG=}", flush=True)
    logger.info(f"Started with {DEBUG=}")
    yield  # Separates code before the application starts and after it stops
    # ___ Any code to clean up resources after the application stops
