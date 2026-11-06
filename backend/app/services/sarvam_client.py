from typing import Optional
from sarvamai import SarvamAI
from ..config import SARVAM_API_KEY

_client: Optional[SarvamAI] = None

def get_sarvam_client() -> Optional[SarvamAI]:
    global _client
    if _client is None and SARVAM_API_KEY:
        _client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    return _client
