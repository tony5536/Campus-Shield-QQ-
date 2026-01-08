# =========================
# Multi-stage build: CampusShield AI FastAPI Backend
# Production-ready for Railway deployment
# =========================

# ----------- Builder Stage -----------
FROM python:3.13-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements for efficient caching
COPY requirements.txt .

# Install Python dependencies globally in builder stage
RUN pip install --no-cache-dir --no-warn-script-location \
    -r requirements.txt

# ----------- Final Stage -----------
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python site-packages from builder to keep image lean
COPY --from=builder /usr/local /usr/local

# Create non-root user with proper permissions (Railway-compatible)
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app /usr/local/lib && \
    chmod -R 755 /usr/local/lib

# Copy application code and set proper ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user for runtime
USER appuser

# Python environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Expose port 8000 for local testing
EXPOSE 8000

# Health check using curl (works without requests library)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Railway-compatible CMD: respects $PORT environment variable
# Uses 4 workers with uvicorn for production load handling
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
