"""
Tests repository logic.
"""

from dataclasses import asdict
from operator import contains
from typing import Sequence

import pytest

from src.python.adapters.outgoing.relational_database import MessageModel, VisitorModel
from src.python.domain.models import Visitor
from src.python.ports.repository import BaseRepository, SQLAlchemyRepository

from ..adapters.outgoing.test_relational_database import get_sessionmaker, create_sqlite_engine
from . import visitor_factory, VisitorFactory, MessageFactory  # imported as a fixture


@pytest.fixture
def my_repository(visitor_factory):

    class MyRepository(BaseRepository):
        def get(self, id_: int) -> Visitor:
            return visitor_factory.build(id=id_)

        def list(self, length: int) -> list[Visitor]:
            return visitor_factory.batch(length)

        def create(self, entity: Visitor) -> Visitor:
            return visitor_factory.build(**asdict(entity))

        def update(self, id_: int, entity: Visitor) -> Visitor:
            entity.id = id_
            return visitor_factory.build(**asdict(entity))

        def delete(self, id_: int):
            return

    return MyRepository


def test_repository_init(my_repository):
    repo = my_repository()
    assert repo


def test_repository_get(my_repository, faker):
    id_ = faker.random_int()
    repo = my_repository()
    visitor = repo.get(id_)
    assert visitor.id == id_


def test_repository_list(my_repository, faker):
    length = faker.random_int(1, 50)
    repo = my_repository()
    visitors = repo.list(length)
    assert len(visitors) == length


def test_repository_create(my_repository, visitor_factory):
    repo = my_repository()
    visitor_before = visitor_factory.build()
    visitor_after = repo.create(visitor_before)
    assert visitor_before == visitor_after


@pytest.fixture(
    params=[
        (VisitorModel, VisitorFactory),
        (MessageModel, MessageFactory)
    ],
)
def my_sqlalchemy_repository_and_factory(create_sqlite_engine, request):
    engine = create_sqlite_engine
    model, factory = request.param
    sessonmaker = get_sessionmaker(engine)
    return SQLAlchemyRepository(sessonmaker, model), factory


def test_sqlalchemy_repository_init(my_sqlalchemy_repository_and_factory):
    repo, factory = my_sqlalchemy_repository_and_factory
    assert repo
    assert factory.build()


@pytest.mark.asyncio
async def test_sqlalchemy_repository_crud(my_sqlalchemy_repository_and_factory):
    repo, factory = my_sqlalchemy_repository_and_factory
    entity = factory.build()
    created_entity = await repo.create(asdict(entity))
    assert created_entity
    assert created_entity.id
    created_entity_id = created_entity.id

    retrieved = await repo.get(created_entity_id)

    for key, value in asdict(entity).items():
        if key == "id" or isinstance(value, Sequence) or value is None:
            continue
        assert getattr(retrieved, key) == value

        # Test list & filter by
        listed_entities = await repo.list(**{key: value})
        assert retrieved in listed_entities

    new_entity = factory.build()

    updated_entity = await repo.update(created_entity_id, asdict(new_entity))
    assert updated_entity
    assert updated_entity.id == created_entity_id
    assert updated_entity != created_entity
    assert updated_entity.created_at == created_entity.created_at
    assert updated_entity.updated_at >= created_entity.updated_at
    for key, value in asdict(new_entity).items():
        if key == "id" or isinstance(value, Sequence) or value is None:
            continue
        assert getattr(updated_entity, key) == value


    delete_operation = await repo.delete(created_entity_id)
    assert delete_operation is None

    assert await repo.list() == []