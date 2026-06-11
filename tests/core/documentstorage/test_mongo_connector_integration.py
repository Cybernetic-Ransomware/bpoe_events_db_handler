import pytest
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


@pytest.mark.integration
def test_mongo_connection_ping(mongo_url: str) -> None:
    """Verify that a raw pymongo client can reach the test MongoDB instance."""
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5_000)
    try:
        info = client.server_info()
        assert "version" in info
    finally:
        client.close()


@pytest.mark.integration
def test_mongo_insert_and_find(mongo_url: str) -> None:
    """Verify basic insert/find round-trip against the test MongoDB instance."""
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5_000)
    try:
        db = client["integration_test_db"]
        collection = db["test_collection"]
        doc = {"filename": "test.jpg", "user_email": "test@example.com", "ocr_result": ["line1"]}
        inserted = collection.insert_one(doc)
        assert inserted.inserted_id is not None

        found = collection.find_one({"filename": "test.jpg"})
        assert found is not None
        assert found["user_email"] == "test@example.com"
        assert found["ocr_result"] == ["line1"]
    finally:
        client.drop_database("integration_test_db")
        client.close()


@pytest.mark.integration
def test_mongo_unavailable_raises(mongo_url: str) -> None:
    """Confirm that a bad connection URL raises ServerSelectionTimeoutError promptly."""
    bad_url = "mongodb://localhost:19999"
    client = MongoClient(bad_url, serverSelectionTimeoutMS=500)
    with pytest.raises(ServerSelectionTimeoutError):
        client.server_info()
    client.close()
