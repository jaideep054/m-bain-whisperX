# 🐳 WhisperX Docker Deployment - Complete Setup

Complete Docker deployment setup for WhisperX with API support and Render deployment.

## 📦 What's Included

This Docker setup includes everything you need to deploy WhisperX:

### Core Files
- **[Dockerfile](Dockerfile)** - Production-ready CPU Docker image with FastAPI
- **[Dockerfile.gpu](Dockerfile.gpu)** - GPU-enabled Docker image for CUDA support
- **[docker-compose.yml](docker-compose.yml)** - Local development environment
- **[.dockerignore](.dockerignore)** - Optimized Docker build context

### API & Deployment
- **[api.py](api.py)** - FastAPI web service wrapper for WhisperX
- **[requirements-api.txt](requirements-api.txt)** - API dependencies
- **[render.yaml](render.yaml)** - One-click Render deployment configuration

### Utilities
- **[build-and-run.sh](build-and-run.sh)** - Build and run Docker containers
- **[test-api.sh](test-api.sh)** - Test the API endpoints
- **[.env.example](.env.example)** - Environment variable template

### Documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **This file** - Overview and architecture

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Client                        │
│           (Browser, cURL, Python, etc)          │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────┐
│              FastAPI Server                     │
│              (api.py - Port 8000)               │
├─────────────────────────────────────────────────┤
│           WhisperX Processing Engine            │
│  ┌─────────────────────────────────────────┐   │
│  │ 1. Audio Loading                        │   │
│  │ 2. Transcription (Whisper + CTranslate2)│   │
│  │ 3. Alignment (Wav2Vec2)                 │   │
│  │ 4. Speaker Diarization (PyAnnote)       │   │
│  └─────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          Model Cache & Storage                  │
│         (/app/models - Persistent Disk)         │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Deploy Commands

### Build Docker Image
```bash
# CPU version (for Render)
docker build -t whisperx:latest .

# GPU version
docker build -f Dockerfile.gpu -t whisperx:gpu .
```

### Run Locally
```bash
# Using helper script
./build-and-run.sh cpu build-run

# Or manually
docker run -p 8000:8000 \
  -e WHISPERX_MODEL=base \
  -e HF_TOKEN=your_token \
  whisperx:latest
```

### Deploy to Render
```bash
# Option 1: Push to GitHub and use Render Blueprint
git add .
git commit -m "Add WhisperX Docker setup"
git push origin main
# Then connect repo in Render dashboard

# Option 2: Use Render CLI
render deploy
```

## 🎯 API Endpoints

### Health Check
```bash
GET /health
```

### Transcribe Audio
```bash
POST /transcribe
Content-Type: multipart/form-data

Parameters:
  - file: audio file (required)
  - language: language code (optional)
  - batch_size: int (default: 8)
  - diarize: boolean (default: false)
  - min_speakers: int (optional)
  - max_speakers: int (optional)
```

### API Documentation
```bash
GET /docs       # Swagger UI
GET /redoc      # ReDoc UI
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | API server port | 8000 | No |
| `WHISPERX_MODEL` | Model size (tiny/base/small/medium/large-v2/large-v3) | base | No |
| `HF_TOKEN` | Hugging Face token for diarization | - | For diarization |
| `WHISPERX_CACHE_DIR` | Model cache directory | /app/models | No |
| `DEVICE` | Device (cpu/cuda) | Auto-detect | No |
| `COMPUTE_TYPE` | Compute type (float16/float32/int8) | Auto-detect | No |

### Set Environment Variables

**Local (.env file)**:
```bash
cp .env.example .env
# Edit .env and add your values
```

**Render Dashboard**:
1. Go to your service settings
2. Click "Environment"
3. Add variables one by one

**Docker run**:
```bash
docker run -e WHISPERX_MODEL=base -e HF_TOKEN=xxx whisperx:latest
```

## 📊 Performance Benchmarks

### CPU (Render Starter Plan - 0.5 CPU, 512MB RAM)
- **tiny model**: ~5-10x realtime
- **base model**: ~2-5x realtime ⭐ Recommended
- **small model**: ~1-2x realtime

### GPU (NVIDIA T4 - 16GB VRAM)
- **tiny model**: ~100x realtime
- **base model**: ~70x realtime
- **large-v2 model**: ~70x realtime ⭐ Recommended

*Realtime = processing 1 hour of audio takes 1 hour*

## 💰 Cost Estimates (Render)

| Plan | vCPU | RAM | Price/mo | Recommended Model |
|------|------|-----|----------|-------------------|
| Free | 0.1 | 512MB | $0 | tiny (limited use) |
| Starter | 0.5 | 512MB | $7 | base |
| Standard | 1 | 2GB | $25 | small |
| Pro | 2 | 4GB | $85 | medium |
| Pro Plus | 4 | 8GB | $175 | large-v2 (CPU) |

*Add $10-20/month for persistent disk storage*

## 🔍 Testing

### Test API Locally
```bash
# 1. Start the server
./build-and-run.sh cpu build-run

