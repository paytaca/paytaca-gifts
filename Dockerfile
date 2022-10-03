
FROM sanicframework/sanic:3.8-latest

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 

WORKDIR /app

COPY pyproject.toml /app

RUN apk add --no-cache make build-base libffi-dev \
    && pip install -U pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

COPY . /app

EXPOSE 8000

CMD [ "sanic", "main.app" ]