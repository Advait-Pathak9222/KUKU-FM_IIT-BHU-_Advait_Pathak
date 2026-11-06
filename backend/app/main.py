from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, Tuple

from .config import SARVAM_API_KEY
from .database import (
    init_db,
    save_chat_message,
    get_chat_history,
    get_case_state,
    upsert_case_state
)
from .models import ChatRequest, ChatResponse, AudioChatResponse
from .services.triage import classify_user_intent
from .services.extractor import (
    extract_facts,
    check_missing_variables,
    generate_clarification_response,
    assemble_legal_notice
)
from .services.voice_service import (
    transcribe_audio_file,
    generate_voice_response
)
from .services.pdf_generator import generate_legal_notice_pdf
from .kb import get_kb

app = FastAPI(
    title="NyayaMitra - Everyday Indic AI Lawyer API",
    version="1.0.0",
    description="Voice and text-enabled conversational legal triage, fact extraction, and legal notice drafting for everyday Indian civil grievances."
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "sarvam_api_connected": bool(SARVAM_API_KEY),
        "supported_domains": ["rental_deposit", "unpaid_salary"]
    }

@app.get("/state/{session_id}")
def get_session_state(session_id: str):
    state = get_case_state(session_id)
    history = get_chat_history(session_id)
    return {
        "session_id": session_id,
        "case_state": state,
        "chat_history": history
    }

@app.get("/notice/{session_id}/pdf")
def get_notice_pdf(session_id: str):
    state = get_case_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found.")
    if not state.get("is_complete"):
        raise HTTPException(status_code=400, detail="Case is not yet complete. Missing variables need resolution.")
    
    domain = state.get("domain", "rental_deposit")
    facts = state.get("facts", {})
    notice_text = assemble_legal_notice(domain, facts)
    pdf_bytes = generate_legal_notice_pdf(notice_text)
    
    return Response(
        content=bytes(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Legal_Notice_{session_id}.pdf"
        }
    )


