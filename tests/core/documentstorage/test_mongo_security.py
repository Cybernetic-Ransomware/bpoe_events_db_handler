from unittest.mock import AsyncMock

import pytest

from src.core.documentstorage.exceptions import MongoDBConnectorError
from src.core.documentstorage.utils import MongoAsynchConnector


def _make_connector() -> MongoAsynchConnector:
    """Return a MongoAsynchConnector with __init__ bypassed; only database is needed."""
    connector = MongoAsynchConnector.__new__(MongoAsynchConnector)
    connector.mongo_db = "test_db"
    connector.mongo_collection = "test_col"
    return connector


@pytest.mark.unit
async def test_ensure_non_admin_blocks_root_role() -> None:
    connector = _make_connector()
    connector.database = AsyncMock()
    connector.database.command = AsyncMock(
        return_value={"users": [{"roles": [{"role": "root", "db": "admin"}]}]}
    )

    with pytest.raises(MongoDBConnectorError):
        await connector._ensure_non_admin_user()


@pytest.mark.unit
async def test_ensure_non_admin_blocks_db_admin_role() -> None:
    connector = _make_connector()
    connector.database = AsyncMock()
    connector.database.command = AsyncMock(
        return_value={"users": [{"roles": [{"role": "dbAdmin", "db": "test_db"}]}]}
    )

    with pytest.raises(MongoDBConnectorError):
        await connector._ensure_non_admin_user()


@pytest.mark.unit
async def test_ensure_non_admin_allows_read_role() -> None:
    connector = _make_connector()
    connector.database = AsyncMock()
    connector.database.command = AsyncMock(
        return_value={"users": [{"roles": [{"role": "read", "db": "test_db"}]}]}
    )

    await connector._ensure_non_admin_user()
