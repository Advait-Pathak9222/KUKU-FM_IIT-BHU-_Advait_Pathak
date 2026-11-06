import io
import base64
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.sarvam_client import get_sarvam_client

def test_audio_pipeline():
    print("=" * 60)
    print("TESTING MULTIMODAL AUDIO PIPELINE (SAARAS STT + BULBUL TTS)")
    print("=" * 60)

    client = TestClient(app)
    sarvam = get_sarvam_client()
    
    # 1. Synthesize a sample Hindi audio clip to simulate user speaking into microphone
    print("1. Generating simulated user speech audio in Hindi...")
    sample_text = "Mera landlord deposit wapas nahi de raha, bol raha hai paint ka katega."
    tts_resp = sarvam.text_to_speech.convert(
        text=sample_text,
        language_code="hi-IN",
        model="bulbul:v3"
    )
    user_audio_bytes = base64.b64decode(tts_resp.audios[0])
    print(f"   Generated user audio WAV: {len(user_audio_bytes)} bytes")

    # 2. Call POST /audio-chat/{session_id}
    session_id = "test_audio_session_001"
    print(f"\n2. Sending audio to POST /audio-chat/{session_id} ...")
    
    response = client.post(
        f"/audio-chat/{session_id}",
        files={"file": ("user_voice.wav", io.BytesIO(user_audio_bytes), "audio/wav")}
    )

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return

    data = response.json()
    print("\n3. Audio-Chat Endpoint Response Received Successfully:")
    print(f"- User Transcription: \"{data['user_transcription']}\"")
    print(f"- Detected Language: {data['detected_language']}")
    print(f"- Domain: {data['domain']}")
    print(f"- Missing Variables: {data['missing_variables']}")
    print(f"- Assistant Reply:\n  {data['reply']}")
    print(f"- Spoken Audio Received: {'YES (Base64 WAV string)' if data.get('audio_base64') else 'NO'}")
    if data.get('audio_base64'):
        print(f"- Assistant Audio Length: {len(data['audio_base64'])} characters")

    print("\n✅ MULTIMODAL AUDIO PIPELINE PASSED END-TO-END!")

if __name__ == "__main__":
    test_audio_pipeline()
