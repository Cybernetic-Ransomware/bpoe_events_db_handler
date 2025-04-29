from fastapi import Request

from src.api.exceptions import ServerInitError
from src.core.documentstorage.utils import MongoConnector


def get_mongo_connector(request: Request):
    if not hasattr(request.app.state, 'mongo_connector_instance'):
        raise ServerInitError(message="Internal server error: MongoDB connector not available")

    connector_instance = request.app.state.mongo_connector_instance

    if not isinstance(connector_instance, MongoConnector):
         raise ServerInitError(message="Internal server error: Invalid DB connector type")

    return connector_instance