# 2. In another terminal, test the API
./test-api.sh sample.mp3

# Or use cURL
curl -X POST http://localhost:8000/transcribe \
  -F "file=@audio.mp3" \
  -F "language=en"
```

### Test on Render
```bash
# After deploying to Render
API_URL=https://your-app.onrender.com ./test-api.sh audio.mp3
```

## 🛡️ Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **HF Token**: Set as secret environment variable
3. **API Keys**: Add authentication for production
4. **Rate Limiting**: Implement to prevent abuse
5. **File Upload Limits**: Configure max file size
6. **CORS**: Configure allowed origins

### Example: Add API Key Authentication

Edit [api.py](api.py):

```python
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException

API_KEY = os.getenv("API_KEY", "your-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/transcribe")
async def transcribe_audio(
    api_key: str = Security(verify_api_key),
    file: UploadFile = File(...),
    ...
):
    # Your code here
```

## 📈 Scaling Recommendations

### Small Scale (< 1000 requests/day)
- **Platform**: Render Starter ($7/mo)
- **Model**: base
- **Config**: 1 instance, auto-sleep enabled

### Medium Scale (< 10,000 requests/day)
- **Platform**: Render Standard ($25/mo)
- **Model**: small
- **Config**: 2 instances, min 1 instance
- **Add**: Redis cache for results

### Large Scale (> 10,000 requests/day)
- **Platform**: Render Pro+ or AWS ECS
- **Model**: medium/large-v2 with GPU
- **Config**: Auto-scaling 3-10 instances
- **Add**: Queue system (Celery + Redis), CDN, load balancer

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs <container_id>

# Check if port is in use
lsof -i :8000

# Try different port
docker run -p 8080:8000 whisperx:latest
```

### Out of memory errors
```bash
# Use smaller model
docker run -e WHISPERX_MODEL=tiny whisperx:latest

# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory
```

### Speaker diarization not working
```bash
# Verify HF token is set
docker run -e HF_TOKEN=hf_xxx whisperx:latest

# Check you've accepted the model terms:
# https://huggingface.co/pyannote/speaker-diarization-community-1
```

### Slow processing on Render
- Use smaller model (tiny or base)
- Upgrade to higher plan
- Split long audio files
- Enable persistent disk for model caching

## 📖 Additional Resources

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Detailed Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **WhisperX Docs**: https://github.com/m-bain/whisperX
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Add webhook support for async processing
- [ ] Implement queue system (Celery/Redis)
- [ ] Add batch processing endpoint
- [ ] Improve error handling
- [ ] Add request validation
- [ ] Implement caching layer
- [ ] Add monitoring/metrics
- [ ] Create Kubernetes manifests

## 📝 License

This Docker setup is provided as-is. WhisperX is licensed under BSD-2-Clause.

## 🎉 Ready to Deploy?

1. **Local Testing**: `./build-and-run.sh cpu build-run`
2. **Push to GitHub**: `git push origin main`
3. **Deploy on Render**: Connect repo in dashboard
4. **Test Live API**: `./test-api.sh` with your Render URL

---

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) or [QUICKSTART.md](QUICKSTART.md)

**Issues?** See the Troubleshooting section above or open a GitHub issue
