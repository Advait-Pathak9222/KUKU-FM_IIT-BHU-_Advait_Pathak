import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

def _get_secret(key: str, default: str = "") -> str:
    val = os.getenv(key, "")
    if val:
        return val
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


SARVAM_API_KEY = _get_secret("SARVAM_API_KEY", "")
DB_PATH = _get_secret("DB_PATH", str(BASE_DIR / "ai_lawyer.db"))

# Hot-Swappable Model Configuration (Allows instant model swapping during live interviews)
# Supported providers: 'sarvam' (default), 'openai', 'gemini', 'anthropic', 'custom_openai'
LLM_PROVIDER = _get_secret("LLM_PROVIDER", "sarvam")
LLM_MODEL = _get_secret("LLM_MODEL", "sarvam-105b-conversations")
LLM_API_KEY = _get_secret("LLM_API_KEY", "")
LLM_BASE_URL = _get_secret("LLM_BASE_URL", "https://api.openai.com/v1")

# Sarvam Credit Protection Toggle: If True, bypasses external network calls and uses deterministic mocks
USE_MOCK_SARVAM = _get_secret("USE_MOCK_SARVAM", "False").lower() in ("true", "1", "yes")

