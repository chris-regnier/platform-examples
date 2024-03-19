ARG IMAGE_PYTHON_VERSION=3.12

# DEPENDENCIES LAYER
FROM python:$IMAGE_PYTHON_VERSION-slim as dependencies

COPY pyproject.toml poetry.lock ./

RUN mkdir -p /app \
    && python -m pip install pipx \
    && python -m pipx ensurepath \
    && pipx install poetry

WORKDIR /app

ENV PATH="/root/.local/bin:${PATH}"
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# RUNTIME LAYER
FROM python:$IMAGE_PYTHON_VERSION-slim as runtime
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV IMAGE_PYTHON_VERSION=$IMAGE_PYTHON_VERSION

COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/

RUN useradd app -m -u 1000 -s /bin/bash

WORKDIR /app

USER 1000:1000

# COPY --from=dependencies --chown=1000:1000 /root/.cache/pypoetry/virtualenvs /home/app/.cache
COPY --chown=1000:1000 src/ /app/src

CMD [ "python", "-m", "src.python", "--host", "0.0.0.0" ]