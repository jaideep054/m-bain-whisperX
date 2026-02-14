# WhisperX Docker Deployment Guide

This guide explains how to deploy WhisperX using Docker, both locally and on Render.

## 📋 Files Created

- **Dockerfile** - CPU-optimized Docker image (for Render)
- **Dockerfile.gpu** - GPU-enabled Docker image (for local/GPU servers)
- **docker-compose.yml** - Local development setup
- **render.yaml** - Render deployment configuration
- **api.py** - FastAPI web service wrapper
- **requirements-api.txt** - Additional API dependencies
- **.dockerignore** - Files to exclude from Docker build

## 🚀 Deployment Options

### Option 1: Deploy to Render (Recommended for Production)

#### Step 1: Update Dockerfile for API Mode

Add FastAPI dependencies to the Dockerfile. Edit [Dockerfile](Dockerfile) and add this line before the CMD:

```dockerfile
# Install API dependencies
RUN pip install --no-cache-dir -r requirements-api.txt
```

Then change the CMD to:

```dockerfile
CMD ["python", "api.py"]
```

#### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add Docker deployment files"
git push origin main
```

#### Step 3: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and set up your service
5. Set environment variables in Render dashboard:
   - `HF_TOKEN` - Your Hugging Face token (for speaker diarization)
   - `WHISPERX_MODEL` - Model size: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`

#### Step 4: Test Your API

Once deployed, test the API:

```bash
curl https://your-app.onrender.com/health
```

Transcribe an audio file:

```bash
curl -X POST https://your-app.onrender.com/transcribe \
  -F "file=@audio.mp3" \
  -F "language=en" \
  -F "diarize=true"
```

### Option 2: Local Docker Build & Run

#### CPU Version (No GPU)

```bash
# Build the image
docker build -t whisperx:latest .

# Run with a sample audio file
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  whisperx:latest \
  whisperx /app/input/audio.mp3 --output_dir /app/output --model base
```

#### GPU Version (Requires NVIDIA GPU)

```bash
# Build GPU image
docker build -f Dockerfile.gpu -t whisperx:gpu .

# Run with GPU support
docker run --gpus all \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  whisperx:gpu \
  whisperx /app/input/audio.mp3 --output_dir /app/output --model large-v2 --device cuda
```

### Option 3: Docker Compose (Local Development)

```bash
# Create input/output directories
mkdir -p input output

# Add your audio file to input directory
cp /path/to/audio.mp3 input/

# Run with CPU
docker-compose up whisperx-cpu

# Or run with GPU
docker-compose up whisperx-gpu
```

## 🌐 API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model": "base",
  "device": "cpu"
}
```

### GET /
API information

### POST /transcribe
Transcribe audio file

**Parameters:**
- `file` (required) - Audio file (mp3, wav, m4a, flac, etc.)
- `language` (optional) - Language code (e.g., "en", "es", "fr")
- `batch_size` (optional) - Batch size for inference (default: 8)
- `diarize` (optional) - Enable speaker diarization (default: false)
- `min_speakers` (optional) - Minimum number of speakers
- `max_speakers` (optional) - Maximum number of speakers

**Example:**
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@sample.mp3" \
  -F "language=en" \
  -F "batch_size=8" \
  -F "diarize=true" \
  -F "min_speakers=2" \
  -F "max_speakers=3"
```

**Response:**
```json
{
  "status": "success",
  "language": "en",
  "segments": [
    {
      "start": 0.5,
      "end": 3.2,
      "text": "Hello, this is a test.",
      "speaker": "SPEAKER_00"
    }
  ]
}
```

## ⚙️ Configuration

### Environment Variables

- `PORT` - API server port (default: 8000)
- `WHISPERX_MODEL` - Model to use: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`
- `HF_TOKEN` - Hugging Face token for speaker diarization
- `WHISPERX_CACHE_DIR` - Directory for model cache (default: /app/models)

### Model Sizes & Requirements

| Model | Parameters | VRAM (GPU) | RAM (CPU) | Speed |
|-------|-----------|-----------|----------|-------|
| tiny | 39M | ~1GB | ~2GB | ~32x |
| base | 74M | ~1GB | ~2GB | ~16x |
| small | 244M | ~2GB | ~4GB | ~6x |
| medium | 769M | ~5GB | ~8GB | ~2x |
| large-v2 | 1550M | ~8GB | ~16GB | ~1x |
| large-v3 | 1550M | ~8GB | ~16GB | ~1x |

## 🔒 Security Notes

1. **Never commit your HF_TOKEN** - Set it in Render dashboard or use `.env` file locally
2. **Rate limiting** - Consider adding rate limiting for production API
3. **File size limits** - The API accepts files up to ~100MB by default
4. **Authentication** - Add authentication for production use

## 🐛 Troubleshooting

### Issue: Out of Memory

**Solution:** Use a smaller model or reduce batch size:
```bash
docker run whisperx:latest \
  whisperx audio.mp3 --model tiny --batch_size 4
```

### Issue: Speaker Diarization Not Working

**Solution:** Make sure you've set `HF_TOKEN` and accepted the model agreement:
1. Go to https://huggingface.co/pyannote/speaker-diarization-community-1
2. Accept the user agreement
3. Generate a token at https://huggingface.co/settings/tokens
4. Set the token as `HF_TOKEN` environment variable

### Issue: Slow Processing on Render

**Solution:** Render's free/starter plans use CPU. For faster processing:
1. Upgrade to a larger Render plan
2. Use a smaller model (`tiny` or `base`)
3. Process shorter audio clips

## 📚 Additional Resources

- [WhisperX GitHub](https://github.com/m-bain/whisperX)
- [Render Documentation](https://render.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📝 Example Usage

### Python Client

```python
import requests

url = "https://your-app.onrender.com/transcribe"

with open("audio.mp3", "rb") as f:
    files = {"file": f}
    data = {
        "language": "en",
        "diarize": True,
        "min_speakers": 2,
        "max_speakers": 3
    }
    response = requests.post(url, files=files, data=data)
    result = response.json()
    print(result)
```

### JavaScript Client

```javascript
const formData = new FormData();
formData.append('file', audioFile);
formData.append('language', 'en');
formData.append('diarize', 'true');

fetch('https://your-app.onrender.com/transcribe', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🎯 Next Steps

1. **Add authentication** - Implement API key authentication
2. **Add caching** - Cache transcription results
3. **Add queue system** - Use Redis/Celery for async processing
4. **Add webhooks** - Notify clients when processing is complete
5. **Add database** - Store transcription history

