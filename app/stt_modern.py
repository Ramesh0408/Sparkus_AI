"""
STT using Groq's Whisper API.
Replaced local openai/whisper-base (1.5GB model) with Groq's hosted whisper-large-v3.
Faster, lighter, and works perfectly on cloud deployments.
"""
from groq import Client
import os
from dotenv import load_dotenv
from app.utils import OUTPUTS_DIR, generate_id

load_dotenv()

_client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Client(api_key=api_key)
    return _client


def transcribe_audio_file(audio_path: str) -> str:
    """Transcribe audio file using Groq Whisper. Returns transcribed text."""
    client = _get_client()

    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f,
            response_format="text"
        )

    text = transcription if isinstance(transcription, str) else transcription.text

    # Save transcript
    out_dir = OUTPUTS_DIR / "stt"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{generate_id()}.txt"
    out_file.write_text(text, encoding="utf-8")

    return text


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(transcribe_audio_file(sys.argv[1]))