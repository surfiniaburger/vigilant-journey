# Use the official Python 3.12 slim image, which is based on Debian
FROM python:3.12-slim

# Use bash and exit on pipeline failures
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install uv, a modern Python package installer, from its official release
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- MODIFIED SECTION ---
# Install system dependencies.
# Version pinning is removed to allow apt to resolve the correct packages for the
# underlying OS (Debian 13 "Trixie"), making the build more robust.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For matplotlib/Pillow
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    # For opencv-python (cv2). libgl1 is the modern replacement for libgl1-mesa-glx
    libgl1 \
    libglib2.0-0 \
    # General build tools and network utilities
    curl \
    build-essential \
    # Install NodeSource repo for a recent version of Node.js
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    # Install Node.js from the newly added repository
    && apt-get install -y --no-install-recommends nodejs \
    # Clean up APT caches to keep the final image smaller
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the application directory
WORKDIR /app

# Copy dependency definition files first for better caching
COPY pyproject.toml requirements.txt* ./

# Create virtual environment and install dependencies
RUN uv venv && \
    uv pip install -r requirements.txt

# Add the virtual environment's bin directory to the system's PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application source code
COPY . .

# Command to run the Gunicorn server with Uvicorn workers.
# This is a robust way to run an ASGI app in production.
CMD ["/app/.venv/bin/gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
