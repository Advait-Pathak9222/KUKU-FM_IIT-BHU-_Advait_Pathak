import streamlit as st
import requests
import base64
import uuid
import json
import os
import hashlib

# --- Page Configuration ---
st.set_page_config(
    page_title="NyayaMitra | Everyday Indic AI Lawyer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern, Clean CSS Styling ---
st.markdown("""
<style>
    /* Global Fonts & Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Area */
    .brand-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .brand-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
    }
    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.1);
        color: #E2E8F0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-right: 0.4rem;
    }

    /* Fact Sheet Cards in Sidebar */
    .fact-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .fact-key {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        color: #64748B;
        margin-bottom: 0.15rem;
    }
    .fact-val {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0F172A;
    }

    /* Notice Card */
    .notice-preview-box {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #2563EB;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
    }

    /* Guardrail Alert */
    .guardrail-box {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 4px solid #DC2626;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #991B1B;
        margin-bottom: 1rem;
    }

    /* Audio Pill */
    .audio-tag {
        font-size: 0.8rem;
        font-weight: 600;
        color: #2563EB;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Streamlit Cloud Secrets Loading ---
try:
    if hasattr(st, "secrets") and "SARVAM_API_KEY" in st.secrets:
        os.environ["SARVAM_API_KEY"] = str(st.secrets["SARVAM_API_KEY"])
    if hasattr(st, "secrets") and "USE_MOCK_SARVAM" in st.secrets:
        os.environ["USE_MOCK_SARVAM"] = str(st.secrets["USE_MOCK_SARVAM"])
except Exception:
    pass

# --- Backend Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "case_state" not in st.session_state:
    st.session_state.case_state = {
        "domain": "unknown",
        "facts": {},
        "is_complete": False,
        "missing_variables": [],
        "escalation_triggered": False,
        "legal_notice_draft": None
    }

if "last_processed_audio_hash" not in st.session_state:
    st.session_state.last_processed_audio_hash = None

if "recorder_counter" not in st.session_state:
    st.session_state.recorder_counter = 0

# --- Hybrid Dispatcher: Microservice HTTP + In-Process Cloud Fallback ---
def send_text_message(message: str):
    session_id = st.session_state.session_id
    payload = {"message": message}
    
    # 1. Try microservice HTTP call if backend is active
    try:
        res = requests.post(f"{BACKEND_URL}/chat/{session_id}", json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    except Exception:
        pass

    # 2. In-Process Fallback (Enables 1-Click Streamlit Community Cloud Deployment)
    try:
        from backend.app.main import process_chat_turn
        lang = None
        if any(w in message for w in ["आहे", "नाही", "माझं", "माझे", "आम्ही", "करा", "करावे", "मिळत", "रुपये", "घरमालक"]):
            lang = "mr-IN"
        elif any(w in message for w in ["hai", "nahi", "raha", "diya", "karo", "makaan", "kiraya", "bhaiya"]):
            lang = "hi-IN"
        return process_chat_turn(session_id=session_id, user_msg=message, language_code=lang)
    except Exception as e:
        return {"reply": f"⚠️ Error processing text: {e}", "error": True}

def send_audio_message(audio_bytes: bytes, filename: str = "voice.wav"):
    session_id = st.session_state.session_id
    files = {"file": (filename, audio_bytes, "audio/wav")}
    
    # 1. Try microservice HTTP call if backend is active
    try:
        res = requests.post(f"{BACKEND_URL}/audio-chat/{session_id}", files=files, timeout=25)
        if res.status_code == 200:
            return res.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    except Exception:
        pass

    # 2. In-Process Fallback (Enables 1-Click Streamlit Community Cloud Deployment)
    try:
        from backend.app.main import process_chat_turn
        from backend.app.services.voice_service import transcribe_audio_file, generate_voice_response
        transcript, lang = transcribe_audio_file(audio_bytes, filename=filename)
        if not transcript:
            return {"reply": "Failed to transcribe audio. Please speak clearly or use text input.", "error": True}
        turn_res = process_chat_turn(session_id=session_id, user_msg=transcript, language_code=lang)
        audio_b64 = generate_voice_response(turn_res["reply"], language_code=lang)
        turn_res["user_transcription"] = transcript
        turn_res["detected_language"] = lang
        turn_res["audio_base64"] = audio_b64
        return turn_res
    except Exception as e:
        return {"reply": f"⚠️ Voice processing error: {e}", "error": True}

# --- Sidebar: Transparent Reasoning & Fact Sheet ---
with st.sidebar:
    st.markdown("### 🏛️ Case Intelligence")
    st.caption("Live SQLite Audit Trail & Fact Extractor")
    
    st.markdown(f"**Session:** `{st.session_state.session_id}`")
    
    if st.button("🔄 Reset / Start New Case", use_container_width=True):
        st.session_state.session_id = f"user_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.session_state.case_state = {
            "domain": "unknown",
            "facts": {},
            "is_complete": False,
            "missing_variables": [],
            "escalation_triggered": False,
            "legal_notice_draft": None
        }
        st.session_state.last_processed_audio_hash = None
        st.session_state.recorder_counter += 1
        st.rerun()

    st.markdown("---")
    
    # Domain & Completeness Status
    curr_domain = st.session_state.case_state.get("domain", "unknown")
    is_complete = st.session_state.case_state.get("is_complete", False)
    is_escalation = st.session_state.case_state.get("escalation_triggered", False)
    facts = st.session_state.case_state.get("facts", {})
    missing = st.session_state.case_state.get("missing_variables", [])

    domain_display = "UNKNOWN (LISTENING)"
    if curr_domain == "rental_deposit":
        domain_display = "🏠 TENANCY DEPOSIT"
    elif curr_domain == "unpaid_salary":
        domain_display = "💼 UNPAID SALARY"
    elif curr_domain == "out_of_scope":
        domain_display = "🚨 OUT OF SCOPE"

    st.markdown(f"**Dispute Type:** `{domain_display}`")

    # Progress Calculation
    total_expected = len(facts) + len(missing)
    if total_expected > 0:
        progress = len(facts) / total_expected
        st.progress(progress, text=f"Facts Verified: {len(facts)}/{total_expected}")
    
    if is_complete:
        st.success("✅ **Notice of Demand Ready!**")
    elif is_escalation:
        st.error("⚠️ **Legal Aid Escalation Mandated**")
    else:
        st.info("🔍 Fact Gathering in Progress")

    # Formatted Fact Cards (Clean UI instead of raw JSON)
    st.markdown("#### 📋 Extracted Facts")
    if facts:
        for k, v in facts.items():
            clean_key = k.replace("_", " ").title()
            val_display = str(v)
            if "amount" in k.lower():
                try:
                    val_display = f"₹{int(float(v)):,}"
                except ValueError:
                    pass
            st.markdown(f"""
            <div class="fact-card">
                <div class="fact-key">{clean_key}</div>
                <div class="fact-val">{val_display}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No entities extracted yet. Speak or type your problem.")

    # Missing fields
    if missing:
        st.markdown("#### ⏳ Information Needed")
        for m in missing:
            st.markdown(f"- 🔸 `{m.replace('_', ' ').title()}`")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Test Scenarios")
    if st.button("📋 Bangalore Deposit Case", use_container_width=True):
        st.session_state.preset_input = "Hi sir, maine 15 October ko Indiranagar Bangalore ka flat khali kiya tha. Landlord Ramesh Kumar ne 80,000 me se 35,000 painting ke kaat liye hain bina kisi bill ke. Agreement aur WhatsApp chat hai mere paas."
        st.rerun()
    if st.button("💼 Noida Salary Default", use_container_width=True):
        st.session_state.preset_input = "TechNova Solutions Noida me kaam karta hoon. Last 2 months September aur October ki salary 1,20,000 roki hui hai. Resign kar chuka hoon offer letter aur relieving letter hai."
        st.rerun()
    if st.button("🚨 Guardrail Safety Test", use_container_width=True):
        st.session_state.preset_input = "Mera pati aur uske gharwale dahej ke liye maar-peet kar rahe hain aur mera bachha chheen liya hai. Mujhe FIR karni hai aur divorce lena hai."
        st.rerun()

# --- Main App Header ---
st.markdown("""
<div class="brand-header">
    <div class="brand-title">⚖️ NyayaMitra (न्यायमित्र)</div>
    <div class="brand-subtitle">Conversational Indic Legal Aid for Everyday Civil Disputes • Powered by Sarvam AI & FastAPI</div>
    <div>
        <span class="pill-badge">🎙️ Saaras Indic STT</span>
        <span class="pill-badge">🧠 Sarvam-105B Reasoning</span>
        <span class="pill-badge">🔊 Bulbul Indic TTS</span>
        <span class="pill-badge">🛡️ Zero-Hallucination Statute Whitelist</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Render Chat History
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Render audio player cleanly if audio bytes/b64 exists
            if msg.get("audio_bytes"):
                st.audio(msg["audio_bytes"], format="audio/wav")
            elif msg.get("audio_b64"):
                try:
                    raw_audio = base64.b64decode(msg["audio_b64"])
                    st.audio(raw_audio, format="audio/wav")
                except Exception:
                    pass

# If Legal Draft is Complete, show the Document Box
if st.session_state.case_state.get("is_complete") and st.session_state.case_state.get("legal_notice_draft"):
    st.markdown("""
    <div class="notice-preview-box">
        <h3 style="margin-top:0; color:#1E3A8A;">📄 Verified Legal Notice of Demand</h3>
        <p style="color:#64748B; font-size:0.9rem;">This statutory demand letter has been generated with verified facts and grounded under Section 73 of the Indian Contract Act, 1872.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("👁️ View Full Legal Notice Document", expanded=True):
        st.markdown(st.session_state.case_state["legal_notice_draft"])
        
    btn_col1, btn_col2 = st.columns([1, 3])
    with btn_col1:
        pdf_bytes = None
        pdf_url = f"{BACKEND_URL}/notice/{st.session_state.session_id}/pdf"
        try:
            pdf_res = requests.get(pdf_url, timeout=5)
            if pdf_res.status_code == 200:
                pdf_bytes = pdf_res.content
        except Exception:
            pass

        if not pdf_bytes and st.session_state.case_state.get("legal_notice_draft"):
            try:
                from backend.app.services.pdf_generator import generate_legal_notice_pdf
                pdf_bytes = generate_legal_notice_pdf(st.session_state.case_state["legal_notice_draft"])
            except Exception:
                pass

        if pdf_bytes:
            st.download_button(
                label="📥 Download Notice (PDF)",
                data=pdf_bytes,
                file_name=f"Legal_Notice_{st.session_state.session_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.caption("PDF service unavailable.")
    with btn_col2:
        st.download_button(
            label="📋 Download Markdown Copy",
            data=st.session_state.case_state["legal_notice_draft"],
            file_name=f"Legal_Notice_{st.session_state.session_id}.md",
            mime="text/markdown"
        )

# --- Clean Input Controls (Tabs for Voice vs Text) ---
st.markdown("---")
tab_voice, tab_text = st.tabs(["🎙️ Speak Voice Note (Indic / Hindi / Hinglish)", "💬 Type Message"])

# TAB 1: VOICE INPUT
with tab_voice:
    v_col1, v_col2 = st.columns([2, 1])
    with v_col1:
        st.caption("Click the red button below, speak your problem naturally in Hindi or Hinglish, then click stop.")
        # Unique dynamic key prevents stale widget replay loops
        recorder_key = f"voice_input_{st.session_state.recorder_counter}"
        audio_val = st.audio_input("Record Voice", key=recorder_key, label_visibility="collapsed")
    with v_col2:
        with st.expander("📁 Or Upload Audio"):
            uploaded_audio = st.file_uploader("Upload .wav / .mp3", type=["wav", "mp3", "m4a"], key=f"uploader_{st.session_state.recorder_counter}")
            if uploaded_audio is not None and audio_val is None:
                audio_val = uploaded_audio

    # SAFE DE-DUPLICATED AUDIO PROCESSING LOOP
    if audio_val is not None:
        raw_audio_bytes = audio_val.getvalue() if hasattr(audio_val, "getvalue") else audio_val.read()
        if raw_audio_bytes and len(raw_audio_bytes) > 0:
            audio_hash = hashlib.md5(raw_audio_bytes).hexdigest()
            
            # CRITICAL CHECK: Only process if this is a NEW recording!
            if audio_hash != st.session_state.last_processed_audio_hash:
                st.session_state.last_processed_audio_hash = audio_hash
                
                # 1. Immediately append user voice message
                st.session_state.messages.append({
                    "role": "user",
                    "content": "🎙️ *(Voice note submitted)*",
                    "audio_bytes": raw_audio_bytes
                })

                # 2. Mask latency with spinner
                with st.spinner("🎙️ Sarvam Saaras is transcribing speech & extracting facts..."):
                    res = send_audio_message(raw_audio_bytes, filename=getattr(audio_val, "name", "recording.wav"))

                # 3. Handle response exactly once
                if not res.get("error"):
                    # Update user message with transcript
                    if res.get("user_transcription"):
                        st.session_state.messages[-1]["content"] = f"🎙️ **Transcribed ({res.get('detected_language', 'Indic')}):**\n\"{res['user_transcription']}\""

                    # Append Assistant reply
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": res["reply"],
                        "audio_b64": res.get("audio_base64")
                    })

                    # Update case state
                    st.session_state.case_state = {
                        "domain": res["domain"],
                        "facts": res["facts"],
                        "is_complete": res["is_complete"],
                        "missing_variables": res.get("missing_variables", []),
                        "escalation_triggered": res.get("escalation_triggered", False),
                        "legal_notice_draft": res.get("legal_notice_draft")
                    }
                    # Increment counter to refresh widget cleanly on next turn
                    st.session_state.recorder_counter += 1
                    st.rerun()
                else:
                    st.error(res["reply"])

# TAB 2: TEXT INPUT
with tab_text:
    default_text = st.session_state.pop("preset_input", "")
    text_val = st.chat_input("Type your situation in Hindi, Hinglish, or English...", key="text_chat_input")
    
    active_text = text_val or default_text
    if active_text:
        st.session_state.messages.append({"role": "user", "content": active_text})
        
        with st.spinner("🧠 NyayaMitra is analyzing legal statutes and extracting facts..."):
            res = send_text_message(active_text)
            
        if not res.get("error"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": res["reply"]
            })
            st.session_state.case_state = {
                "domain": res["domain"],
                "facts": res["facts"],
                "is_complete": res["is_complete"],
                "missing_variables": res.get("missing_variables", []),
                "escalation_triggered": res.get("escalation_triggered", False),
                "legal_notice_draft": res.get("legal_notice_draft")
            }
            st.rerun()
        else:
            st.error(res["reply"])
