"""
Adapter for Relational Database.
"""

from datetime import datetime
from typing import Annotated, AsyncGenerator, Optional

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ...domain.models import BaseModel, Message, Visitor


class BaseRelationalModel(AsyncAttrs, DeclarativeBase, BaseModel):
    """
    Transforms a normal SQLAlchemy model into a dataclass.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Optional[Mapped[datetime]] = Annotated[
        datetime, mapped_column(nullable=True, default=None)
    ]


async def create_database_engine(url: str) -> AsyncEngine:
    """
    Creates a database engine.
    """
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(BaseRelationalModel.metadata.create_all)
    return engine


def get_sessionmaker(
    engine: AsyncEngine, expire_on_commit=False
) -> AsyncGenerator[AsyncSession, None]:
    """
    Returns a sessionmaker for the database engine.
    """
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=expire_on_commit
    )


class VisitorModel(BaseRelationalModel, Visitor):
    """
    Adapter for Visitor model to persist to a relational DB with SQLAlchemy.
    """

    __tablename__ = "visitors"

    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    messages: Optional[Mapped[list["MessageModel"]]] = relationship(
        "MessageModel",
        lazy="selectin",
        cascade_backrefs=False,
    )


class MessageModel(BaseRelationalModel, Message):
    """
    Adapter for Message model to persist to a relational DB with SQLAlchemy.
    """

    __tablename__ = "messages"

    content: Mapped[str] = mapped_column()
    sender: Mapped[str] = mapped_column()
    receiver: Mapped[str] = mapped_column()
    visitor_id: Mapped[int] = mapped_column(ForeignKey(VisitorModel.id), nullable=True)

    visitor: Optional[Mapped[VisitorModel]] = relationship(
        "VisitorModel",
        lazy="selectin",
        cascade_backrefs=False,
        back_populates="messages",
    )
