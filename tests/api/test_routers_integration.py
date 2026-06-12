import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.dependencies import get_mongo_connector, get_pg_connector
from src.core.documentstorage.exceptions import MongoDBConnectorError


@pytest.fixture
async def pg_api_client(app, pg_connection: asyncpg.Connection):
    async def override_pg():
        yield pg_connection

    app.dependency_overrides[get_pg_connector] = override_pg
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.pop(get_pg_connector, None)


@pytest.fixture
def mock_mongo():
    connector = AsyncMock()
    connector.get_ocr_result = AsyncMock(return_value=["line one", "line two"])
    connector.get_full_ocr_document = AsyncMock(
        return_value={
            "filename": "test_image.jpg",
            "user_email": "user@example.com",
            "ocr_result": ["line one", "line two"],
            "upload_date": datetime.now(UTC),
        }
    )
    return connector


@pytest.fixture
async def mongo_api_client(app, mock_mongo):
    async def override_mongo():
        return mock_mongo

    app.dependency_overrides[get_mongo_connector] = override_mongo
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.pop(get_mongo_connector, None)


@pytest.mark.integration
async def test_create_event_returns_event_id(pg_api_client: AsyncClient) -> None:
    response = await pg_api_client.post("/api/", json={"name": "Test Event", "owner_email": "owner@example.com"})
    assert response.status_code == 201
    body = response.json()
    assert "event_id" in body
    uuid.UUID(body["event_id"])


@pytest.mark.integration
async def test_get_event_returns_correct_structure(pg_api_client: AsyncClient) -> None:
    create_resp = await pg_api_client.post("/api/", json={"name": "Read Event", "owner_email": "reader@example.com"})
    assert create_resp.status_code == 201
    event_id = create_resp.json()["event_id"]

    get_resp = await pg_api_client.get(f"/api/{event_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["id"] == event_id
    assert body["name"] == "Read Event"
    assert body["closed_at"] is None
    assert len(body["participants"]) >= 1
    emails = [p["email"] for p in body["participants"]]
    assert "reader@example.com" in emails


@pytest.mark.integration
async def test_get_event_not_found_returns_404(pg_api_client: AsyncClient) -> None:
    missing_id = uuid.uuid4()
    response = await pg_api_client.get(f"/api/{missing_id}")
    assert response.status_code == 404


@pytest.mark.integration
async def test_read_ocr_returns_ocr_lines(mongo_api_client: AsyncClient, mock_mongo) -> None:
    response = await mongo_api_client.get("/api/ocr/", params={"image_name": "test_image.jpg", "user_email": "user@example.com"})
    assert response.status_code == 200
    body = response.json()
    assert body["ocr_result"] == ["line one", "line two"]
    mock_mongo.get_ocr_result.assert_awaited_once_with("test_image.jpg", "user@example.com")


@pytest.mark.integration
async def test_read_ocr_wrong_email_returns_error(mongo_api_client: AsyncClient, mock_mongo) -> None:
    mock_mongo.get_ocr_result = AsyncMock(side_effect=MongoDBConnectorError(message="User email does not match the record owner."))
    response = await mongo_api_client.get("/api/ocr/", params={"image_name": "test_image.jpg", "user_email": "wrong@example.com"})
    assert response.status_code == 503


@pytest.mark.integration
async def test_read_ocr_full_returns_full_document(mongo_api_client: AsyncClient) -> None:
    response = await mongo_api_client.get(
        "/api/ocr/full/", params={"image_name": "test_image.jpg", "user_email": "user@example.com"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "test_image.jpg"
    assert body["user_email"] == "user@example.com"
    assert body["ocr_result"] == ["line one", "line two"]
