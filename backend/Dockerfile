# =============================================================================
# Stage 1: Builder - Install dependencies
# =============================================================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies for psycopg (PostgreSQL driver)
# These are needed at build time but not runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
# This layer will only rebuild if requirements.txt changes
COPY requirements.txt .

# Install Python dependencies to /app/venv
# Using --no-cache-dir reduces image size by not storing pip cache
# Using venv ensures clean separation of dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Minimal production image
# =============================================================================
FROM python:3.11-slim

# Metadata labels for image identification and tracking
LABEL maintainer="Todo App Team" \
      version="1.0.0" \
      description="FastAPI Todo Backend with AI Chatbot - Kubernetes Ready" \
      org.opencontainers.image.source="https://github.com/your-org/todo-app"

# Set working directory
WORKDIR /app

# Install only runtime dependencies (libpq for PostgreSQL client)
# Keep image minimal by removing apt cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python virtual environment from builder stage
# This contains all installed packages without build dependencies
COPY --from=builder /app/venv /app/venv

# Copy application code
# This is done last to maximize Docker layer caching
COPY . .

# Create non-root user for security (UID 1000 as specified)
# Running as non-root is a Kubernetes security best practice
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables for Python optimization
# PYTHONUNBUFFERED: Ensure logs are flushed immediately (critical for container logs)
# PYTHONDONTWRITEBYTECODE: Don't create .pyc files (reduces image size)
# PATH: Add venv to PATH so python/pip commands use virtualenv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/venv/bin:$PATH"

# Expose port 8000 for FastAPI application
# This is the default uvicorn port and matches health check requirements
EXPOSE 8000

# Health check configuration for Kubernetes liveness/readiness probes
# Checks /health endpoint every 30s, starts after 30s, times out after 10s
# Kubernetes will use this to determine if container is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Run uvicorn server
# --host 0.0.0.0: Listen on all interfaces (required for container networking)
# --port 8000: Standard FastAPI port
# --workers 1: Single worker for development (Kubernetes handles scaling)
# --log-level info: Structured logging for observability
# NOTE: SIGTERM handling is automatic with uvicorn for graceful shutdown
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