def process_chat_turn(
    session_id: str,
    user_msg: str,
    audio_url: Optional[str] = None,
    language_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Core state machine loop for a single conversation turn:
    1. Persists user message in SQLite.
    2. Runs Triage (if domain unknown).
    3. Triggers escalation/refusal if out of scope.
    4. Extracts/updates facts against Grounding KB.
    5. Checks missing variables -> generates targeted clarification OR assembles notice.
    6. Commits state and returns full result payload.
    """
    # 1. Commit user message to SQLite chat_history
    save_chat_message(session_id=session_id, role="user", content=user_msg, audio_url=audio_url)

    # 2. Fetch existing state & history
    existing_state = get_case_state(session_id)
    history = get_chat_history(session_id, limit=5)

    current_domain = existing_state.get("domain") if existing_state else "unknown"
    current_facts = existing_state.get("facts", {}) if existing_state else {}

    # 3. If domain is unknown, run Triage Classification
    if current_domain == "unknown" or not current_domain:
        triage = classify_user_intent(user_msg)
        current_domain = triage.domain

        # Handle Out of Scope & Escalation
        if triage.domain == "out_of_scope" or triage.is_escalation:
            escalation_msg = (
                "⚠️ **Aapko ek Enrolled Advocate ya Official Legal Helpline se sampark karne ki salah di jaati hai.**\n\n"
                "Kanooni aur suraksha niyamon ke mutabiq, criminal mamle, gharelu hinsa (domestic violence), "
                "dahej vivad, ya family/divorce mamlon me automated legal drafting karna kanooni taur par uchit nahi hai.\n\n"
                "**Emergency & Free Legal Aid Contacts:**\n"
                "- **National Legal Services Authority (NALSA):** 15100 (Free 24x7 Legal Aid)\n"
                "- **Women's National Helpline:** 1091 / 181\n"
                "- **Emergency Police Support:** 112\n\n"
                f"*Reason:* {triage.escalation_reason or 'Domain falls outside civil deposit and wage recovery scope.'}"
            )
            upsert_case_state(
                session_id=session_id,
                domain="out_of_scope",
                facts=current_facts,
                is_complete=False,
                escalation_triggered=True,
                escalation_reason=triage.escalation_reason
            )
            save_chat_message(session_id=session_id, role="assistant", content=escalation_msg)
            return {
                "session_id": session_id,
                "domain": "out_of_scope",
                "reply": escalation_msg,
                "is_complete": False,
                "escalation_triggered": True,
                "escalation_reason": triage.escalation_reason,
                "missing_variables": [],
                "facts": {},
                "legal_notice_draft": None
            }

    # 4. In-Scope: Extraction & Missing Variable Audit Loop
    updated_facts = extract_facts(
        domain=current_domain,
        new_message=user_msg,
        current_facts=current_facts,
        recent_history=history
    )
    
    missing_vars = check_missing_variables(current_domain, updated_facts)
    is_complete = len(missing_vars) == 0

    legal_draft = None
    if is_complete:
        # Generate the formal legal notice from deterministic template
        legal_draft = assemble_legal_notice(current_domain, updated_facts)
        kb = get_kb(current_domain)
        standing_text = kb["grounded_legal_standing"]["hi"] if kb else ""
        
        reply_msg = (
            f"✅ **Aapke sabhi zaroori facts verify ho chuke hain.**\n\n"
            f"**Aapki Kanooni Sthiti (Legal Standing):**\n{standing_text}\n\n"
            f"Maine aapke liye ek Formal Legal Notice of Demand draft kar diya hai. "
            f"Aap ise verify karke samne wali party ko Speed Post, WhatsApp, ya Email ke zariye bhej sakte hain."
        )
    else:
        # Generate targeted conversational clarification in user's detected regional language
        reply_msg = generate_clarification_response(
            domain=current_domain,
            missing_fields=missing_vars,
            user_message=user_msg,
            facts=updated_facts,
            language_code=language_code
        )

    # 5. Commit state updates back to SQLite
    upsert_case_state(
        session_id=session_id,
        domain=current_domain,
        facts=updated_facts,
        is_complete=is_complete,
        escalation_triggered=False,
        escalation_reason=None
    )
    save_chat_message(session_id=session_id, role="assistant", content=reply_msg)

    return {
        "session_id": session_id,
        "domain": current_domain,
        "reply": reply_msg,
        "is_complete": is_complete,
        "escalation_triggered": False,
        "escalation_reason": None,
        "missing_variables": missing_vars,
        "facts": updated_facts,
        "legal_notice_draft": legal_draft
    }

@app.post("/chat/{session_id}", response_model=ChatResponse)
def handle_chat(session_id: str, request: ChatRequest):
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    # Auto-detect language for text if not specified
    lang = request.language_code
    if not lang:
        if any(w in user_msg for w in ["आहे", "नाही", "माझं", "माझे", "आम्ही", "करा", "करावे", "मिळत", "रुपये", "घरमालक"]):
            lang = "mr-IN"
        elif any(w in user_msg for w in ["hai", "nahi", "raha", "diya", "karo", "makaan", "kiraya", "bhaiya"]):
            lang = "hi-IN"

    result = process_chat_turn(session_id=session_id, user_msg=user_msg, audio_url=request.audio_url, language_code=lang)
    return ChatResponse(**result)

@app.post("/audio-chat/{session_id}", response_model=AudioChatResponse)
async def handle_audio_chat(session_id: str, file: UploadFile = File(...)):
    """
    Multimodal Voice Endpoint:
    1. Ingests user audio recording.
    2. Transcribes & detects dialect via Sarvam Saaras STT.
    3. Runs extraction & dialogue loop in detected dialect.
    4. Generates spoken audio reply via Sarvam Bulbul TTS.
    5. Returns structured JSON + base64 audio.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Received empty audio file.")

    # 1. Transcribe voice via Sarvam Saaras STT
    user_transcription, detected_language = transcribe_audio_file(file_bytes, filename=file.filename or "recording.wav")
    
    if not user_transcription:
        raise HTTPException(status_code=422, detail="Failed to transcribe audio. Please speak clearly or use text input.")

    # 2. Process turn through core extraction loop in user's spoken language
    turn_result = process_chat_turn(
        session_id=session_id,
        user_msg=user_transcription,
        audio_url=f"audio_input_{session_id}_{file.filename}",
        language_code=detected_language
    )

    # 3. Generate voice reply via Sarvam Bulbul TTS
    assistant_audio_b64 = generate_voice_response(
        text=turn_result["reply"],
        language_code=detected_language if detected_language != "unknown" else "hi-IN"
    )

    return AudioChatResponse(
        session_id=session_id,
        domain=turn_result["domain"],
        user_transcription=user_transcription,
        detected_language=detected_language,
        reply=turn_result["reply"],
        audio_base64=assistant_audio_b64,
        is_complete=turn_result["is_complete"],
        escalation_triggered=turn_result["escalation_triggered"],
        escalation_reason=turn_result.get("escalation_reason"),
        missing_variables=turn_result["missing_variables"],
        facts=turn_result["facts"],
        legal_notice_draft=turn_result.get("legal_notice_draft")
    )
