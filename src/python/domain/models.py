import functools
from dataclasses import dataclass, field
from datetime import datetime
from types import NoneType
from typing import Optional

base_field = functools.partial(field, kw_only=True, default=None)


@dataclass
class BaseModel:
    id: int = base_field()
    created_at: datetime = base_field()
    updated_at: datetime = base_field()
    deleted_at: Optional[datetime | NoneType] = base_field()


@dataclass
class Visitor(BaseModel):
    name: str
    email: str
    messages: Optional[list["Message"]] = field(default_factory=list)


@dataclass
class Message(BaseModel):
    content: str
    sender: str
    receiver: str
    visitor_id: int = field(kw_only=True, default=None)
