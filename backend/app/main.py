import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, Tuple

from .config import SARVAM_API_KEY, LLM_PROVIDER, LLM_MODEL
from .database import (
    init_db,
    save_chat_message,
    get_chat_history,
    get_case_state,
    upsert_case_state
)
from .models import ChatRequest, ChatResponse, AudioChatResponse
from .services.triage import classify_user_intent, check_deterministic_escalation
from .services.extractor import (
    extract_facts,
    extract_facts_with_reasoning,
    check_missing_variables,
    generate_clarification_response,
    generate_lawyer_turn_response,
    assemble_legal_notice,
    generate_roleplay_response
)
from .services.voice_service import (
    transcribe_audio_file,
    generate_voice_response
)
from .services.pdf_generator import generate_legal_notice_pdf
from .services.precedent_search import run_calibrated_precedent_agent
from .kb import get_kb

app = FastAPI(
    title="NyayaMitra - Everyday Indic AI Lawyer API",
    version="1.1.0",
    description="Voice and text-enabled conversational legal triage, fact extraction, negotiation roleplay, and legal notice drafting for everyday Indian civil grievances."
)

# Enable CORS for frontend clients
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
        "sarvam_api_connected": bool(os.getenv("SARVAM_API_KEY", SARVAM_API_KEY)),
        "active_llm_provider": os.getenv("LLM_PROVIDER", LLM_PROVIDER),
        "active_llm_model": os.getenv("LLM_MODEL", LLM_MODEL),
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


def _build_escalation_payload(session_id: str, current_facts: Dict[str, Any], reason: Optional[str]) -> Dict[str, Any]:
    escalation_msg = (
        "⚠️ **Aapko ek Enrolled Advocate ya Official Legal Helpline se sampark karne ki salah di jaati hai.**\n\n"
        "Kanooni aur suraksha niyamon ke mutabiq, criminal mamle, gharelu hinsa (domestic violence), "
        "dahej vivad, ya family/divorce mamlon me automated legal drafting karna kanooni taur par uchit nahi hai.\n\n"
        "**Emergency & Free Legal Aid Contacts:**\n"
        "- **National Legal Services Authority (NALSA):** 15100 (Free 24x7 Legal Aid)\n"
        "- **Women's National Helpline:** 1091 / 181\n"
        "- **Emergency Police Support:** 112\n\n"
        f"*Reason:* {reason or 'Domain falls outside civil deposit and wage recovery scope.'}"
    )
    upsert_case_state(
        session_id=session_id,
        domain="out_of_scope",
        facts=current_facts,
        is_complete=False,
        escalation_triggered=True,
        escalation_reason=reason
    )
    save_chat_message(session_id=session_id, role="assistant", content=escalation_msg)
    return {
        "session_id": session_id,
        "domain": "out_of_scope",
        "reply": escalation_msg,
        "is_complete": False,
        "escalation_triggered": True,
        "escalation_reason": reason,
        "missing_variables": [],
        "facts": {},
        "legal_notice_draft": None
    }


