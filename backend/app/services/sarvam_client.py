import os
import requests
from typing import Optional
from sarvamai import SarvamAI
from ..config import SARVAM_API_KEY, LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL

_client: Optional[SarvamAI] = None
_client_key: Optional[str] = None

def get_sarvam_client() -> Optional[SarvamAI]:
    """
    Returns an initialized SarvamAI client. Dynamically checks os.environ
    so Streamlit Cloud secrets loaded at runtime are always picked up.
    """
    global _client, _client_key
    active_key = os.getenv("SARVAM_API_KEY", SARVAM_API_KEY)
    if active_key and (_client is None or _client_key != active_key):
        _client = SarvamAI(api_subscription_key=active_key)
        _client_key = active_key
    return _client


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> Optional[str]:
    """
    Universal, hot-swappable LLM router.
    Defaults to Sarvam-105B-Conversations, but allows instant zero-code model swapping
    (OpenAI, Gemini, Anthropic, or any OpenAI-compatible endpoint) during live interviews
    via environment variables or the UI sidebar.
    """
    use_mock = os.getenv("USE_MOCK_SARVAM", "False").lower() in ("true", "1", "yes")
    if use_mock:
        return None

    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower().strip()
    model = os.getenv("LLM_MODEL", LLM_MODEL).strip()
    api_key = os.getenv("LLM_API_KEY", LLM_API_KEY).strip()
    base_url = os.getenv("LLM_BASE_URL", LLM_BASE_URL).strip()

    # 1. Default Sarvam AI Provider
    if provider == "sarvam":
        client = get_sarvam_client()
        if not client:
            return None
        sarvam_model = model if model else "sarvam-105b-conversations"
        response = client.chat.completions(
            model=sarvam_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    # 2. Anthropic Claude Provider
    if provider == "anthropic":
        key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("Missing API key for Anthropic provider.")
        claude_model = model if model and "sarvam" not in model else "claude-3-5-sonnet-latest"
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": claude_model,
                "max_tokens": 1024,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}]
            },
            timeout=25
        )
        res.raise_for_status()
        return res.json()["content"][0]["text"].strip()

    # 3. OpenAI / Gemini / Custom OpenAI-Compatible Provider
    if provider in ("openai", "gemini", "custom_openai"):
        if provider == "gemini":
            key = api_key or os.getenv("GEMINI_API_KEY", "")
            endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            active_model = model if model and "sarvam" not in model else "gemini-2.5-flash"
        else:
            key = api_key or os.getenv("OPENAI_API_KEY", "")
            clean_base = (base_url or "https://api.openai.com/v1").rstrip("/")
            endpoint = f"{clean_base}/chat/completions"
            active_model = model if model and "sarvam" not in model else "gpt-4o-mini"

        if not key:
            raise ValueError(f"Missing API key for {provider} provider.")

        res = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": active_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
            },
            timeout=25
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()

    return None
