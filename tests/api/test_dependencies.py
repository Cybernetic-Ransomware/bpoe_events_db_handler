"""Unit tests for api/dependencies.py guard functions.

Uses a minimal fake Request built with types.SimpleNamespace so there is no
need to spin up a real FastAPI app or any database connections.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api.exceptions import ServerInitError


def _fake_request(**state_attrs):
    """Return a minimal Request-like object with app.state carrying *state_attrs*."""
    state = SimpleNamespace(**state_attrs)
    app = SimpleNamespace(state=state)
    return SimpleNamespace(app=app)


@pytest.mark.unit
async def test_get_mongo_connector_missing_attribute_raises() -> None:
    """No mongo_connector on app.state → ServerInitError."""
    from src.api.dependencies import get_mongo_connector

    request = _fake_request()
    with pytest.raises(ServerInitError):
        await get_mongo_connector(request)


@pytest.mark.unit
async def test_get_mongo_connector_wrong_type_raises() -> None:
    """mongo_connector is not a MongoAsynchConnector → ServerInitError."""
    from src.api.dependencies import get_mongo_connector

    request = _fake_request(mongo_connector=object())
    with pytest.raises(ServerInitError):
        await get_mongo_connector(request)


@pytest.mark.unit
async def test_get_mongo_connector_returns_connector() -> None:
    """Valid MongoAsynchConnector instance is returned as-is."""
    from src.api.dependencies import get_mongo_connector
    from src.core.documentstorage.utils import MongoAsynchConnector

    fake_connector = MagicMock(spec=MongoAsynchConnector)
    request = _fake_request(mongo_connector=fake_connector)
    result = await get_mongo_connector(request)
    assert result is fake_connector


@pytest.mark.unit
async def test_get_pg_connector_missing_attribute_raises() -> None:
    """No postgres_pool_connector on app.state → ServerInitError."""
    from src.api.dependencies import get_pg_connector

    request = _fake_request()
    gen = get_pg_connector(request)
    with pytest.raises(ServerInitError):
        await gen.__anext__()


@pytest.mark.unit
async def test_get_pg_connector_wrong_type_raises() -> None:
    """postgres_pool_connector is not an AsyncPGConnector → ServerInitError."""
    from src.api.dependencies import get_pg_connector

    request = _fake_request(postgres_pool_connector=object())
    gen = get_pg_connector(request)
    with pytest.raises(ServerInitError):
        await gen.__anext__()


@pytest.mark.unit
async def test_get_pg_connector_yields_connection() -> None:
    """Valid AsyncPGConnector: the dependency yields the acquired connection."""
    from src.api.dependencies import get_pg_connector
    from src.core.relationaldb.psycopg2_con.utils import AsyncPGConnector

    fake_conn = object()
    pool_mock = MagicMock()
    pool_mock.acquire.return_value.__aenter__ = AsyncMock(return_value=fake_conn)
    pool_mock.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

    fake_pg = MagicMock(spec=AsyncPGConnector)
    fake_pg.get_pool = MagicMock(return_value=pool_mock)

    request = _fake_request(postgres_pool_connector=fake_pg)
    gen = get_pg_connector(request)
    conn = await gen.__anext__()
    assert conn is fake_conn
