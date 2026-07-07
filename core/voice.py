import os
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise ValueError("ELEVENLABS_API_KEY is not set.")

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
if not VOICE_ID:
    raise ValueError("ELEVENLABS_VOICE_ID is not set.")


def synthesise_speech(text, output_path, intensity=5.0):
    """
    Convert text to speech using ElevenLabs.
    Voice settings shift based on intensity.
    """

    url = f"{ELEVENLABS_API_URL}/{VOICE_ID}"

    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # High intensity = less stable (more excited), high similarity
    # Low intensity = more stable (calm), normal similarity
    stability = max(0.2, 0.8 - (intensity / 10) * 0.5)
    similarity = min(0.95, 0.6 + (intensity / 10) * 0.3)

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": round(stability, 2),
            "similarity_boost": round(similarity, 2)
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"ElevenLabs error: {response.status_code} {response.text}"
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"[Pulse] Audio saved: {output_path}")
    return output_path


def synthesise_all_commentary(commentary_results, output_dir="output/audio"):
    """
    Convert all commentary lines to audio files.
    Passes intensity to voice synthesiser for dynamic voice settings.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_results = []

    for item in commentary_results:
        timestamp = item["timestamp"]
        text = item["commentary"].strip('"').strip("'")
        intensity = item.get("intensity", 5.0)

        filename = f"commentary_t{timestamp}s.mp3"
        output_path = os.path.join(output_dir, filename)

        print(f"[Pulse] Synthesising t={timestamp}s intensity={intensity}...")
        synthesise_speech(text, output_path, intensity=intensity)

        audio_results.append({
            "timestamp": timestamp,
            "intensity": intensity,
            "commentary": text,
            "audio_path": output_path
        })

    return audio_results
