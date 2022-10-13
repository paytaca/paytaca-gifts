
FROM sanicframework/sanic:3.8-latest

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 

WORKDIR /app

COPY pyproject.toml /app

RUN apk add --no-cache make build-base libffi-dev coreutils bash  \
    && pip install -U pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root && \
    wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/8ed92e8cab83cfed76ff012ed4a36cef74b28096/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

COPY . /app

EXPOSE 8000

ENTRYPOINT [ "sh", "entrypoint.sh" ]