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
RUN groupadd -g 10001 cronuser && \
    useradd -u 10001 -g cronuser -s /bin/bash cronuser && \
    mkdir -p /app/storage/logs /app/storage/database && \
    chown -R cronuser:cronuser /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/cronuser/.local
ENV PATH=/home/cronuser/.local/bin:$PATH

# Copy application source
COPY --chown=cronuser:cronuser . .

USER cronuser

# Healthcheck: Verify the scheduler process is running
HEALTHCHECK --interval=60s --timeout=15s --start-period=10s --retries=3 \
    CMD ps aux | grep "[p]ython -m src.main_cron" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "-m", "src.main_cron"]
