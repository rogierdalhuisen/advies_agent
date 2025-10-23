# Base stage - shared dependencies
FROM python:3.12.12-slim AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install uv for faster dependency management (optional, or use pip)
RUN pip install --no-cache-dir uv

# Install Python dependencies
# If you're using uv:
RUN uv pip install --system --no-cache -r pyproject.toml || \
    pip install --no-cache-dir .

# If you prefer traditional pip and have a requirements.txt:
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/logs


# Development stage
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir debugpy pytest pytest-cov black ruff ipython jupyterlab

# Copy application code
COPY src/ ./src/
COPY main.py ./

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000
EXPOSE 5678

# Default command for development
CMD ["python", "main.py"]


# Production stage
FROM base AS production

# Copy application code
COPY src/ ./src/
COPY main.py ./

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check (adjust endpoint if needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command for production
CMD ["python", "main.py"]
