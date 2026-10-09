# Stage 1: Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    LOG_LEVEL=info

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY src/ ./src/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
