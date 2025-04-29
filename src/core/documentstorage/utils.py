
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid, ServerSelectionTimeoutError

from src.config.conf_logger import setup_logger
from src.config.config import DEBUG, MONGO_COLLECTION, MONGO_DB, MONGO_POOL_SIZE, MONGO_READER_URI
from src.core.documentstorage.exceptions import MongoDBConnectorError

logger = setup_logger(__name__, "documentstorage")


mongo_client: MongoClient = MongoClient(
    MONGO_READER_URI,
    uuidRepresentation='standard',
    maxPoolSize=MONGO_POOL_SIZE[1],
    minPoolSize=MONGO_POOL_SIZE[0],
)


class MongoConnector:
    def __init__(self, mongo_db: str = MONGO_DB, mongo_collection: str = MONGO_COLLECTION):
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.database = mongo_client[self.mongo_db]

    def _perform_startup_checks(self):
        logger.info("Performing MongoDB startup checks...")
        try:
            server_info = mongo_client.server_info()
            logger.info(f"Successfully connected to MongoDB server version {server_info['version']}")

            if self.mongo_collection not in self.database.list_collection_names():
                logger.error(f"Collection '{self.mongo_collection}' does not exist in database '{self.mongo_db}'")
                raise CollectionInvalid(
                    f"Collection '{self.mongo_collection}' does not exist in database '{self.mongo_db}'"
                )
            logger.info(f"Collection '{self.mongo_collection}' found in database '{self.mongo_db}'.")

            if not DEBUG:
                self._ensure_non_admin_user()
                logger.info("User role checks passed.")
            else:
                logger.warning("Skipping user role checks in DEBUG mode.")

            logger.info("MongoDB startup checks completed successfully.")

        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB connection error during startup checks: {e}")
            raise MongoDBConnectorError(message=str(e) if DEBUG else "MongoDB connection failed") from e
        except Exception as e:
            logger.error(f"Error during MongoDB startup checks: {e}")
            raise MongoDBConnectorError(message="Error during MongoDB startup checks") from e

    def _ensure_non_admin_user(self):
        try:
            result = self.database.command("usersInfo", {"forAllDBs": False})
            roles = result.get("users", [])[0].get("roles", [])

            forbidden_roles = {
                "dbAdmin", "userAdmin", "readWriteAnyDatabase",
                "dbOwner", "root", "clusterAdmin"
            }

            for role in roles:
                if role["role"] in forbidden_roles or role["role"].endswith("Admin"):
                    raise MongoDBConnectorError(
                        message=f"User role not allowed: {role['role']} on the base: {role['db']}"
                    )
        except Exception as e:
            logger.error(f"Error during getting user role: {e}")
            raise MongoDBConnectorError(message="Error during getting user role") from e

    def get_ocr_result(self, image_name: str, user_email: str) -> list[str]:
        try:
            collection = self.database[self.mongo_collection]  # type: ignore[index]
            document = collection.find_one({"filename": image_name})

            if document is None:
                raise MongoDBConnectorError(message=f"No OCR result found for filename: {image_name}")

            if document.get("user_email") != user_email:
                raise MongoDBConnectorError(message="User email does not match the record owner.")

            return document.get("ocr_result", [])

        except Exception as e:
            logger.error(f"Failed to retrieve OCR result for '{image_name}': {e}")
            raise MongoDBConnectorError(message=f"Failed to retrieve OCR data: {e}") from e
