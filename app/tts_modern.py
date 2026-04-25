from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR    = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs" / "tts"

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set in .env")
        _client = ElevenLabs(api_key=api_key)
    return _client

def text_to_speech(text: str) -> str:
    try:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        client = _get_client()

        audio = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            text=text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.3,
                use_speaker_boost=True
            )
        )

        filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".mp3"
        out_path = OUTPUTS_DIR / filename

        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return str(out_path)

    except Exception as e:
        print("TTS ERROR:", e)
        return None