def process_chat_turn(
    session_id: str,
    user_msg: str,
    audio_url: Optional[str] = None,
    language_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Core state machine loop for a single conversation turn:
    1. Fetches prior conversation history & state from SQLite.
    2. Runs continuous safety guardrail check.
    3. Runs Triage (if domain unknown).
    4. Extracts/updates facts + performs financial/CTC calculations using full conversation history.
    5. Generates non-repetitive, context-aware LLM lawyer response (and assembles deterministic Legal Notice when complete).
    6. Commits state and returns full result payload.
    """
    # 1. Fetch existing state & prior history before appending current turn
    existing_state = get_case_state(session_id)
    prior_history = get_chat_history(session_id, limit=15)

    # Save current user message to SQLite chat_history
    save_chat_message(session_id=session_id, role="user", content=user_msg, audio_url=audio_url)

    current_domain = existing_state.get("domain") if existing_state else "unknown"
    current_facts = existing_state.get("facts", {}) if existing_state else {}

    # 2. Continuous Safety Guardrail Check
    mid_turn_safety = check_deterministic_escalation(user_msg)
    if mid_turn_safety and mid_turn_safety.is_escalation:
        return _build_escalation_payload(session_id, current_facts, mid_turn_safety.escalation_reason)

    # 3. If domain is unknown, run full Triage Classification
    if current_domain == "unknown" or not current_domain:
        triage = classify_user_intent(user_msg)
        current_domain = triage.domain

        if triage.domain == "out_of_scope" or triage.is_escalation:
            return _build_escalation_payload(session_id, current_facts, triage.escalation_reason)

    # 4. In-Scope: Multi-Turn Fact Extraction + Financial Calculation Loop
    updated_facts, calc_note = extract_facts_with_reasoning(
        domain=current_domain,
        new_message=user_msg,
        current_facts=current_facts,
        recent_history=prior_history
    )
    
    missing_vars = check_missing_variables(current_domain, updated_facts)
    is_complete = len(missing_vars) == 0

    # 4b. Calibrated Severity Gate & Live IndianKanoon Precedent Browsing Agent
    precedent_info = run_calibrated_precedent_agent(
        domain=current_domain,
        user_msg=user_msg,
        facts=updated_facts,
        is_complete=is_complete
    )
    updated_facts["_precedent_search"] = precedent_info

    legal_draft = assemble_legal_notice(current_domain, updated_facts) if is_complete else None

    # 5. Generate context-aware, non-repetitive AI Lawyer response
    reply_msg = generate_lawyer_turn_response(
        domain=current_domain,
        missing_fields=missing_vars,
        user_message=user_msg,
        facts=updated_facts,
        recent_history=prior_history,
        calculation_note=calc_note,
        language_code=language_code
    )

    # 6. Commit state updates back to SQLite
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
        "legal_notice_draft": legal_draft,
        "precedent_search": precedent_info
    }


def process_roleplay_turn(
    session_id: str,
    user_argument: str,
    language_code: Optional[str] = None,
    include_audio: bool = True
) -> Dict[str, Any]:
    """
    Runs a single turn of the counterparty negotiation practice simulator while
    simultaneously running Triage, Fact Extraction (with CTC/deposit calculations),
    Missing Variable Audit, Calibrated Precedent Search, and Legal Notice Assembly.
    """
    state = get_case_state(session_id)
    prior_history = get_chat_history(session_id, limit=15)
    save_chat_message(session_id=session_id, role="user", content=f"[Roleplay Argument] {user_argument}")

    current_domain = state.get("domain", "unknown") if state else "unknown"
    current_facts = state.get("facts", {}) if state else {}

    # 1. Safety Guardrail Check
    mid_turn_safety = check_deterministic_escalation(user_argument)
    if mid_turn_safety and mid_turn_safety.is_escalation:
        esc = _build_escalation_payload(session_id, current_facts, mid_turn_safety.escalation_reason)
        return {
            "counterparty_reply": esc["reply"],
            "coach_tip": "⚠️ Criminal / Domestic Violence matter detected. Civil negotiation halted.",
            "suggested_argument": "",
            "case_state": esc
        }

    # 2. If domain is unknown (or out_of_scope), classify intent from the user's argument!
    if current_domain in ("unknown", "out_of_scope", "", None):
        triage = classify_user_intent(user_argument)
        if triage.domain == "out_of_scope" or triage.is_escalation:
            esc = _build_escalation_payload(session_id, current_facts, triage.escalation_reason)
            return {
                "counterparty_reply": esc["reply"],
                "coach_tip": "⚠️ Out of scope matter detected. Please contact NALSA 15100.",
                "suggested_argument": "",
                "case_state": esc
            }
        current_domain = triage.domain

    # 3. Extract new facts + perform any math calculations mentioned during the argument
    updated_facts, calc_note = extract_facts_with_reasoning(
        domain=current_domain,
        new_message=user_argument,
        current_facts=current_facts,
        recent_history=prior_history
    )
    missing_vars = check_missing_variables(current_domain, updated_facts)
    is_complete = len(missing_vars) == 0

    precedent_info = run_calibrated_precedent_agent(
        domain=current_domain,
        user_msg=user_argument,
        facts=updated_facts,
        is_complete=is_complete
    )
    updated_facts["_precedent_search"] = precedent_info

    legal_draft = assemble_legal_notice(current_domain, updated_facts) if is_complete else None

    upsert_case_state(
        session_id=session_id,
        domain=current_domain,
        facts=updated_facts,
        is_complete=is_complete,
        escalation_triggered=False,
        escalation_reason=None
    )

    lang = language_code
    if not lang:
        if any(w in user_argument for w in ["आहे", "नाही", "माझं", "माझे", "आम्ही", "करा", "करावे", "मिळत", "रुपये", "घरमालक"]):
            lang = "mr-IN"
        elif any(w in user_argument for w in ["hai", "nahi", "raha", "diya", "karo", "makaan", "kiraya", "bhaiya"]):
            lang = "hi-IN"
        else:
            lang = "hi-IN"

    rp_res = generate_roleplay_response(
        domain=current_domain,
        facts=updated_facts,
        user_argument=user_argument,
        language_code=lang,
        missing_fields=missing_vars,
        recent_history=prior_history,
        calculation_note=calc_note
    )
    if include_audio and rp_res.get("counterparty_reply"):
        rp_res["audio_base64"] = generate_voice_response(
            text=rp_res["counterparty_reply"],
            language_code=lang if lang != "unknown" else "hi-IN"
        )

    rp_res["precedent_search"] = precedent_info
    rp_res["case_state"] = {
        "domain": current_domain,
        "facts": updated_facts,
        "is_complete": is_complete,
        "missing_variables": missing_vars,
        "escalation_triggered": False,
        "legal_notice_draft": legal_draft
    }
    return rp_res


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


@app.post("/roleplay/{session_id}")
def handle_roleplay(session_id: str, request: ChatRequest):
    user_arg = request.message.strip()
    if not user_arg:
        raise HTTPException(status_code=400, detail="Argument cannot be empty.")
    return process_roleplay_turn(session_id=session_id, user_argument=user_arg, language_code=request.language_code)


@app.post("/audio-roleplay/{session_id}")
async def handle_audio_roleplay(session_id: str, file: UploadFile = File(...)):
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Received empty audio file.")
    transcript, detected_lang = transcribe_audio_file(file_bytes, filename=file.filename or "roleplay.wav")
    if not transcript:
        raise HTTPException(status_code=422, detail="Failed to transcribe audio.")
    rp_res = process_roleplay_turn(session_id=session_id, user_argument=transcript, language_code=detected_lang, include_audio=True)
    rp_res["user_transcription"] = transcript
    rp_res["detected_language"] = detected_lang
    return rp_res


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
