from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_patches(*, mongo_raises=None, pg_connect_raises=None, hypertables_raises=None, pg_pool=True):
    """Return a shared patch context for lifespan tests.

    mongo_raises  — exception to raise from _perform_startup_checks (None = success)
    pg_connect_raises — exception to raise from pg.connect (None = success)
    hypertables_raises — exception to raise from ensure_hypertables (None = success)
    pg_pool — whether mock_pg._pool is truthy (controls rollback path)
    """
    mock_mongo_client = AsyncMock()
    mock_mongo = AsyncMock()
    if mongo_raises is not None:
        mock_mongo._perform_startup_checks = AsyncMock(side_effect=mongo_raises)

    mock_pg = AsyncMock()
    mock_pg._pool = MagicMock() if pg_pool else None
    mock_pg.get_pool = MagicMock(return_value=MagicMock())
    if pg_connect_raises is not None:
        mock_pg.connect = AsyncMock(side_effect=pg_connect_raises)

    mock_ensure = AsyncMock(side_effect=hypertables_raises) if hypertables_raises else AsyncMock()

    patches = [
        patch("src.config.lifespan.create_async_mongo_client", return_value=mock_mongo_client),
        patch("src.config.lifespan.MongoAsynchConnector", return_value=mock_mongo),
        patch("src.config.lifespan.get_pg_connector", return_value=mock_pg),
        patch("src.config.lifespan.ensure_hypertables", new=mock_ensure),
    ]
    return patches, mock_mongo_client, mock_mongo, mock_pg, mock_ensure


@pytest.mark.unit
async def test_lifespan_sets_correct_state_attributes() -> None:
    """Startup stores connectors under the expected app.state attribute names."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    patches, mock_mongo_client, mock_mongo, mock_pg, _ = _make_patches()

    with patches[0], patches[1], patches[2], patches[3]:
        async with lifespan(test_app):
            assert hasattr(test_app.state, "postgres_pool_connector")
            assert hasattr(test_app.state, "mongo_connector")
            assert test_app.state.postgres_pool_connector is mock_pg
            assert test_app.state.mongo_connector is mock_mongo
            assert test_app.state.mongo_client is mock_mongo_client


@pytest.mark.unit
async def test_lifespan_shutdown_closes_postgres_pool() -> None:
    """Regression: shutdown must call close_postgres() on postgres_pool_connector."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    patches, mock_mongo_client, _, mock_pg, _ = _make_patches()

    with patches[0], patches[1], patches[2], patches[3]:
        async with lifespan(test_app):
            pass

    mock_pg.close_postgres.assert_awaited_once()


@pytest.mark.unit
async def test_lifespan_shutdown_closes_mongo_client() -> None:
    """Shutdown must call close() on the MongoDB async client."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    patches, mock_mongo_client, _, _, _ = _make_patches()

    with patches[0], patches[1], patches[2], patches[3]:
        async with lifespan(test_app):
            pass

    mock_mongo_client.close.assert_awaited_once()


@pytest.mark.unit
async def test_lifespan_mongo_startup_fail_raises_runtime_error() -> None:
    """When MongoDB startup checks fail, lifespan raises RuntimeError about MongoDB."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    patches, _, _, mock_pg, _ = _make_patches(mongo_raises=RuntimeError("mongo down"))

    with patches[0], patches[1], patches[2], patches[3]:
        with pytest.raises(RuntimeError, match="MongoDB connector"):
            async with lifespan(test_app):
                pass  # pragma: no cover

    assert not hasattr(test_app.state, "postgres_pool_connector")


@pytest.mark.unit
async def test_lifespan_pg_connect_fail_raises_runtime_error() -> None:
    """When PostgreSQL connect() fails, lifespan raises RuntimeError about Postgres/Alembic."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    patches, _, _, _, _ = _make_patches(pg_connect_raises=OSError("pg down"))

    with patches[0], patches[1], patches[2], patches[3]:
        with pytest.raises(RuntimeError, match="Postgres/Alembic"):
            async with lifespan(test_app):
                pass  # pragma: no cover


@pytest.mark.unit
async def test_lifespan_partial_failure_closes_pg_pool() -> None:
    """When ensure_hypertables raises after the pool is created, close_postgres is called."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    patches, _, _, mock_pg, _ = _make_patches(hypertables_raises=RuntimeError("hypertable error"), pg_pool=True)

    with patches[0], patches[1], patches[2], patches[3]:
        with pytest.raises(RuntimeError):
            async with lifespan(test_app):
                pass  # pragma: no cover

    mock_pg.close_postgres.assert_awaited_once()
