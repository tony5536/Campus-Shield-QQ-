# ==========================================
# Stage 1: Build Frontend (React)
# ==========================================
FROM node:18-alpine as frontend_build

WORKDIR /app/frontend

# Copy package files first for better caching
COPY dashboard/package.json dashboard/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the frontend source code
COPY dashboard ./

# Build the React application
RUN npm run build

# ==========================================
# Stage 2: Final Backend Image
# ==========================================
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/workspace

WORKDIR /workspace

# Install system dependencies if needed (e.g. for some python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy Backend directory
COPY Backend /workspace/Backend

# Copy built frontend assets from Stage 1
# We place them in a known directory, e.g., /workspace/static_build
COPY --from=frontend_build /app/frontend/build /workspace/static_build

# Install Python dependencies
RUN pip install --upgrade pip --no-cache-dir && \
    pip install -r /workspace/Backend/requirements.txt --no-cache-dir

# Expose port (8080 is standard for many cloud providers)
EXPOSE 8080

# Run command
# 1. We use the shell form to allow variable expansion (${PORT:-8080})
# 2. We point to the app module correctly
CMD ["sh", "-c", "uvicorn Backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2"]
