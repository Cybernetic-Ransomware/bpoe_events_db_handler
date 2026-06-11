# syntax=docker/dockerfile:1.7
FROM python:3.12.10-alpine3.21 AS builder

WORKDIR /src

RUN apk update && apk add --no-cache postgresql-dev gcc musl-dev

RUN pip install uv --break-system-packages

COPY ./pyproject.toml ./uv.lock ./

ENV UV_PYTHON_PREFERENCE=only-system
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --no-group dev


FROM python:3.12.10-alpine3.21 AS runtime
LABEL authors="aleksander.marszalki"
LABEL name="bpoe-events-db-handler"

RUN apk update && apk add --no-cache postgresql-dev gcc musl-dev

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

ENV PATH="/src/.venv/bin:/usr/local/bin:$PATH"

WORKDIR /src

COPY --from=builder --chown=appuser:appgroup /src/.venv /src/.venv
COPY --chown=appuser:appgroup ./src .
RUN chmod -R +x /src/.venv/bin/

RUN mkdir /log && chown appuser:appgroup /log

COPY ./docker/init_alembic.sh /src/init_alembic.sh
RUN chmod +x /src/init_alembic.sh

USER appuser

EXPOSE 8080/tcp

ENTRYPOINT ["/src/init_alembic.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
