# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.5 \
    GENETIC_HEALTH_COACH_HOST=0.0.0.0 \
    GENETIC_HEALTH_COACH_PORT=8000

WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install "poetry==${POETRY_VERSION}"

# Copy project metadata first to leverage Docker layer caching
COPY pyproject.toml README.md ./

# Configure Poetry to avoid virtualenv creation inside the container
RUN poetry config virtualenvs.create false

# Install only runtime dependencies before copying the sources
RUN poetry install --only main --no-root

# Copy the application source code and sample data
COPY genetic_health_coach ./genetic_health_coach
COPY sample_data ./sample_data

# Install the project itself so console scripts are registered
RUN poetry install --only main

EXPOSE 8000

CMD ["genetic-health-coach-demo"]
