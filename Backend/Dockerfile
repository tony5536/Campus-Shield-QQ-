# =========================
# Multi-stage build: CampusShield AI FastAPI Backend
# =========================

# ----------- Builder Stage -----------
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------- Final Stage -----------
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder (global install)
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app
USER appuser

# Environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Optional health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Run the FastAPI app with 4 workers
CMD ["uvicorn", "Backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
