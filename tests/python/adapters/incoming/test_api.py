"""
Tests for the API adapter.
"""

import os
from fastapi import FastAPI
import pytest

from fastapi.testclient import TestClient

VISITOR_NAMES = ("John", "Jane")
VISITOR_EMAILS = ("John@cto.com", "jane@ceo.com")


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch):
    """
    Fixture for the FastAPI application.
    """
    from src.python.adapters.incoming.api import app

    db_name = "local-test.sqlite"

    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_name}")
    yield app
    os.remove(db_name)


@pytest.fixture
def client(app: FastAPI):
    """
    Fixture for the FastAPI test client.
    """
    return TestClient(app)


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World"}


##### Visitors #####


@pytest.mark.parametrize("name", VISITOR_NAMES)
@pytest.mark.parametrize("email", VISITOR_EMAILS)
def test_visitors_get(client: TestClient, name: str, email: str):

    response = client.get("/visitors", params={"name": name, "email": email})
    assert response.status_code == 200
    visitors = response.json()
    assert len(visitors) == 0


@pytest.mark.parametrize("name", VISITOR_NAMES)
@pytest.mark.parametrize("email", VISITOR_EMAILS)
def test_visitors_create(client: TestClient, name: str, email: str):

    create_response = client.post("/visitors", json={"name": name, "email": email})
    assert create_response.status_code == 201
    visitor = create_response.json()
    assert visitor["name"] == name
    assert visitor["email"] == email
    assert visitor["messages"] == []
    assert visitor["id"] > 0


@pytest.mark.parametrize("name", VISITOR_NAMES)
@pytest.mark.parametrize("email", VISITOR_EMAILS)
def test_visitors_get_by_id(client: TestClient, name: str, email: str):
    create_response = client.post("/visitors", json={"name": name, "email": email})
    assert create_response.status_code == 201
    visitor = create_response.json()

    response = client.get(f"/visitors/{visitor['id']}")
    assert response.status_code == 200
    assert response.json() == visitor


def test_visitors_get_by_id_404(client: TestClient, faker):
    dummy_id = faker.random_int(1000, 2000)
    response = client.get(f"/visitors/{dummy_id}")
    assert response.status_code == 404


@pytest.mark.parametrize("name", VISITOR_NAMES)
@pytest.mark.parametrize("email", VISITOR_EMAILS)
@pytest.mark.parametrize("method", ("put", "patch"))
def test_visitors_update(client: TestClient, name: str, email: str, method: str):
    create_response = client.post("/visitors", json={"name": name, "email": email})
    assert create_response.status_code == 201
    visitor = create_response.json()

    http_method = getattr(client, method)

    new_name = f"{name} updated"
    new_email = f"{email} updated"
    update_response = http_method(
        f"/visitors/{visitor['id']}", json={"name": new_name, "email": new_email}
    )
    assert update_response.status_code == 200
    updated_visitor = update_response.json()
    assert updated_visitor["name"] == new_name
    assert updated_visitor["email"] == new_email
    assert updated_visitor["id"] == visitor["id"]


@pytest.mark.parametrize("name", VISITOR_NAMES)
@pytest.mark.parametrize("email", VISITOR_EMAILS)
def test_visitors_delete(client: TestClient, name: str, email: str):
    create_response = client.post("/visitors", json={"name": name, "email": email})
    assert create_response.status_code == 201
    visitor = create_response.json()

    response = client.delete(f"/visitors/{visitor['id']}")
    assert response.status_code == 204

    response = client.get(f"/visitors/{visitor['id']}")
    assert response.status_code == 404


##### Messages #####


def test_messages_get(client: TestClient):
    response = client.get("/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 0


def test_messages_create(client: TestClient, faker):
    content = faker.text()
    sender = faker.name()
    receiver = faker.name()

    visitor_name = faker.name()
    visitor_email = faker.email()
    create_visitor_response = client.post(
        "/visitors", json={"name": visitor_name, "email": visitor_email}
    )
    assert create_visitor_response.status_code == 201
    visitor_id = create_visitor_response.json()["id"]

    create_response = client.post(
        "/messages",
        json={
            "content": content,
            "sender": sender,
            "receiver": receiver,
            "visitor_id": visitor_id,
        },
    )
    assert create_response.status_code == 201, create_response.text
    message = create_response.json()
    assert message["content"] == content
    assert message["sender"] == sender
    assert message["receiver"] == receiver
    assert message["visitor_id"] == visitor_id
    assert message["id"] > 0


def test_messages_get_by_id(client: TestClient, faker):
    content = faker.text()
    sender = faker.name()
    receiver = faker.name()

    visitor_name = faker.name()
    visitor_email = faker.email()
    create_visitor_response = client.post(
        "/visitors", json={"name": visitor_name, "email": visitor_email}
    )
    assert create_visitor_response.status_code == 201
    visitor_id = create_visitor_response.json()["id"]

    create_response = client.post(
        "/messages",
        json={
            "content": content,
            "sender": sender,
            "receiver": receiver,
            "visitor_id": visitor_id,
        },
    )
    assert create_response.status_code == 201
    message = create_response.json()
    message_id = message["id"]

    response = client.get(f"/messages/{message_id}")
    assert response.status_code == 200
    assert response.json() == message


def test_messages_get_by_id_404(client: TestClient, faker):
    dummy_id = faker.random_int(1000, 2000)
    response = client.get(f"/messages/{dummy_id}")
    assert response.status_code == 404


def test_messages_update(client: TestClient, faker):
    content = faker.text()
    sender = faker.name()
    receiver = faker.name()

    visitor_name = faker.name()
    visitor_email = faker.email()
    create_visitor_response = client.post(
        "/visitors", json={"name": visitor_name, "email": visitor_email}
    )
    assert create_visitor_response.status_code == 201
    visitor_id = create_visitor_response.json()["id"]

    create_response = client.post(
        "/messages",
        json={
            "content": content,
            "sender": sender,
            "receiver": receiver,
            "visitor_id": visitor_id,
        },
    )
    assert create_response.status_code == 201
    message = create_response.json()

    new_content = f"{content} updated"
    new_sender = f"{sender} updated"
    new_receiver = f"{receiver} updated"
    update_response = client.put(
        f"/messages/{message['id']}",
        json={"content": new_content, "sender": new_sender, "receiver": new_receiver},
    )
    assert update_response.status_code == 200
    updated_message = update_response.json()
    assert updated_message["content"] == new_content
    assert updated_message["sender"] == new_sender
    assert updated_message["receiver"] == new_receiver
    assert updated_message["id"] == message["id"]


def test_messages_delete(client: TestClient, faker):
    content = faker.text()
    sender = faker.name()
    receiver = faker.name()

    visitor_name = faker.name()
    visitor_email = faker.email()
    create_visitor_response = client.post(
        "/visitors", json={"name": visitor_name, "email": visitor_email}
    )
    assert create_visitor_response.status_code == 201
    visitor_id = create_visitor_response.json()["id"]

    create_response = client.post(
        "/messages",
        json={
            "content": content,
            "sender": sender,
            "receiver": receiver,
            "visitor_id": visitor_id,
        },
    )
    assert create_response.status_code == 201
    message = create_response.json()

    response = client.delete(f"/messages/{message['id']}")
    assert response.status_code == 204

    response = client.get(f"/messages/{message['id']}")
    assert response.status_code == 404

    response = client.delete(f"/visitors/{visitor_id}")
    assert response.status_code == 204
