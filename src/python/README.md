# Example Python Application

Here you'll find a simple Python REST API built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/).

## Local Development

In the _root of this project_, install with Poetry:

```shell
# if poetry is not installed
pipx install poetry

# install poetry
poetry install --with dev
```

### Testing

Run the tests for this project with the following:

```shell
poetry run python -m pytest
...

```

## Design

This application is implements ports and adapters (hexagonal) architecture pattern for a simple message board application. The domain data is kept strictly distinct from both the persistence and API layers. The directory structure looks something like this:

```tree
.
├── adapters
│   ├── incoming
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── cli.py
│   │   └── consumer.py
│   ├── outgoing
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── producer.py
│   │   └── relational_database.py
│   └── __init__.py
├── domain
│   ├── __init__.py
│   └── models.py
├── ports
│   ├── __init__.py
│   └── repository.py
├── README.md
├── __init__.py
├── __main__.py
└── main.py
```

### domain

The `domain` folder contains core business logic. In our case, this is the stdlib dataclasses for Python to represent both Messages and Visitors.

### adapters

The `adapters` folder contains both `incoming` and `outgoing` folders for describing how information comes into and departs our application. For our purposes, the `incoming` folder contains the (RESTful) API logic, and the ASGI application that serves as the interaction layer. The `outgoing` folder contains the components for communicating data outside of the application. The main use case a the moment is persisting to a relational database (`relational_database.py`) while other components (`logging.py`, `producer.py`) are stubbed out.

### ports

The `ports` folder contain the specific interfaces for interacting with the domain layer. These are implementations of the domain model that allow different systems to interact; for example, `repository.py` describes the interface for and the SQLAlchemy implementation of repository logic for persisting to relational databases. Adapters use Ports to access Domain objects.
