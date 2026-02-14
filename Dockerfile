# WhisperX Docker Image for Render Deployment
# CPU-optimized version (for GPU version, use Dockerfile.gpu)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install whisperX and dependencies
# Using CPU version of PyTorch for Render (no GPU)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -e .

# Install API dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Create directories for input/output
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV WHISPERX_CACHE_DIR=/app/models

# Expose port for API
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "api.py"]
