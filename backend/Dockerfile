# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.2

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy poetry project files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only=main

# Copy application code
COPY app/ ./app/

# Copy environment file (if exists)
COPY .env* ./

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application with configuration from environment
CMD ["sh", "-c", "poetry run uvicorn app.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}"]
