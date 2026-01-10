# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is in the PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["uv", "run", "-m", "app.main"]
