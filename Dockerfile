FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir uv \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && uv pip install --system -e .

COPY . .

EXPOSE 8000
