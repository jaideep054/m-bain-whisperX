# 🚀 WhisperX Docker - Quick Start Guide

Get WhisperX running in Docker in 5 minutes!

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- For GPU: NVIDIA GPU with Docker GPU support

## 🏃 Quick Start (3 Steps)

### Step 1: Build the Docker Image

```bash
# CPU version (for Render or local CPU)
docker build -t whisperx:latest .

# OR GPU version (requires NVIDIA GPU)
docker build -f Dockerfile.gpu -t whisperx:gpu .
```

### Step 2: Run the API Server

```bash
# CPU version
docker run -p 8000:8000 whisperx:latest

# OR GPU version
docker run --gpus all -p 8000:8000 whisperx:gpu
```

### Step 3: Test the API

Open your browser and go to:
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/docs (try it out!)

## 📤 Transcribe Your First Audio

### Using cURL

```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@your-audio.mp3" \
  -F "language=en"
```

### Using the Test Script

```bash
./test-api.sh your-audio.mp3
```

### Using Python

```python
import requests

with open("audio.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/transcribe",
        files={"file": f},
        data={"language": "en"}
    )
    print(response.json())
```

## 🐳 Using Docker Compose (Easiest)

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env and add your HF_TOKEN if needed

# 2. Create directories
mkdir -p input output

# 3. Add audio file
cp your-audio.mp3 input/sample.mp3

# 4. Run
docker-compose up whisperx-cpu
```

## 🌐 Deploy to Render

### Method 1: Automatic (Using render.yaml)

1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Add WhisperX Docker setup"
   git push origin main
   ```

2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** → **Blueprint**
4. Connect your repository
5. Render will auto-deploy using `render.yaml`

### Method 2: Manual

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your repository
4. Configure:
   - **Name**: whisperx-api
   - **Environment**: Docker
   - **Dockerfile Path**: ./Dockerfile
   - **Plan**: Starter (or higher)

5. Add Environment Variables:
   - `WHISPERX_MODEL`: `base` (or `tiny`, `small`, `medium`, `large-v2`)
   - `HF_TOKEN`: Your Hugging Face token (optional, for diarization)

6. Add Disk Storage:
   - **Name**: whisperx-models
   - **Mount Path**: /app/models
   - **Size**: 10 GB

7. Click **Create Web Service**

## 🔑 Enable Speaker Diarization

To use speaker diarization (identify who is speaking):

1. Get a Hugging Face token:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token (read access)

2. Accept the model agreement:
   - Visit https://huggingface.co/pyannote/speaker-diarization-community-1
   - Accept the terms

3. Set the token:
   - **Local**: Add to `.env` file: `HF_TOKEN=your_token`
   - **Render**: Add in environment variables

4. Use diarization in API:
   ```bash
   curl -X POST http://localhost:8000/transcribe \
     -F "file=@audio.mp3" \
     -F "diarize=true" \
     -F "min_speakers=2" \
     -F "max_speakers=3"
   ```

## 🎛️ Model Selection

Choose the right model for your needs:

| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|--------|----------|
| tiny | ⚡⚡⚡⚡ | ⭐⭐ | 1GB | Testing, demos |
| base | ⚡⚡⚡ | ⭐⭐⭐ | 2GB | **Recommended for Render** |
| small | ⚡⚡ | ⭐⭐⭐⭐ | 4GB | Good balance |
| medium | ⚡ | ⭐⭐⭐⭐⭐ | 8GB | High accuracy |
| large-v2 | ⚡ | ⭐⭐⭐⭐⭐ | 16GB | Best accuracy (GPU only) |

Set in Render: `WHISPERX_MODEL=base`

## 🛠️ Helper Scripts

### Build and Run Script

```bash
# Build and run CPU version
./build-and-run.sh cpu build-run

# Build only
./build-and-run.sh cpu build

# Run existing image
./build-and-run.sh cpu run

# GPU version
./build-and-run.sh gpu build-run
```

### Test API Script

```bash
# Test with default sample.mp3
./test-api.sh

# Test with specific file
./test-api.sh path/to/audio.mp3

# Test deployed Render API
API_URL=https://your-app.onrender.com ./test-api.sh audio.mp3
```

## 📊 API Response Example

```json
{
  "status": "success",
  "language": "en",
  "segments": [
    {
      "start": 0.5,
      "end": 2.8,
      "text": "Hello, welcome to WhisperX.",
      "speaker": "SPEAKER_00"
    },
    {
      "start": 3.0,
      "end": 5.5,
      "text": "This is an example transcription.",
      "speaker": "SPEAKER_01"
    }
  ]
}
```

## ⚠️ Common Issues

### Issue: Port already in use

```bash
# Use different port
docker run -p 8080:8000 whisperx:latest

# Then access at: http://localhost:8080
```

### Issue: Out of memory

```bash
# Use smaller model
docker run -e WHISPERX_MODEL=tiny -p 8000:8000 whisperx:latest

# Or reduce batch size in API call
curl -X POST http://localhost:8000/transcribe \
  -F "file=@audio.mp3" \
  -F "batch_size=4"
```

### Issue: Slow processing

- Use GPU version for 70x faster processing
- Use smaller model (tiny or base)
- Split long audio into smaller chunks
- Upgrade Render plan for more CPU/RAM

## 📚 Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide
- Check out [WhisperX GitHub](https://github.com/m-bain/whisperX) for more features
- Explore the interactive API docs at `/docs` endpoint

## 🎯 Example Use Cases

1. **Meeting Transcription**: Transcribe with speaker diarization
2. **Podcast Transcription**: Generate accurate subtitles
3. **Voice Note Processing**: Convert audio notes to text
4. **Video Subtitling**: Extract and time-stamp spoken content
5. **Interview Analysis**: Identify speakers and transcribe conversations

## 💡 Tips

- Start with `base` model for testing
- Enable diarization for multi-speaker audio
- Use GPU for production workloads
- Cache models to speed up startup
- Monitor memory usage on Render

---

**Need Help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) or open an issue on GitHub.
