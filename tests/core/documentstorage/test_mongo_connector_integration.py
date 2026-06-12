from datetime import UTC, datetime

import pytest
from pymongo import AsyncMongoClient, MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from src.core.documentstorage.exceptions import MongoDBConnectorError
from src.core.documentstorage.utils import MongoAsynchConnector

_DB = "connector_test_db"
_COL = "ocr_results"


@pytest.fixture(scope="session")
def seeded_mongo(mongo_url: str):
    """Seed test documents once per session using a sync client."""
    client = MongoClient(mongo_url)
    col = client[_DB][_COL]
    col.insert_many(
        [
            {
                "filename": "image1.jpg",
                "user_email": "owner@example.com",
                "ocr_result": ["First line", "Second line"],
                "upload_date": datetime.now(UTC),
            },
            {
                "filename": "image2.jpg",
                "user_email": "other@example.com",
                "ocr_result": ["Other content"],
                "upload_date": datetime.now(UTC),
            },
        ]
    )
    yield
    client.drop_database(_DB)
    client.close()


@pytest.fixture
async def connector(mongo_url: str, seeded_mongo):
    """MongoAsynchConnector wired to the test container — new client per test."""
    client = AsyncMongoClient(mongo_url)
    conn = MongoAsynchConnector(client, mongo_db=_DB, mongo_collection=_COL)
    yield conn
    await client.close()


@pytest.mark.integration
def test_mongo_connection_ping(mongo_url: str) -> None:
    """Raw pymongo client reaches the test MongoDB instance."""
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5_000)
    try:
        info = client.server_info()
        assert "version" in info
    finally:
        client.close()


@pytest.mark.integration
def test_mongo_insert_and_find(mongo_url: str) -> None:
    """Basic insert/find round-trip against the test MongoDB instance."""
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5_000)
    try:
        col = client["integration_test_db"]["test_collection"]
        inserted = col.insert_one(
            {"filename": "test.jpg", "user_email": "test@example.com", "ocr_result": ["line1"]}
        )
        assert inserted.inserted_id is not None
        found = col.find_one({"filename": "test.jpg"})
        assert found is not None
        assert found["user_email"] == "test@example.com"
    finally:
        client.drop_database("integration_test_db")
        client.close()


@pytest.mark.integration
def test_mongo_unavailable_raises(mongo_url: str) -> None:
    """Bad connection URL raises ServerSelectionTimeoutError promptly."""
    client = MongoClient("mongodb://localhost:19999", serverSelectionTimeoutMS=500)
    with pytest.raises(ServerSelectionTimeoutError):
        client.server_info()
    client.close()


@pytest.mark.integration
async def test_get_ocr_result_happy_path(connector: MongoAsynchConnector) -> None:
    result = await connector.get_ocr_result("image1.jpg", "owner@example.com")
    assert result == ["First line", "Second line"]


@pytest.mark.integration
async def test_get_ocr_result_not_found_raises(connector: MongoAsynchConnector) -> None:
    with pytest.raises(MongoDBConnectorError):
        await connector.get_ocr_result("missing.jpg", "owner@example.com")


@pytest.mark.integration
async def test_get_ocr_result_wrong_email_raises(connector: MongoAsynchConnector) -> None:
    with pytest.raises(MongoDBConnectorError):
        await connector.get_ocr_result("image1.jpg", "wrong@example.com")


@pytest.mark.integration
async def test_get_full_ocr_document_happy_path(connector: MongoAsynchConnector) -> None:
    doc = await connector.get_full_ocr_document("image1.jpg", "owner@example.com")
    assert doc["filename"] == "image1.jpg"
    assert doc["user_email"] == "owner@example.com"
    assert doc["ocr_result"] == ["First line", "Second line"]
    assert "_id" not in doc


@pytest.mark.integration
async def test_get_full_ocr_document_not_found_raises(connector: MongoAsynchConnector) -> None:
    with pytest.raises(MongoDBConnectorError):
        await connector.get_full_ocr_document("missing.jpg", "owner@example.com")


@pytest.mark.integration
async def test_get_full_ocr_document_wrong_email_raises(connector: MongoAsynchConnector) -> None:
    with pytest.raises(MongoDBConnectorError):
        await connector.get_full_ocr_document("image1.jpg", "wrong@example.com")


@pytest.mark.integration
async def test_perform_startup_checks_passes_with_valid_collection(mongo_url: str, seeded_mongo) -> None:
    """Startup checks pass against a real container when the collection exists.
    DEBUG=True (set in tests/.env.test) skips role checks, so no mocks are needed."""
    client = AsyncMongoClient(mongo_url)
    conn = MongoAsynchConnector(client, mongo_db=_DB, mongo_collection=_COL)
    try:
        await conn._perform_startup_checks()
    finally:
        await client.close()


@pytest.mark.integration
async def test_perform_startup_checks_fails_missing_collection(mongo_url: str, seeded_mongo) -> None:
    """Startup checks raise MongoDBConnectorError when the collection does not exist."""
    client = AsyncMongoClient(mongo_url)
    conn = MongoAsynchConnector(client, mongo_db=_DB, mongo_collection="nonexistent_collection")
    try:
        with pytest.raises(MongoDBConnectorError):
            await conn._perform_startup_checks()
    finally:
        await client.close()
