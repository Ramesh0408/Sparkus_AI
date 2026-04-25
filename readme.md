# ✦ Sparkus AI — Multimodal Intelligence

A production-ready ChatGPT-style chatbot with text, voice, and image support.

**Stack:** Streamlit · FastAPI · Groq (LLaMA 3.3 + Whisper) · BLIP · pyttsx3 · Tesseract

---

## 📁 Project Structure

```
chatbot/
├── app/
│   ├── main_fastapi.py      # FastAPI backend (all endpoints)
│   ├── llm_module.py        # LLaMA 3.3 via Groq
│   ├── stt_modern.py        # Whisper via Groq API
│   ├── tts_modern.py        # pyttsx3 TTS
│   ├── image_caption.py     # BLIP image captioning
│   ├── image_ocr.py         # Tesseract OCR
│   └── utils.py             # Shared helpers
├── streamlit_app/
│   └── app.py               # Sparkus AI frontend
├── packages.txt             # System packages for Streamlit Cloud
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── README.md
```

---

## 🚀 Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/sparkus-ai.git
cd sparkus-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

Run two terminals:
```bash
# Terminal 1 — Backend
uvicorn app.main_fastapi:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run streamlit_app/app.py
```

---

## ☁️ Deploy

- **Backend** → Railway.app
- **Frontend** → Streamlit Cloud

See README for full deploy steps.