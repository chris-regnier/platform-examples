from abc import ABC, abstractmethod
from typing import Any, Mapping

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from ..domain.models import BaseModel


class BaseRepository(ABC):

    @abstractmethod
    async def get(self, id_: int) -> BaseModel: ...

    @abstractmethod
    async def list(self, **kwargs) -> list[BaseModel]: ...

    @abstractmethod
    async def create(self, entity: BaseModel) -> BaseModel: ...

    @abstractmethod
    async def update(self, id_: int, entity: BaseModel) -> BaseModel: ...

    @abstractmethod
    async def delete(self, id_: int) -> None: ...


class SQLAlchemyRepository(BaseRepository):

    def __init__(self, sessionmaker: async_sessionmaker, model: BaseModel):
        self.session = sessionmaker
        self.model = model

    async def get(self, id_: int) -> BaseModel:
        async with self.session() as s:
            result = await s.get(self.model, id_)
            entity = result
        return entity

    async def list(self, **kwargs) -> list[BaseModel]:
        query = select(self.model).filter_by(**kwargs)
        async with self.session() as s:
            result = await s.scalars(query)
            entities = result.fetchall()
        return entities

    async def create(self, data: Mapping[str, Any]) -> BaseModel:
        async with self.session() as s:
            entity = self.model(**data)
            s.add(entity)
            await s.commit()
            await s.refresh(entity)
        return entity

    async def update(
        self, id_, data: Mapping[str, Any], set_none: bool = False
    ) -> BaseModel:
        async with self.session() as s:
            existing_entity = await s.get(self.model, id_)
            for key, value in data.items():
                if value is not None or (value is None and set_none):
                    setattr(existing_entity, key, value)
            await s.commit()
            await s.refresh(existing_entity)
        return existing_entity

    async def delete(self, id_: int) -> None:
        query = delete(self.model).where(self.model.id == id_)
        async with self.session() as s:
            result = await s.execute(query)
            await s.commit()
            try:
                assert result.rowcount == 1
            except AssertionError:
                raise ValueError(f"Entity with id {id_} not deleted")
            entity = await self.get(id_)
        return entity
