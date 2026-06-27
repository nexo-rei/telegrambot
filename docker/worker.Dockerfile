# Stage 1: Builder
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

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

# Install runtime dependencies and tini
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ffmpeg \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and directory structure
RUN groupadd -g 10001 workeruser && \
    useradd -u 10001 -g workeruser -s /bin/bash workeruser && \
    mkdir -p /app/storage/logs /app/storage/database && \
    chown -R workeruser:workeruser /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/workeruser/.local
ENV PATH=/home/workeruser/.local/bin:$PATH

# Copy application source
COPY --chown=workeruser:workeruser . .

USER workeruser

# Healthcheck: Celery worker specific check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD celery -A src.main_worker inspect ping -d celery@${HOSTNAME} || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "-m", "src.main_worker"]
