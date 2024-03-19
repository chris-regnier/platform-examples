"""
Tests the relational database adapter.
"""

import datetime

import pytest
import pytest_asyncio
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.pytest_plugin import register_fixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.python.adapters.outgoing.relational_database import (
    MessageModel,
    VisitorModel,
    create_database_engine,
    get_sessionmaker,
)


@pytest_asyncio.fixture(scope="session")
async def create_sqlite_engine():
    """
    Creates a SQLite database engine.
    """
    engine = await create_database_engine("sqlite+aiosqlite:///:memory:")
    yield engine
    await engine.dispose()


class VisitorFactory(SQLAlchemyFactory[VisitorModel]):
    __set_as_default_factory_for_type__ = True

    id = None
    created_at = None
    updated_at = None
    deleted_at = None
    messages = []


class MessageFactory(SQLAlchemyFactory[MessageModel]):
    __set_as_default_factory_for_type__ = True

    id = None
    created_at = None
    updated_at = None
    deleted_at = None


visitor_factory = register_fixture(VisitorFactory)
message_factory = register_fixture(MessageFactory)


def _test_message_properties(message):
    assert message.id is not None
    assert message.content
    assert message.sender
    assert message.receiver
    assert message.created_at.timestamp()
    assert message.updated_at.timestamp()


def _test_visitor_properties(visitor):
    assert visitor.id is not None
    assert visitor.name
    assert visitor.email
    assert visitor.created_at
    assert visitor.updated_at
    for message in visitor.messages:
        _test_message_properties(message)


@pytest.mark.asyncio
async def test_create_visitor(create_sqlite_engine, visitor_factory):
    """
    Tests creating a visitor.
    """
    visitor = visitor_factory.build()
    test_now = (
        datetime.datetime.now()
    )  # objects should be created *after* this point by default
    async with AsyncSession(create_sqlite_engine, expire_on_commit=False) as conn:
        conn.add(visitor)
        await conn.commit()
    _test_visitor_properties(visitor)


@pytest.mark.asyncio
async def test_create_visitor_with_messages(
    create_sqlite_engine, visitor_factory, message_factory
):
    """
    Tests creating a visitor with a message.
    """
    messages = message_factory.batch(5)
    visitor = visitor_factory.build(messages=messages)
    async with AsyncSession(create_sqlite_engine, expire_on_commit=False) as conn:
        conn.add(visitor)
        await conn.commit()
    _test_visitor_properties(visitor)
