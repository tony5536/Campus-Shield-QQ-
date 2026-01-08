FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/workspace

WORKDIR /workspace

# Copy Backend directory (entire Backend folder with all subdirectories)
COPY Backend /workspace/Backend

# Install dependencies from Backend/requirements.txt
RUN pip install --upgrade pip --no-cache-dir && \
    pip install -r /workspace/Backend/requirements.txt --no-cache-dir

EXPOSE 8080

# Railway-compatible CMD: 
# - Uses shell to expand $PORT at runtime
# - Correct module path: Backend.app.main:app
# - Fallback to 8080 if $PORT not set
# - 2 workers for Railway's resource constraints
CMD ["sh", "-c", "uvicorn Backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2"]
