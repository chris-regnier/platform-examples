import pytest
from polyfactory import Ignore, Use, pytest_plugin
from polyfactory.factories import DataclassFactory

from src.python.domain import models


class FactoryIgnoredMixin:
    __set_as_default_factory_for_type__ = True

    id = Ignore()
    created_at = Ignore()
    updated_at = Ignore()
    deleted_at = Ignore()


class VisitorFactory(DataclassFactory[models.Visitor], FactoryIgnoredMixin):
    messages = []


class MessageFactory(DataclassFactory[models.Message], FactoryIgnoredMixin):
    visitor = Ignore()
    visitor_id = Ignore()


visitor_factory = pytest_plugin.register_fixture(VisitorFactory)
message_factory = pytest_plugin.register_fixture(MessageFactory)
