# ⚖️ NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat

> **Kuku FM Take-Home Assignment | AI Generalist Role**  
> **Candidate:** Advait Pathak  
> **Problem Chosen:** Problem 2 — Build an AI Lawyer  
> **Live Prototype:** Deployable to Streamlit Community Cloud / Local Run  
> **GitHub Repository:** [https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak](https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Sarvam AI](https://img.shields.io/badge/AI%20Suite-Sarvam%20AI-6366F1.svg)](https://www.sarvam.ai/)
[![Zero Hallucination](https://img.shields.io/badge/Guardrails-Statute%20Whitelisted-success.svg)](#-anti-hallucination--legal-grounding)

---

## 🎯 Executive Summary & Problem Framing

In India, over **90% of ordinary citizens** never approach the formal legal system for everyday civil grievances—such as **unreturned rental security deposits** or **withheld wages and severance**. For a tenant or junior employee in tier-2/tier-3 Bharat, a single advocate consultation costs ₹2,500 – ₹5,000 (often 20% to 50% of the disputed amount), legal jargon is intimidating, and drafting formal notices feels insurmountable.

While general-purpose LLMs struggle with vernacular code-mixing and dangerously hallucinate criminal sections (*e.g., advising IPC 420 for simple rent disputes*), **NyayaMitra** is purposefully engineered for everyday Indian citizens:

1. 🎙️ **Speaks & Listens in Indic Dialects:** Supports vernacular voice notes with natural code-mixing (Hindi, Marathi, Hinglish, English loanwords) powered by Sarvam AI (`saaras:v3` STT & `bulbul:v3` TTS).
2. 🛡️ **Zero-Hallucination Statute Whitelist:** Strict architectural separation between probabilistic entity extraction and deterministic legal citations (*Section 73 Indian Contract Act, Model Tenancy Act, Order 37 CPC*).
3. ⚖️ **Mandatory Legal Escalation:** Continuously screens every turn (Roman & Devanagari scripts) for criminal offenses, domestic violence, and matrimonial disputes, halting civil drafting and serving statutory helpline numbers (**NALSA 15100**, **1091**).
4. 📄 **Court-Ready Actionable Paperwork:** Generates and downloads a formal **Legal Notice of Demand** in both Markdown and crash-proof PDF with a 15-day cure period.
5. 🥊 **Negotiation Roleplay Coach:** Roleplays the stubborn Landlord or defensive HR Manager so citizens can practice arguing their case, paired with live tactical coaching tips.
6. ⚙️ **Hot-Swappable Model Router:** Swap dynamically between `sarvam-105b-conversations`, `OpenAI`, `Gemini`, or `Anthropic Claude` via `.env` or the UI sidebar during live evaluations.

---

## 🌐 Live Cloud Deployment (For Evaluators & Judges)

NyayaMitra features a **Hybrid Dispatcher Architecture**: it seamlessly runs as a distributed FastAPI microservice locally, or **completely self-contained in-process** when deployed to the cloud. Evaluators do not need to maintain any local servers to test the app.

### Deploying to Streamlit Community Cloud (60 Seconds)

1. Fork or open the GitHub repository:  
   `https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak`
2. Go to [share.streamlit.io](https://share.streamlit.io/) and click **New App**.
3. Select:
   * **Repository:** `Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak`
   * **Branch:** `main`
   * **Main file path:** `app.py`
4. Under **Advanced Settings > Secrets**, paste your Sarvam AI credentials:
   ```toml
   SARVAM_API_KEY = "your_sarvam_api_key_here"
   USE_MOCK_SARVAM = "False"
   ```
5. Click **Deploy**. Streamlit Cloud automatically provides an HTTPS endpoint (e.g. `https://nyayamitra.streamlit.app`) with native browser microphone permissions for instant mobile and desktop voice testing.

---

## 🏗️ System Architecture & Multimodal Pipeline

```
                                ┌─────────────────────────────────────────┐
                                │        Citizen User (Mobile / Web)      │
                                └────────────────────┬────────────────────┘
                                                     │ Voice (Audio WAV/MP3) or Text
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STREAMLIT FRONTEND (Option A UX: Latency Masking + Live Reasoning Sidebar)             │
│                                                                                        │
│   • MD5 Audio De-duplication Cache (Eliminates recursive audio loop glitches)           │
│   • Hybrid Dispatcher: HTTP Microservice ──[fallback]──► In-Process Execution         │
└────────────────────────────────────┬───────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PERCEPTION & SAFETY GUARDRAILS                                                         │
│                                                                                        │
│   1. Sarvam Saaras STT (`saaras:v3`): Indic Speech-to-Text & Dialect Auto-Detection     │
│   2. Deterministic Safety Triage: Regex + Semantic Check for Out-of-Scope Risks        │
│      ├─ If Criminal / Domestic Abuse / Dowry ──► Immediate NALSA 15100 Escalation      │
│      └─ If Tenancy / Salary Grievance        ──► Proceed to Fact Gathering             │
└────────────────────────────────────┬───────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ COGNITIVE REASONING & EXTRACTION MACHINE                                               │
│                                                                                        │
│   • Sarvam-105B Reasoning: Conversational extraction with regional code-mixing         │
│   • Missing-Variable Audit: Evaluates 5-part timeline completeness against schema      │
│   • Evidence Risk Handler: Handles oral agreements without deadlocking pipeline         │
│   • Persistent State: Atomic upsert into SQLite (`ai_lawyer.db`)                       │
└────────────────────────────────────┬───────────────────────────────────────────────────┘
                                     │
                ┌────────────────────┴────────────────────┐
                ▼                                         ▼
┌───────────────────────────────┐       ┌────────────────────────────────────────────────┐
│   IF FACTS INCOMPLETE (< 5)   │       │   IF COMPLETE (All 5 Essential Facts Verified)  │
│                               │       │                                                │
│ • Targeted Indic Follow-up    │       │ • Deterministic Legal Notice Assembly          │
│ • Sarvam Bulbul TTS Synthesis │       │ • Whitelisted Statutes (Sec 73 Contract Act)   │
│ • Dynamic Audio Playback      │       │ • Court-Ready FPDF2 Vector PDF Download        │
└───────────────────────────────┘       └────────────────────────────────────────────────┘
```

---

## 🛡️ Anti-Hallucination & Legal Grounding

LLM hallucinations in legal applications can lead to severe real-world harm. NyayaMitra enforces a strict boundary between probabilistic generation and deterministic legal enforcement:

| Component | Responsibility | Guardrail Mechanism |
| :--- | :--- | :--- |
| **Entity Extraction** | Extracting names, dates, amounts, deductions, evidence | LLM operates solely on user statements; never infers missing numbers. |
| **Statute Whitelist** | Legal citations and statutory grounds | **Zero LLM citation generation.** Bound strictly to vetted statutory templates: *Section 73 Indian Contract Act 1872*, *Model Tenancy Act principles*, *Order 37 CPC*. |
| **Evidentiary Deadlocks** | Tenant lacks written agreement / cash paid | System marks `oral_agreement_only`, explains legal risk transparently, and proceeds without deadlocking. |
| **Mandatory Escalation** | Criminal violence, matrimonial, domestic abuse | Immediate pipeline halt. LLM drafting disabled. Free legal aid helplines provided (**NALSA: 15100**, **Women's Helpline: 1091**). |

---

## 💰 Unit Economics & Real-World Production Scale

Kuku FM explicitly evaluates submissions on *"what it costs at real-world volume and how it holds up at scale"*.

### 1. Cost per Case Resolved (50 Paise per Citizen)

| Pipeline Step | Provider & Model | Workload / Token Budget | Cost (INR) |
| :--- | :--- | :--- | :--- |
| **Voice Perception** | Sarvam Saaras (`saaras:v3`) | ~20s Indic audio ingestion + dialect detection | ₹0.15 |
| **Cognitive Extraction** | Sarvam-105B-Conversations | ~1,200 tokens across 2 conversational turns | ₹0.20 |
| **Spoken Advisory** | Sarvam Bulbul (`bulbul:v3`) | ~15s synthesized Indic audio response | ₹0.15 |
| **Notice Generation & PDF** | Python Core (Deterministic) | Slot-filling + FPDF2 rendering on local CPU | ₹0.00 |
| **Total Cost per Case** | **End-to-End Civil Pipeline** | **Complete Audio Consultation + Verified Notice** | **~₹0.50** |

> **Economic Impact:** Compared to a traditional advocate consultation (₹2,500 – ₹5,000), NyayaMitra achieves a **99.98% cost reduction**, transforming legal recourse into an affordable 50-paise utility for Bharat.

### 2. Infrastructure at 100,000 Monthly Grievance Scale

* **Stateless Compute:** FastAPI services run containerized (Docker on AWS ECS / GCP Cloud Run) with CPU auto-scaling (100 concurrent requests per node).
* **Database Transition:** The local SQLite storage is architected as an atomic document-state store; transitioning to Amazon Aurora PostgreSQL (or Supabase) requires swapping the connection string, managed with PgBouncer connection pooling.
* **Safety Ceilings:** Sessions are hard-capped at 4 clarification turns to prevent token runaway costs on uncooperative inputs.
* **Monthly Run-Rate for 100,000 Citizens:**
  * Container Compute (2–4 vCPU nodes): ~$80/month
  * Managed Database (Postgres): ~$50/month
  * Sarvam AI API Volume (100,000 cases × ₹0.50): ₹50,000 (~$600/month)
  * **Total Run-Rate: ~$730 / month (~₹61,000) to serve 100,000 Indian citizens.**

---

## 🧪 Evaluation Suite & Test Results

The system was evaluated against **8 intentional, messy, real-world conversational scenarios** (unedited test outputs available in [`raw_outputs/`](raw_outputs/)):

| Test ID | Scenario Description | Domain | Complete? | Escalation? | Facts | Outcome |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **TC_01** | Rental Deposit — Vague Hindi Story | `rental_deposit` | ❌ | No | 1 | Follow-up for deposit & address |
| **TC_02** | Rental Deposit — Dense Hinglish (Bangalore 2BHK) | `rental_deposit` | ✅ | No | 8 | 📄 Legal Notice Drafted |
| **TC_03** | Rental Deposit — Bogus Damage Deduction (Pune) | `rental_deposit` | ✅ | No | 8 | 📄 Legal Notice Drafted |
| **TC_04** | Rental Deposit — Oral Agreement & Cash (Deadlock Test) | `rental_deposit` | ✅ | No | 8 | 📄 Evidentiary Warning + Notice |
| **TC_05** | Unpaid Salary — Emotional Rant & IPC 420 Confusion | `unpaid_salary` | ✅ | No | 8 | 📄 Legal Notice Drafted |
| **TC_06** | Unpaid Salary — Resigned Full & Final Delay (Gurugram) | `unpaid_salary` | ✅ | No | 8 | 📄 Legal Notice Drafted |
| **TC_07** | Unpaid Salary — Missing Corporate Entity Details | `unpaid_salary` | ❌ | No | 3 | Targeted follow-up for employer name |
| **TC_08** | Out of Scope — Domestic Violence & Dowry Harassment | `out_of_scope` | ❌ | 🚨 Yes | 0 | **Halted:** NALSA 15100 helpline |

To reproduce the automated evaluation suite:
```bash
python generate_raw_outputs.py
```

---

## 🚀 Quickstart & Local Setup

### 1. Installation
```bash
git clone https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git
cd KUKU-FM_IIT-BHU-_Advait_Pathak
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```ini
SARVAM_API_KEY=your_sarvam_api_key_here
USE_MOCK_SARVAM=False   # Set True to test offline with zero API credit consumption
```

### 3. Run Application
Run the Streamlit frontend (runs seamlessly in standalone mode or with backend):
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

*(Optional)* Run the FastAPI microservice in a separate terminal:
```bash
uvicorn backend.app.main:app --port 8000
```
Interactive Swagger API documentation: `http://127.0.0.1:8000/docs`

---

## 📂 Project Structure

```
├── app.py                      # Root Streamlit app (with hybrid in-process cloud fallback)
├── .streamlit/
│   ├── config.toml             # Streamlit Cloud production styling & headless settings
│   └── secrets.toml.example    # Cloud secrets configuration reference
├── backend/
│   └── app/
│       ├── main.py             # FastAPI routes (/chat, /audio-chat, /notice/{id}/pdf)
│       ├── database.py         # SQLite persistence (chat_history & case_state)
│       ├── config.py           # Configuration & credit-protection mocks
│       ├── models.py           # Pydantic schemas
│       ├── kb/                 # Grounding Knowledge Bases (Rental & Salary)
│       └── services/           # Triage, Extractor, Voice (Saaras/Bulbul), & PDF generator
├── frontend/
│   └── app.py                  # Standalone UI module
├── test_cases/
│   └── test_cases.json         # 8 messy conversational test cases
├── raw_outputs/                # Unedited evaluation transcripts & generated notices
├── SOLUTION_DOC.md             # The 2-page submission solution writeup
├── SOLUTION_DOC.pdf            # Exact 2-page compiled submission PDF
└── requirements.txt            # Minimal production dependencies
```

---

*Authored by **Advait Pathak** for the Kuku FM AI Generalist Take-Home Evaluation.*
