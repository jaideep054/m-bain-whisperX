"""
Test script for WhisperX API with speaker diarization
"""
import requests
import json
import sys

# API endpoint
API_URL = "http://localhost:8000/transcribe"

def test_transcription(audio_file_path, language="hi", diarize=True, min_speakers=2, max_speakers=5):
    """
    Test the WhisperX API with speaker diarization

    Args:
        audio_file_path: Path to audio file
        language: Language code (e.g., 'hi' for Hindi)
        diarize: Enable speaker diarization
        min_speakers: Minimum number of speakers
        max_speakers: Maximum number of speakers
    """
    print(f"Testing API with audio file: {audio_file_path}")
    print(f"Parameters: language={language}, diarize={diarize}, min_speakers={min_speakers}, max_speakers={max_speakers}")
    print("-" * 80)

    # Prepare the request
    files = {'file': open(audio_file_path, 'rb')}
    data = {
        'language': language,
        'diarize': str(diarize).lower(),
        'min_speakers': min_speakers,
        'max_speakers': max_speakers
    }

    try:
        print("Sending request to API...")
        response = requests.post(API_URL, files=files, data=data, timeout=600)

        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Transcription completed.\n")

            # Save result to file
            output_file = "test_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Full result saved to: {output_file}")

            # Print summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Language: {result.get('language')}")
            print(f"Detected Language: {result.get('detected_language')}")
            print(f"Total Segments: {len(result.get('segments', []))}")

            # Print first few segments with speaker info
            segments = result.get('segments', [])
            if segments:
                print("\nFirst 3 segments:")
                for i, seg in enumerate(segments[:3]):
                    speaker = seg.get('speaker', 'N/A')
                    text = seg.get('text', '')
                    print(f"\n  [{i+1}] Speaker: {speaker}")
                    print(f"      Text: {text[:100]}...")

            # Count unique speakers
            if diarize:
                speakers = set()
                for seg in segments:
                    if 'speaker' in seg:
                        speakers.add(seg['speaker'])
                print(f"\n👥 Total unique speakers detected: {len(speakers)}")
                print(f"   Speakers: {', '.join(sorted(speakers))}")

        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out. The audio file might be too long or the model is processing slowly.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_diarization.py <audio_file_path> [language] [min_speakers] [max_speakers]")
        print("\nExample:")
        print("  python test_diarization.py audio.mp3")
        print("  python test_diarization.py audio.mp3 hi 2 3")
        sys.exit(1)

    audio_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "hi"
    min_speakers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    max_speakers = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    test_transcription(audio_file, language, diarize=True, min_speakers=min_speakers, max_speakers=max_speakers)
