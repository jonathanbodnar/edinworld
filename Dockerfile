FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY pyproject.toml .

FROM base AS api
EXPOSE 8001
CMD ["uvicorn", "src.canon.api.app:app", "--host", "0.0.0.0", "--port", "8001"]

FROM base AS worker
CMD ["python", "-m", "src.canon.workers.runner", "all"]

FROM base AS migrate
CMD ["alembic", "upgrade", "head"]
