import requests
from app.config import settings

def generate(prompt: str, system: str = "You are a careful business analyst.") -> str | None:
    try:
        r = requests.post(f"{settings.ollama_base_url}/api/chat",
            json={"model": settings.ollama_chat_model,
                  "messages": [{"role":"system","content":system},{"role":"user","content":prompt}],
                  "stream":False}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except (requests.RequestException, KeyError, ValueError):
        return None

def ollama_available():
    try:
        return requests.get(f"{settings.ollama_base_url}/api/tags", timeout=2).ok
    except requests.RequestException:
        return False
