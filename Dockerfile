FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir ".[dev]"

COPY alembic.ini ./
COPY db ./db
COPY services ./services
COPY shared ./shared
COPY scripts ./scripts

CMD ["python", "-m", "services.consumer.main"]
