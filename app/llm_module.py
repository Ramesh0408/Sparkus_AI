from groq import Client
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

_client = None
MODEL   = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful, friendly, and concise multimodal AI assistant.
You can understand text, images, and voice messages.
When analyzing images, describe them clearly and answer questions about them.
Keep responses clear and conversational. Use markdown formatting when helpful."""


def _get_client() -> Client:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in your .env file")
        _client = Client(api_key=api_key)
    return _client


def generate_response(text: str, history: List[Dict] = []) -> str:
    client = _get_client()

    # Build messages: system + history + new user message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add previous conversation (limit to last 10 turns to save tokens)
    for msg in history[-10:]:
        clean_text = msg["content"].strip()

# remove UI artifacts
        if clean_text in ["🎤 Sending…", "🖼️ Analyzing…", "Thinking…"]:
            continue

        if clean_text.startswith("<img"):
            clean_text = "[Image]"

        messages.append({"role": msg["role"], "content": clean_text})
            # Strip image HTML tags from history to avoid token bloat
        content = msg["content"]
        if content.startswith("<img"):
            content = "[Image]"
        messages.append({"role": msg["role"], "content": content})

    # Add current user message
    messages.append({"role": "user", "content": text})

    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    return completion.choices[0].message.content


if __name__ == "__main__":
    print(generate_response("Hello! What can you do?"))