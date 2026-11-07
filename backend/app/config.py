import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "ai_lawyer.db"))

# Hot-Swappable Model Configuration (Allows instant model swapping during live interviews)
# Supported providers: 'sarvam' (default), 'openai', 'gemini', 'anthropic', 'custom_openai'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "sarvam")
LLM_MODEL = os.getenv("LLM_MODEL", "sarvam-105b-conversations")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

# Sarvam Credit Protection Toggle: If True, bypasses external network calls and uses deterministic mocks
USE_MOCK_SARVAM = os.getenv("USE_MOCK_SARVAM", "False").lower() in ("true", "1", "yes")
