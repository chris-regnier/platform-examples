import pytest
from polyfactory import pytest_plugin
from polyfactory.factories import DataclassFactory

from src.python.domain import models


class VisitorFactory(DataclassFactory[models.Visitor]):
    __set_as_default_factory_for_type__ = True


class MessageFactory(DataclassFactory[models.Message]):
    __set_as_default_factory_for_type__ = True


visitor_factory = pytest_plugin.register_fixture(VisitorFactory)
message_factory = pytest_plugin.register_fixture(MessageFactory)
