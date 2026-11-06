import streamlit as st
import requests
import base64
import uuid
import json
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="NyayaMitra | Everyday Indic AI Lawyer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .stat-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #E0E7FF;
        color: #3730A3;
        margin-right: 0.5rem;
    }
    .legal-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 1rem;
    }
    .guardrail-alert {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 5px solid #DC2626;
        border-radius: 8px;
        padding: 1rem;
        color: #991B1B;
    }
</style>
""", unsafe_allow_html=True)

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

if "latest_audio_b64" not in st.session_state:
    st.session_state.latest_audio_b64 = None

# --- Helper Functions ---
def fetch_session_state(session_id: str):
    try:
        res = requests.get(f"{BACKEND_URL}/state/{session_id}", timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("case_state"):
                st.session_state.case_state = data["case_state"]
    except Exception:
        pass

def send_text_message(message: str):
    session_id = st.session_state.session_id
    payload = {"message": message}
    try:
        res = requests.post(f"{BACKEND_URL}/chat/{session_id}", json=payload, timeout=25)
        if res.status_code == 200:
            return res.json()
        else:
            return {"reply": f"⚠️ Server Error ({res.status_code}): {res.text}", "error": True}
    except Exception as e:
        return {"reply": f"⚠️ Failed to reach backend API at {BACKEND_URL}: {e}", "error": True}

def send_audio_message(audio_bytes: bytes, filename: str = "voice_input.wav"):
    session_id = st.session_state.session_id
    files = {"file": (filename, audio_bytes, "audio/wav")}
    try:
        res = requests.post(f"{BACKEND_URL}/audio-chat/{session_id}", files=files, timeout=35)
        if res.status_code == 200:
            return res.json()
        else:
            return {"reply": f"⚠️ Audio processing failed ({res.status_code}): {res.text}", "error": True}
    except Exception as e:
        return {"reply": f"⚠️ Failed to reach voice backend at {BACKEND_URL}: {e}", "error": True}

# --- Sidebar: Real-Time Reasoning & State Audit ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/courthouse.png", width=64)
    st.title("Reasoning & State Engine")
    st.caption("Real-time inspection of SQLite database state")
    
    st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    if st.button("🔄 Reset / New Session"):
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
        st.session_state.latest_audio_b64 = None
        st.rerun()

    st.markdown("---")
    
    # Domain & Completeness Status
    curr_domain = st.session_state.case_state.get("domain", "unknown")
    st.markdown(f"**Domain:** `{curr_domain.upper()}`")
    
    is_complete = st.session_state.case_state.get("is_complete", False)
    if is_complete:
        st.success("🎯 Status: 100% Facts Complete (Notice Ready)")
    elif st.session_state.case_state.get("escalation_triggered"):
        st.error("🚨 Escalation: Real Lawyer Referral Mandated")
    else:
        st.info("🔍 Status: Fact Extraction & Clarification Active")

    # Extracted Facts Table
    st.subheader("Extracted Facts (SQLite)")
    facts = st.session_state.case_state.get("facts", {})
    if facts:
        st.json(facts)
    else:
        st.caption("No entities extracted yet. Speak or type your story to begin.")

    # Missing Variables
    missing = st.session_state.case_state.get("missing_variables", [])
    if missing:
        st.markdown("**Pending Required Variables:**")
        for m in missing:
            st.markdown(f"- ⏳ `{m}`")

    st.markdown("---")
    st.markdown("### Preloaded Scenarios")
    if st.button("📋 Load Bangalore Deposit Case"):
        prompt = "Hi sir, maine 15 October ko Indiranagar Bangalore ka flat khali kiya tha. Landlord Ramesh Kumar ne 80,000 me se 35,000 painting ke kaat liye hain bina kisi bill ke. Agreement aur WhatsApp chat hai mere paas."
        st.session_state.preset_input = prompt
        st.rerun()
    if st.button("💼 Load Noida Salary Case"):
        prompt = "TechNova Solutions Noida me kaam karta hoon. Last 2 months September aur October ki salary 1,20,000 roki hui hai. Resign kar chuka hoon offer letter aur relieving letter hai."
        st.session_state.preset_input = prompt
        st.rerun()
    if st.button("⚠️ Test Guardrail Trigger"):
        prompt = "Mera pati aur uske gharwale dahej ke liye maar-peet kar rahe hain aur mera bachha chheen liya hai. Mujhe FIR karni hai aur divorce lena hai."
        st.session_state.preset_input = prompt
        st.rerun()

# --- Main Interface ---
st.markdown('<div class="main-header">⚖️ NyayaMitra (न्यायमित्र)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Conversational Indic Legal Assistant for Everyday Grievances • Powered by Sarvam AI & FastAPI</div>', unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem;">
    <span class="stat-badge">🎙️ Saaras Indic STT</span>
    <span class="stat-badge">🧠 Sarvam-105B Reasoning</span>
    <span class="stat-badge">🔊 Bulbul Indic TTS</span>
    <span class="stat-badge">🛡️ Zero-Hallucination Statute Grounding</span>
</div>
""", unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("audio_b64"):
            audio_html = f"""
            <audio controls style="width: 100%; margin-top: 8px;">
                <source src="data:audio/wav;base64,{msg['audio_b64']}" type="audio/wav">
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

# Option A: Seamless Autoplay for latest assistant turn
if st.session_state.latest_audio_b64:
    autoplay_html = f"""
    <audio autoplay style="display:none;">
        <source src="data:audio/wav;base64,{st.session_state.latest_audio_b64}" type="audio/wav">
    </audio>
    """
    st.markdown(autoplay_html, unsafe_allow_html=True)
    # Clear after playing once
    st.session_state.latest_audio_b64 = None

# If legal draft is ready, render highlight box and download options
if st.session_state.case_state.get("is_complete") and st.session_state.case_state.get("legal_notice_draft"):
    st.markdown("---")
    st.markdown("### 📄 Generated Legal Document")
    with st.expander("👁️ View Draft Notice of Demand (Speed Post / WhatsApp Format)", expanded=True):
        st.markdown(st.session_state.case_state["legal_notice_draft"])
    
    col1, col2 = st.columns([1, 4])
    with col1:
        # Download as PDF button
        pdf_url = f"{BACKEND_URL}/notice/{st.session_state.session_id}/pdf"
        try:
            pdf_res = requests.get(pdf_url)
            if pdf_res.status_code == 200:
                st.download_button(
                    label="📥 Download Legal Notice (PDF)",
                    data=pdf_res.content,
                    file_name=f"Legal_Notice_{st.session_state.session_id}.pdf",
                    mime="application/pdf"
                )
        except Exception:
            st.caption("PDF service offline.")
    with col2:
        st.download_button(
            label="📋 Download Markdown Copy",
            data=st.session_state.case_state["legal_notice_draft"],
            file_name=f"Legal_Notice_{st.session_state.session_id}.md",
            mime="text/markdown"
        )

# --- Input Area (Voice + Text) ---
st.markdown("---")
input_col1, input_col2 = st.columns([1, 3])

with input_col1:
    st.markdown("🎙️ **Voice Input (Indic Speech)**")
    audio_val = st.audio_input("Record your voice", key="voice_recorder")

with input_col2:
    st.markdown("💬 **Text Input (Hindi / Hinglish / English)**")
    default_text = st.session_state.pop("preset_input", "")
    text_val = st.chat_input("Apni samasya batayein ya type karein...", key="text_chat_input")

# Handle Voice Input
if audio_val is not None:
    audio_bytes = audio_val.read()
    if audio_bytes:
        with st.chat_message("user"):
            st.markdown("*(Audio message sent...)*")
            st.audio(audio_bytes, format="audio/wav")
        st.session_state.messages.append({"role": "user", "content": "*(Audio message sent)*"})

        # Optimistic UI Latency Masking
        with st.spinner("🎙️ Sarvam Saaras is transcribing Indic speech and verifying facts..."):
            res = send_audio_message(audio_bytes, filename=getattr(audio_val, "name", "recording.wav"))

        if not res.get("error"):
            # Update user transcription
            if res.get("user_transcription"):
                st.session_state.messages[-1]["content"] = f"🎙️ **Transcribed ({res.get('detected_language', 'Indic')}):**\n\"{res['user_transcription']}\""
            
            # Append Assistant Message
            reply_text = res["reply"]
            audio_b64 = res.get("audio_base64")
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply_text,
                "audio_b64": audio_b64
            })
            st.session_state.latest_audio_b64 = audio_b64
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

# Handle Text Input (or preset load)
active_text = text_val or default_text
if active_text:
    with st.chat_message("user"):
        st.markdown(active_text)
    st.session_state.messages.append({"role": "user", "content": active_text})

    with st.spinner("🧠 NyayaMitra is analyzing your situation against statutory legal grounding..."):
        res = send_text_message(active_text)

    if not res.get("error"):
        reply_text = res["reply"]
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply_text
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
