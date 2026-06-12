import uuid

from asyncpg import Connection
from fastapi import APIRouter, Depends

from src.api.dependencies import get_mongo_connector, get_pg_connector
from src.config.conf_logger import setup_logger
from src.core.documentstorage.models import OCRedImageResult, OCROnlyResult
from src.core.documentstorage.utils import MongoAsynchConnector
from src.core.relationaldb.models.schemas import EventCreateIn, EventRead
from src.core.relationaldb.psycopg2_con.repositories.events import create_event_with_owner, get_event_by_id

logger = setup_logger(__name__, "api")

router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck():
    logger.info("Called second healthcheck [API router]")
    return {"status": "OK"}


@router.get("/ocr/", response_model=OCROnlyResult)
async def read_ocr(image_name: str, user_email: str, connector: MongoAsynchConnector = Depends(get_mongo_connector)):
    ocr_data = await connector.get_ocr_result(image_name, user_email)
    return OCROnlyResult(ocr_result=ocr_data)


@router.get("/ocr/full/", response_model=OCRedImageResult)
async def read_ocr_full(image_name: str, user_email: str, connector: MongoAsynchConnector = Depends(get_mongo_connector)):
    doc = await connector.get_full_ocr_document(image_name, user_email)
    return OCRedImageResult.model_validate(doc)


@router.post("/", status_code=201)
async def create_event(payload: EventCreateIn, conn: Connection = Depends(get_pg_connector)):
    event_id = await create_event_with_owner(conn, name=payload.name, owner_email=payload.owner_email)
    return {"event_id": event_id}


@router.get("/{event_id}", response_model=EventRead)
async def read_event(event_id: uuid.UUID, conn: Connection = Depends(get_pg_connector)):
    return await get_event_by_id(conn, event_id)
