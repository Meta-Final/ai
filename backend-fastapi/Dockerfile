FROM    python:3.12.7-alpine3.19

WORKDIR /app

RUN     apk update && apk upgrade
RUN apk add --no-cache \
    dumb-init \
    gcc \
    musl-dev \
    linux-headers \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    bash

RUN pip install --no-cache-dir --upgrade \
    "fastapi[all]" \
    python-multipart \
    "python-jose[cryptography]" \
    "passlib[bcrypt]" \
    sqlalchemy \
    alembic \
    "pydantic[email]" \
    pytest \
    httpx \
    black \
    isort \
    flake8 \
    fastapi-users \
    fastapi-utils \
    slowapi \
    fastapi-sqlalchemy \
    fastapi-cache \
    uvicorn \
    gunicorn

#DEV PURPOSE ONLY, CHANGE AS SOON AS POSSIBLE.
CMD ["sleep", "infinity"]