# syntax=docker/dockerfile:1
# PDS Containerfile - Hardened Python Runtime
FROM python:3.12-slim-bookworm AS base

# Prevent Python from writing .pyc files to disk and disable stdout buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for cryptography compilation
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pinned Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create an unprivileged non-root user (UID 10001)
RUN groupadd -g 10001 pdsgroup \
    && useradd -u 10001 -g pdsgroup -s /sbin/nologin -d /app pdsuser \
    && chown -R pdsuser:pdsgroup /app

# Copy application source code
COPY --chown=pdsuser:pdsgroup ./app /app/app

# Drop root privileges
USER pdsuser

EXPOSE 8000

# Healthcheck to verify service availability
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
