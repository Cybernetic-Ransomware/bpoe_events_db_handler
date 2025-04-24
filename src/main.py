from fastapi import FastAPI

from src.config.conf_logger import setup_logger
from src.config.lifespan import lifespan

logger = setup_logger(__name__, "main")

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def healthcheck():
    logger.info("Called first healthcheck")
    return {"status": "OK"}
