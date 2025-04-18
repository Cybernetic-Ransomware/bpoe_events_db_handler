FROM python:3.12.10-alpine3.21 AS builder

WORKDIR /src

RUN apk update && apk add --no-cache postgresql-dev gcc musl-dev

RUN python -m pip install --upgrade pip --break-system-packages && \
    pip install uv --break-system-packages

COPY ./pyproject.toml ./uv.lock ./

RUN uv sync --no-cache --no-group dev


FROM python:3.12.10-alpine3.21 AS runtime
LABEL authors="aleksander.marszalki"
LABEL name="bpoe-ocr"

RUN apk update && apk add --no-cache postgresql-dev gcc musl-dev

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

ENV PATH="/src/.venv/bin:/usr/local/bin:$PATH"

WORKDIR /src

COPY --chown=appuser:appgroup ./src .
COPY --from=builder --chown=appuser:appgroup /src/.venv /src/.venv
RUN chmod -R +x /src/.venv/bin/

RUN mkdir /log && chown appuser:appgroup /log

USER appuser

EXPOSE 8080/tcp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
