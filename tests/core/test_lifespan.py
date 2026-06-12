from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.unit
async def test_lifespan_sets_correct_state_attributes() -> None:
    """Startup stores connectors under the expected app.state attribute names."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    mock_mongo = AsyncMock()
    mock_pg = AsyncMock()
    mock_pg.get_pool = MagicMock(return_value=MagicMock())

    with (
        patch("src.config.lifespan.MongoAsynchConnector", return_value=mock_mongo),
        patch("src.config.lifespan.get_pg_connector", return_value=mock_pg),
        patch("src.config.lifespan.ensure_hypertables", new=AsyncMock()),
    ):
        async with lifespan(test_app):
            assert hasattr(test_app.state, "postgres_pool_connector")
            assert hasattr(test_app.state, "mongo_connector")
            assert test_app.state.postgres_pool_connector is mock_pg
            assert test_app.state.mongo_connector is mock_mongo


@pytest.mark.unit
async def test_lifespan_shutdown_closes_postgres_pool() -> None:
    """Regression: shutdown must call close_postgres() on postgres_pool_connector, not postgres_pool."""
    from fastapi import FastAPI

    from src.config.lifespan import lifespan

    test_app = FastAPI(lifespan=lifespan)
    mock_mongo = AsyncMock()
    mock_pg = AsyncMock()
    mock_pg.get_pool = MagicMock(return_value=MagicMock())

    with (
        patch("src.config.lifespan.MongoAsynchConnector", return_value=mock_mongo),
        patch("src.config.lifespan.get_pg_connector", return_value=mock_pg),
        patch("src.config.lifespan.ensure_hypertables", new=AsyncMock()),
    ):
        async with lifespan(test_app):
            pass

    mock_pg.close_postgres.assert_awaited_once()
