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
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and directory structure
RUN groupadd -g 10001 botuser && \
    useradd -u 10001 -g botuser -s /bin/bash botuser && \
    mkdir -p /app/storage/logs /app/storage/database /tmp/investment_platform/storage /tmp/investment_platform/backups /tmp/investment_platform/logs && \
    chown -R botuser:botuser /app /tmp/investment_platform

# BUG FIX: Builder runs as root and installs to /root/.local.
# The runtime stage copies these to /home/botuser/.local correctly,
# but the PATH must explicitly include /home/botuser/.local/bin.
COPY --from=builder /root/.local /home/botuser/.local
RUN chown -R botuser:botuser /home/botuser/.local
ENV PATH=/home/botuser/.local/bin:$PATH

# Copy application source
COPY --chown=botuser:botuser . .

USER botuser

# BUG FIX: Health check pings port 8080 which is the aiohttp health server
# started in main_bot.py. This is now correctly implemented.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "-m", "src.main_bot"]
