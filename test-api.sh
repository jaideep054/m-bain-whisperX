#!/bin/bash
# Test script for WhisperX API

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
AUDIO_FILE="${1:-sample.mp3}"

echo "🎙️  WhisperX API Test Script"
echo "================================"
echo "API URL: $API_URL"
echo "Audio File: $AUDIO_FILE"
echo ""

# Check if audio file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Error: Audio file '$AUDIO_FILE' not found!"
    echo "Usage: ./test-api.sh <audio_file.mp3>"
    exit 1
fi

# Test health endpoint
echo "1️⃣  Testing health endpoint..."
curl -s "$API_URL/health" | jq .
echo ""

# Test root endpoint
echo "2️⃣  Testing root endpoint..."
curl -s "$API_URL/" | jq .
echo ""

# Test transcription endpoint
echo "3️⃣  Testing transcription endpoint..."
echo "   (This may take a while depending on the audio file size)"
echo ""

response=$(curl -s -X POST "$API_URL/transcribe" \
  -F "file=@$AUDIO_FILE" \
  -F "language=en" \
  -F "batch_size=8")

echo "$response" | jq .

# Save response to file
echo "$response" > transcription_result.json
echo ""
echo "✅ Transcription saved to: transcription_result.json"
echo ""

# Extract and display just the text
echo "📝 Transcribed Text:"
echo "-------------------"
echo "$response" | jq -r '.segments[].text' 2>/dev/null || echo "No transcription found"
