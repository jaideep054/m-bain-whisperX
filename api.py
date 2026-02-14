"""
Simple FastAPI wrapper for WhisperX
Use this for deploying WhisperX as a web service on Render
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import whisperx
import os
import tempfile
import shutil
from typing import Optional
import torch

app = FastAPI(
    title="WhisperX API",
    description="Speech recognition API powered by WhisperX",
    version="1.0.0"
)

# Configuration from environment variables
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"
MODEL_NAME = os.getenv("WHISPERX_MODEL", "base")
HF_TOKEN = os.getenv("HF_TOKEN", None)

# Load model on startup
model = None

@app.on_event("startup")
async def startup_event():
    """Load WhisperX model on startup"""
    global model
    print(f"Loading WhisperX model '{MODEL_NAME}' on {DEVICE}...")
    model = whisperx.load_model(MODEL_NAME, DEVICE, compute_type=COMPUTE_TYPE)
    print("Model loaded successfully!")

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "device": DEVICE
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "WhisperX API",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "device": DEVICE,
        "endpoints": {
            "transcribe": "/transcribe",
            "health": "/health"
        }
    }

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    batch_size: int = Form(8),
    diarize: bool = Form(False),
    min_speakers: Optional[int] = Form(None),
    max_speakers: Optional[int] = Form(None)
):
    """
    Transcribe audio file with WhisperX

    Parameters:
    - file: Audio file (mp3, wav, m4a, etc.)
    - language: Language code (optional, auto-detect if not provided)
    - batch_size: Batch size for inference (default: 8)
    - diarize: Enable speaker diarization (requires HF_TOKEN)
    - min_speakers: Minimum number of speakers (optional)
    - max_speakers: Maximum number of speakers (optional)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    try:
        # Save uploaded file
        temp_audio_path = os.path.join(temp_dir, file.filename)
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load and transcribe audio
        audio = whisperx.load_audio(temp_audio_path)
        result = model.transcribe(audio, batch_size=batch_size, language=language)

        # Align whisper output
        if result.get("language"):
            model_a, metadata = whisperx.load_align_model(
                language_code=result["language"],
                device=DEVICE
            )
            result = whisperx.align(
                result["segments"],
                model_a,
                metadata,
                audio,
                DEVICE,
                return_char_alignments=False
            )

        # Speaker diarization (if requested)
        if diarize:
            if not HF_TOKEN:
                raise HTTPException(
                    status_code=400,
                    detail="HF_TOKEN required for speaker diarization"
                )

            from whisperx.diarize import DiarizationPipeline
            diarize_model = DiarizationPipeline(token=HF_TOKEN, device=DEVICE)
            diarize_kwargs = {}
            if min_speakers:
                diarize_kwargs["min_speakers"] = min_speakers
            if max_speakers:
                diarize_kwargs["max_speakers"] = max_speakers

            diarize_segments = diarize_model(audio, **diarize_kwargs)
            result = whisperx.assign_word_speakers(diarize_segments, result)

        return JSONResponse(content={
            "status": "success",
            "language": result.get("language"),
            "segments": result.get("segments", []),
            "word_segments": result.get("word_segments", [])
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
