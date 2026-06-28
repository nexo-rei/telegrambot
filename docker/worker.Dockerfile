# Stage 1: Builder
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/calls/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Runtime
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    TZ=Africa/Lagos \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and directory structure
RUN groupadd -g 10001 workeruser && \
    useradd -u 10001 -g workeruser -s /bin/bash workeruser && \
    mkdir -p /app/storage/logs /app/storage/database /tmp/investment_platform/storage /tmp/investment_platform/backups /tmp/investment_platform/logs && \
    chown -R workeruser:workeruser /app /tmp/investment_platform

# BUG FIX: Same PATH issue as bot.Dockerfile — chown the copied .local directory
COPY --from=builder /root/.local /home/workeruser/.local
RUN chown -R workeruser:workeruser /home/workeruser/.local
ENV PATH=/home/workeruser/.local/bin:$PATH

COPY --chown=workeruser:workeruser . .

USER workeruser

# BUG FIX: Celery inspect ping health check requires celery to be on PATH,
# which it now is via /home/workeruser/.local/bin
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD celery -A src.main_worker inspect ping -d celery@${HOSTNAME} || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

# BUG FIX: Celery workers must be started with the `celery worker` command,
# not `python -m src.main_worker`. The module defines the app; celery CLI starts it.
CMD ["celery", "-A", "src.main_worker.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
