# WhisperX Docker Image for Railway/Render Deployment
# CPU-optimized version (for GPU version, use Dockerfile.gpu)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY pyproject.toml requirements-api.txt ./
COPY whisperx/__init__.py whisperx/

# Install whisperX and dependencies
# Using CPU version of PyTorch - optimized for faster builds
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.5.0 \
    torchaudio==2.5.0 \
    --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    fastapi==0.104.0 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    faster-whisper>=1.1.1 \
    ctranslate2>=4.5.0 \
    pyannote-audio>=4.0.0 \
    transformers>=4.48.0 \
    nltk>=3.9.1 \
    numpy>=2.1.0 \
    pandas>=2.2.3 \
    omegaconf>=2.3.0

# Copy rest of the application
COPY . .

# Create directories for input/output
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV WHISPERX_CACHE_DIR=/app/models

# Expose port for API
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "api.py"]
