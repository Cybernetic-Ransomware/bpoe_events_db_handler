from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.conf_logger import setup_logger
from src.config import DEBUG

logger = setup_logger(__name__, "main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{DEBUG=}", flush=True)
    logger.info(f"Started with {DEBUG=}")
    yield  # Separates code before the application starts and after it stops
    # ___ Any code to clean up resources after the application stops


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def healthcheck():
    logger.info("Called first healthcheck")
    return {"status": "OK"}
