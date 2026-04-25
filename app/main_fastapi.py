from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

from app.stt_modern import transcribe_audio_file
from app.image_ocr import run_ocr
from app.image_caption import caption_image
from app.tts_modern import text_to_speech
from app.llm_module import generate_response
from app.utils import UPLOADS_DIR, save_bytes

import re

def clean_for_tts(text: str) -> str:
    text = re.sub(r'[#*_`>-]', '', text)
    text = re.sub(r'\n+', '. ', text)
    return text.strip()

# ─────────────────────────────────────────
app = FastAPI(title="Multimodal AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class TextRequest(BaseModel):
    text: str
    history: Optional[List[Message]] = []


# ─────────────────────────────────────────
# PURE UTILITY ENDPOINTS
# ─────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    path = save_bytes(UPLOADS_DIR / "audio", file.filename, await file.read())
    text = transcribe_audio_file(str(path))
    return {"text": text}


@app.post("/tts")
async def tts(text: str = Form(...)):
    audio_path = text_to_speech(text)
    return {"audio": audio_path}


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    path = save_bytes(UPLOADS_DIR / "images", file.filename, await file.read())
    text = run_ocr(str(path))
    return {"text": text}


@app.post("/caption")
async def caption(file: UploadFile = File(...)):
    path = save_bytes(UPLOADS_DIR / "images", file.filename, await file.read())
    result = caption_image(str(path))
    return {"caption": result}


# ─────────────────────────────────────────
# ASSISTANT ENDPOINTS
# ─────────────────────────────────────────
@app.post("/assistant/text")
async def assistant_text(data: TextRequest):
    try:
        history = [{"role": m.role, "content": m.content} for m in data.history]

        print("INPUT:", data.text)
        print("HISTORY:", history)

        reply = generate_response(data.text, history)
        print("LLM REPLY:", reply)

        clean_text = clean_for_tts(reply)

        audio = None
        try:
            audio = text_to_speech(clean_text)
        except Exception as e:
            print("TTS FAILED:", e)

        print("AUDIO PATH:", audio)

        return {"text": reply, "audio": audio}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"text": f"ERROR: {str(e)}", "audio": None}


@app.post("/assistant/audio")
async def assistant_audio(file: UploadFile = File(...)):
    try:
        path       = save_bytes(UPLOADS_DIR / "audio", file.filename, await file.read())
        transcript = transcribe_audio_file(str(path))
        reply      = generate_response(transcript, [])
        clean_text = clean_for_tts(reply)

        audio = None
        try:
            audio = text_to_speech(clean_text)
        except Exception as e:
            print("TTS FAILED:", e)
        return {"text": reply, "audio": audio, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assistant/image")
async def assistant_image(file: UploadFile = File(...)):
    try:
        path    = save_bytes(UPLOADS_DIR / "images", file.filename, await file.read())
        ocr_txt = run_ocr(str(path))
        cap_txt = caption_image(str(path))

        combined = (
            f"The user sent an image.\n\n"
            f"Image caption: {cap_txt}\n\n"
            f"Text found in image (OCR): {ocr_txt if ocr_txt.strip() else 'None'}\n\n"
            f"Please describe what you see and answer any questions about it."
        )

        reply = generate_response(combined, [])
        audio = text_to_speech(reply)
        return {"text": reply, "audio": audio, "caption": cap_txt, "ocr": ocr_txt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))