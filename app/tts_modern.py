"""
TTS using gTTS — works on all platforms including Linux (Render/Streamlit Cloud).
pyttsx3 removed because it requires Windows-only pywin32.
"""
from gtts import gTTS
from pathlib import Path
from datetime import datetime


BASE_DIR    = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs" / "tts"


def text_to_speech(text: str, lang: str = "en") -> str:
    """Convert text to speech and save as mp3. Returns file path or empty string."""
    try:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".mp3"
        out_path = OUTPUTS_DIR / filename
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(str(out_path))
        return str(out_path)
    except Exception as e:
        # If no internet or any error, return empty — app still works without audio
        print(f"TTS warning: {e}")
        return ""


if __name__ == "__main__":
    path = text_to_speech("Hello! I am Sparkus AI, your multimodal assistant.")
    print(f"Saved to: {path}")
