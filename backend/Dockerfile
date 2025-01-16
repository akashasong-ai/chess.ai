FROM python:3.12 as builder

WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml ./
RUN poetry install --no-dev --no-root

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV HOST="0.0.0.0"
ENV PORT="8080"

CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
