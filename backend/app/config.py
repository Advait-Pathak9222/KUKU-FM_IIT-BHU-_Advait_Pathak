import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "ai_lawyer.db"))

# Sarvam Credit Protection Toggle: If True, bypasses external network calls and uses deterministic mocks
USE_MOCK_SARVAM = os.getenv("USE_MOCK_SARVAM", "False").lower() in ("true", "1", "yes")
