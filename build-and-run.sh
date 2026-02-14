#!/bin/bash
# Build and run WhisperX Docker container

set -e

echo "🐳 WhisperX Docker Build & Run Script"
echo "====================================="
echo ""

# Parse arguments
BUILD_TYPE="${1:-cpu}"
ACTION="${2:-build-run}"

if [ "$BUILD_TYPE" = "gpu" ]; then
    DOCKERFILE="Dockerfile.gpu"
    IMAGE_TAG="whisperx:gpu"
    GPU_FLAGS="--gpus all"
    echo "Building GPU version..."
else
    DOCKERFILE="Dockerfile"
    IMAGE_TAG="whisperx:cpu"
    GPU_FLAGS=""
    echo "Building CPU version..."
fi

# Build the image
if [ "$ACTION" = "build" ] || [ "$ACTION" = "build-run" ]; then
    echo ""
    echo "📦 Building Docker image..."
    docker build -f $DOCKERFILE -t $IMAGE_TAG .
    echo "✅ Build complete!"
fi

# Run the container
if [ "$ACTION" = "run" ] || [ "$ACTION" = "build-run" ]; then
    echo ""
    echo "🚀 Starting WhisperX API server..."
    echo ""
    echo "Access the API at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
    echo "Press Ctrl+C to stop"
    echo ""

    # Load environment variables
    if [ -f .env ]; then
        echo "Loading environment variables from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    fi

    docker run -it --rm \
        $GPU_FLAGS \
        -p 8000:8000 \
        -v $(pwd)/input:/app/input \
        -v $(pwd)/output:/app/output \
        -e HF_TOKEN=${HF_TOKEN:-} \
        -e WHISPERX_MODEL=${WHISPERX_MODEL:-base} \
        -e PORT=8000 \
        $IMAGE_TAG
fi

echo ""
echo "Usage:"
echo "  $0 [cpu|gpu] [build|run|build-run]"
echo ""
echo "Examples:"
echo "  $0 cpu build-run    # Build and run CPU version"
echo "  $0 gpu build        # Build GPU version only"
echo "  $0 cpu run          # Run existing CPU image"
