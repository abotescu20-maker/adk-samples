# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

ENV POETRY_VERSION=1.8.4 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies and Poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

# Copy project metadata first for better build caching
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy source code
COPY nutrigenomics_rag ./nutrigenomics_rag
COPY tests ./tests

# Install the local package itself (so entrypoints are available if defined later)
RUN poetry install --no-interaction --no-ansi

ENTRYPOINT ["poetry", "run", "adk", "run", "nutrigenomics_rag"]
