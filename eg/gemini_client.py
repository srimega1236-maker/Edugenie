import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE = Path(__file__).parent
ENV_FILE = BASE / ".env"
load_dotenv(ENV_FILE, override=True, encoding="utf-8-sig")

# .env work aagala-na, key-a inga quotes-kulla podunga (last option)
BACKUP_KEY = ""

MODELS = [m for m in [
    os.getenv("GEMINI_MODEL", "").strip(),
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
] if m]


def generate(prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'") or BACKUP_KEY
    if not key:
        found = "irukku" if ENV_FILE.exists() else "illa"
        raise RuntimeError(
            f"API key kedaikkala. Ithu dhaan .env path: {ENV_FILE} (file {found}). "
            "Ullae GEMINI_API_KEY=unga_key nu irukkanum."
        )
    last = "Unknown error"
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        r = requests.post(
            url,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=90,
        )
        data = r.json()
        if r.ok:
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError):
                last = "Gemini returned an empty answer"
        else:
            last = data.get("error", {}).get("message", f"Request failed ({r.status_code})")
            if r.status_code in (400, 401, 403) and "model" not in last.lower():
                break
    raise RuntimeError(last)