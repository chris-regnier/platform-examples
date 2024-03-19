"""
Tests the models for backward compatibility.
"""

import datetime

import pytest

from . import message_factory, visitor_factory  # imported as a fixtures

visitor_factory, message_factory = visitor_factory, message_factory


def _test_base_model(base_model):
    assert base_model.id
    assert base_model.created_at
    assert base_model.updated_at
    assert base_model.deleted_at is None or isinstance(
        base_model.deleted_at, datetime.datetime
    )

    assert isinstance(base_model.id, int)
    assert isinstance(base_model.created_at, datetime.datetime)
    assert isinstance(base_model.updated_at, datetime.datetime)


def test_visitor(visitor_factory):
    visitor = visitor_factory.build()
    assert visitor.name
    assert visitor.email

    assert isinstance(visitor.name, str)
    assert isinstance(visitor.email, str)

    _test_base_model(visitor)


def test_message(message_factory):
    message = message_factory.build()

    assert message.content
    assert message.sender
    assert message.receiver

    assert isinstance(message.content, str)
    assert isinstance(message.sender, str)
    assert isinstance(message.receiver, str)

    _test_base_model(message)
