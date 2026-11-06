import io
import re
import wave
import base64
from typing import Tuple, Optional
from ..config import USE_MOCK_SARVAM
from .sarvam_client import get_sarvam_client

def get_dummy_wav_base64() -> str:
    """Generates a small valid WAV sound clip in base64 for testing/mocking."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b'\x00\x00' * 8000) # 0.5s tone/silence
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def clean_text_for_tts(text: str) -> str:
    """Removes markdown symbols and cleans text for clear audio synthesis."""
    cleaned = re.sub(r"\*\*|\*|__|_|#+", "", text)
    cleaned = re.sub(r"^\s*[-•]\s*", "", cleaned, flags=re.MULTILINE)
    lines = cleaned.strip().split("\n\n")
    if len(lines) > 2:
        return " ".join(lines[:2]).strip()
    return cleaned.strip()

def transcribe_audio_file(file_bytes: bytes, filename: str = "recording.wav") -> Tuple[str, str]:
    """
    Sends audio bytes to Sarvam Saaras STT API.
    Returns (transcript_text, detected_language_code).
    """
    if USE_MOCK_SARVAM:
        return "Mera landlord deposit wapas nahi de raha hai, bol raha hai paint ka katega.", "hi-IN"

    client = get_sarvam_client()
    if not client:
        return "Audio input received (Sarvam API key not set)", "unknown"

    try:
        mime = "audio/wav"
        if filename.endswith(".mp3"):
            mime = "audio/mp3"
        elif filename.endswith(".m4a"):
            mime = "audio/m4a"
        elif filename.endswith(".webm"):
            mime = "audio/webm"

        response = client.speech_to_text.transcribe(
            file=(filename, file_bytes, mime),
            model="saaras:v3",
            language_code="unknown"
        )
        transcript = getattr(response, "transcript", "")
        language_code = getattr(response, "language_code", "hi-IN")
        return transcript, language_code
    except Exception as e:
        print(f"Sarvam STT Error: {e}")
        return "", "unknown"

def generate_voice_response(text: str, language_code: str = "hi-IN") -> Optional[str]:
    """
    Sends text to Sarvam Bulbul TTS API.
    Returns base64-encoded WAV audio string.
    """
    if USE_MOCK_SARVAM:
        return get_dummy_wav_base64()

    client = get_sarvam_client()
    if not client:
        return None

    try:
        tts_text = clean_text_for_tts(text)
        if not tts_text:
            return None

        valid_langs = ["hi-IN", "bn-IN", "kn-IN", "ml-IN", "mr-IN", "od-IN", "pa-IN", "ta-IN", "te-IN", "en-IN", "gu-IN"]
        lang = language_code if language_code in valid_langs else "hi-IN"

        response = client.text_to_speech.convert(
            text=tts_text,
            language_code=lang,
            model="bulbul:v3"
        )
        if hasattr(response, "audios") and len(response.audios) > 0:
            return response.audios[0]
        return None
    except Exception as e:
        print(f"Sarvam TTS Error: {e}")
        return None
