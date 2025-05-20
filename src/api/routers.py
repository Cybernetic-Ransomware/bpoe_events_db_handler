import uuid

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_mongo_connector, get_pg_connector
from src.api.schemas import EventCreateIn, EventRead
from src.config.conf_logger import setup_logger
from src.core.documentstorage.models import OCRedImageResult, OCROnlyResult
from src.core.documentstorage.utils import MongoConnector
from src.core.relationaldb.repositories.events import create_event_with_owner, get_event_by_id

logger = setup_logger(__name__, "api")

router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck():
    logger.info("Called second healthcheck [API router]")
    return {"status": "OK"}


@router.get("/ocr/", response_model=OCROnlyResult)
def read_ocr(image_name: str, user_email: str, connector: MongoConnector = Depends(get_mongo_connector)):
    ocr_data = connector.get_ocr_result(image_name, user_email)
    return OCROnlyResult(ocr_result=ocr_data)

@router.get("/ocr/full/", response_model=OCRedImageResult)
def read_ocr_full(image_name: str, user_email: str, connector: MongoConnector = Depends(get_mongo_connector)):
    return connector.get_ocr_result(image_name, user_email)

@router.post("/", status_code=201)
async def create_event(
    payload: EventCreateIn,
    conn: Connection = Depends(get_pg_connector)
):
    event_id = await create_event_with_owner(conn, name=payload.name, owner_email=payload.owner_email)
    return {"event_id": event_id}


@router.get("/{event_id}", response_model=EventRead)
async def read_event(
    event_id: uuid.UUID,
    conn: Connection = Depends(get_pg_connector)
):
    try:
        event = await get_event_by_id(conn, event_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e  #TODO custom

    return event
