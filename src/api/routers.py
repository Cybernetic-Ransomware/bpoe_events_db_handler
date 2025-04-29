from fastapi import APIRouter, Depends

from src.api.dependencies import get_mongo_connector
from src.config.conf_logger import setup_logger
from src.core.documentstorage.models import OCRedImageResult, OCROnlyResult
from src.core.documentstorage.utils import MongoConnector

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

@router.get("/ocr_full/", response_model=OCRedImageResult)
def read_ocr_full(image_name: str, user_email: str, connector: MongoConnector = Depends(get_mongo_connector)):
    return connector.get_ocr_result(image_name, user_email)

