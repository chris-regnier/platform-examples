"""
Adapter for REST API
"""

import datetime
from types import NoneType
from typing import Annotated, Any, Optional

from decouple import config
from fastapi import Depends, FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from ...domain.models import Message, Visitor
from ...ports.repository import SQLAlchemyRepository
from ..outgoing.relational_database import (
    MessageModel,
    VisitorModel,
    async_sessionmaker,
    create_database_engine,
    get_sessionmaker,
)


class VisitorSchema(BaseModel, Visitor):
    model_config = ConfigDict(from_attributes=True)

    deleted_at: datetime.datetime | Any = Field(..., exclude=True)
    messages: list["MessageSchema"] = Field(..., default_factory=list)


class VisitorCreateSchema(BaseModel):
    name: str
    email: str


async def filter_visitor_parameters(name: str = None, email: str = None):
    params = dict()
    if name:
        params["name"] = name
    if email:
        params["email"] = email
    return params


class MessageSchema(BaseModel, Message):
    model_config = ConfigDict(from_attributes=True)

    deleted_at: datetime.datetime | Any = Field(..., exclude=True)


class MessageCreateSchema(BaseModel):
    content: str
    sender: str
    receiver: str
    visitor_id: int


class MessageUpdateSchema(MessageCreateSchema):
    content: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    visitor_id: Optional[int] = None


VisitorFilterParameters = Annotated[dict, Depends(filter_visitor_parameters)]


async def get_session():
    database_url = config("DATABASE_URL", default="sqlite+aiosqlite:///local.sqlite")
    engine = await create_database_engine(url=database_url)
    yield get_sessionmaker(engine)
    await engine.dispose()


DatabaseSession = Annotated[async_sessionmaker, Depends(get_session)]

app = FastAPI(dependencies=[Depends(get_session)])


@app.get("/")
async def root():
    return {"message": "Hello, World"}


##### Visitors #####


@app.get("/visitors", response_model=list[VisitorSchema], status_code=200)
async def get_visitors(
    filter_visitor_parameters: VisitorFilterParameters,
    session: DatabaseSession,
) -> JSONResponse:
    """
    Returns the number of visitors to the API.
    """
    repository = SQLAlchemyRepository(session, VisitorModel)
    visitors = await repository.list(**filter_visitor_parameters)
    return [VisitorSchema.model_validate(visitor) for visitor in visitors]


@app.get("/visitors/{visitor_id}", response_model=VisitorSchema, status_code=200)
async def get_visitor_by_id(visitor_id: int, session: DatabaseSession) -> JSONResponse:
    """
    Returns a visitor by ID.
    """
    repository = SQLAlchemyRepository(session, VisitorModel)
    visitor = await repository.get(visitor_id)
    if visitor is None:
        return Response(status_code=404)
    return VisitorSchema.model_validate(visitor)


@app.post("/visitors", response_model=VisitorSchema, status_code=201)
async def create_visitor(
    session: DatabaseSession, visitor: VisitorCreateSchema
) -> JSONResponse:
    """
    Creates a visitor.
    """
    repository = SQLAlchemyRepository(session, VisitorModel)
    created_visitor = await repository.create(visitor.model_dump())
    return VisitorSchema.model_validate(created_visitor)


@app.patch("/visitors/{visitor_id}", response_model=VisitorSchema, status_code=200)
@app.put("/visitors/{visitor_id}", response_model=VisitorSchema, status_code=200)
async def update_visitor(
    visitor_id: int, session: DatabaseSession, visitor: VisitorCreateSchema
) -> JSONResponse:
    """
    Updates a visitor.
    """
    repository = SQLAlchemyRepository(session, VisitorModel)
    updated_visitor = await repository.update(visitor_id, visitor.model_dump())
    return VisitorSchema.model_validate(updated_visitor)


@app.delete("/visitors/{visitor_id}", status_code=204)
async def delete_visitor(visitor_id: int, session: DatabaseSession) -> JSONResponse:
    """
    Deletes a visitor.
    """
    repository = SQLAlchemyRepository(session, VisitorModel)
    await repository.delete(visitor_id)
    return Response(status_code=204)


##### Messages #####


@app.get("/messages", response_model=list[MessageSchema], status_code=200)
async def get_messages(session: DatabaseSession) -> JSONResponse:
    """
    Returns the number of messages to the API.
    """
    repository = SQLAlchemyRepository(session, MessageModel)
    messages = await repository.list()
    return [MessageSchema.model_validate(message) for message in messages]


@app.get("/messages/{message_id}", response_model=MessageSchema, status_code=200)
async def get_message_by_id(message_id: int, session: DatabaseSession) -> JSONResponse:
    """
    Returns a message by ID.
    """
    repository = SQLAlchemyRepository(session, MessageModel)
    message = await repository.get(message_id)
    if message is None:
        return Response(status_code=404)
    return MessageSchema.model_validate(message)


@app.post("/messages", response_model=MessageSchema, status_code=201)
async def create_message(
    session: DatabaseSession, message: MessageCreateSchema
) -> JSONResponse:
    """
    Creates a message.
    """
    repository = SQLAlchemyRepository(session, MessageModel)
    created_message = await repository.create(message.model_dump())
    return MessageSchema.model_validate(created_message)


@app.put("/messages/{message_id}", response_model=MessageSchema, status_code=200)
@app.patch("/messages/{message_id}", response_model=MessageSchema, status_code=200)
async def update_message(
    message_id: int, session: DatabaseSession, message: MessageUpdateSchema
) -> JSONResponse:
    """
    Updates a message.
    """
    repository = SQLAlchemyRepository(session, MessageModel)
    updated_message = await repository.update(message_id, message.model_dump())
    return MessageSchema.model_validate(updated_message)


@app.delete("/messages/{message_id}", status_code=204)
async def delete_message(message_id: int, session: DatabaseSession) -> JSONResponse:
    """
    Deletes a message.
    """
    repository = SQLAlchemyRepository(session, MessageModel)
    await repository.delete(message_id)
    return Response(status_code=204)
