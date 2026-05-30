# Use a specific Python version
FROM python:3.12-slim AS builder

# Set the working directory
WORKDIR /app

# Install uv using pip as requested
# This ensures we have the latest version and avoids installation script issues
RUN pip install --no-cache-dir uv

# Copy only the files needed for dependency installation to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies into the .venv directory
# --frozen ensures we use the exact versions from uv.lock
# --no-dev excludes development dependencies
# --no-cache avoids saving cache in the image layer
RUN uv sync --frozen --no-cache --no-dev

# Final runtime stage
FROM python:3.12-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# Ensure the virtual environment's bin is in the PATH
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY *.py /app/
COPY routers /app/routers
# Copy alembic for runtime migrations
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# Create a non-privileged user to run the app
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Cloud Run defaults to port 8080, but we use the PORT env var provided by the environment
ENV PORT=8080

# Command to run the application
# We use uvicorn directly since it's in our venv/bin (which is in PATH)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]