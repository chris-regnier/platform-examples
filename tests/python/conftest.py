import pytest
import pytest_asyncio


@pytest.fixture
def async_sqlite_engine():
    from sqlalchemy.ext.asyncio import create_async_engine

    return create_async_engine("sqlite+aiosqlite:///:memory:")


@pytest_asyncio.fixture
async def async_bootstrapped_sqlite_engine(async_sqlite_engine):
    from src.python.models.base import BaseModel

    async with async_sqlite_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    return async_sqlite_engine


@pytest.fixture
def async_sessionmaker(async_bootstrapped_sqlite_engine):
    from sqlalchemy.ext.asyncio import async_sessionmaker

    return async_sessionmaker(async_bootstrapped_sqlite_engine, expire_on_commit=False)
