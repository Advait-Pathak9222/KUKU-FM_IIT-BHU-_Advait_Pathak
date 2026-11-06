# NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat

> **Kuku FM Take-Home Assignment | AI Generalist Role**  
> **Candidate:** Advait Pathak  
> **Problem Chosen:** Problem 2 — Build an AI Lawyer  
> **Tech Stack:** Python 3.10+, FastAPI, SQLite, Sarvam AI Suite (Saaras STT, Sarvam-105B Reasoning, Bulbul TTS), Streamlit, FPDF2  

---

## 🎯 Project Overview

**NyayaMitra** is a voice and text-first conversational legal assistant built for ordinary people in India. It empowers vernacular citizens to resolve everyday civil grievances (**withheld rental security deposits** and **unpaid wages/severance**) without paying exorbitant advocate fees or falling victim to LLM hallucinations.

### Core Capabilities
* 🎙️ **Indic Speech Perception:** Native voice-in (Sarvam Saaras STT) and voice-out (Sarvam Bulbul TTS) supporting Hindi, Hinglish, and regional dialects.
* 🛡️ **Zero-Hallucination Statute Grounding:** Strict separation of probabilistic entity extraction from deterministic statute whitelists (*Section 73 Indian Contract Act, Model Tenancy Act, Order 37 CPC*).
* ⚖️ **Mandatory Legal Escalation:** Immediately halts civil automation and refers to **NALSA (15100)** or **Women's Helpline (1091)** upon detecting criminal violence, dowry, or matrimonial disputes.
* 📄 **Actionable Paperwork:** Once all variables are verified, generates and downloads a formal **Legal Notice of Demand** in Markdown and court-ready PDF format.

---

## 📂 Project Structure

```
├── app.py                      # Root launcher for the Streamlit dashboard
├── backend/
│   └── app/
│       ├── main.py             # FastAPI app (/chat, /audio-chat, /notice/{id}/pdf)
│       ├── database.py         # SQLite manager (ai_lawyer.db: chat_history & case_state)
│       ├── config.py           # Configuration & USE_MOCK_SARVAM toggle
│       ├── models.py           # Pydantic schemas
│       ├── kb/                 # Grounding Knowledge Bases (Rental & Salary)
│       └── services/           # Triage, Extractor, Voice (STT/TTS), and PDF services
├── frontend/
│   └── app.py                  # Streamlit dashboard implementing Option A UX
├── test_cases/
│   └── test_cases.json         # 8 intentional messy conversational test scripts
├── raw_outputs/                # Unedited evaluation logs and generated notices
├── generate_raw_outputs.py     # Script to generate raw outputs for submission
├── run_test_suite.py           # Automated evaluation runner
├── compile_solution_pdf.py     # Compiles SOLUTION_DOC.md to 2-page PDF
├── SOLUTION_DOC.md             # The 2-page submission solution writeup
├── SOLUTION_DOC.pdf            # Exact 2-page submission PDF
└── ai_lawyer.db                # Local SQLite persistence database
```

---

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git
cd KUKU-FM_IIT-BHU-_Advait_Pathak
pip install -r requirements.txt  # Or pip install fastapi uvicorn streamlit sarvamai fpdf2 python-dotenv
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```ini
SARVAM_API_KEY=your_sarvam_api_key_here
USE_MOCK_SARVAM=False   # Set True to bypass external network calls and save credits
```

### 3. Run the Backend API
```bash
uvicorn backend.app.main:app --reload --port 8000
```
* Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
* Health Check: `http://127.0.0.1:8000/health`

### 4. Run the Streamlit Frontend
In a separate terminal:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Running the Test Suite & Generating Raw Outputs

To execute the test suite across all 8 intentional messy test scenarios and regenerate the `/raw_outputs` folder:
```bash
python generate_raw_outputs.py
```
View the live evaluation log in [`raw_outputs/EVALUATION_SUMMARY.md`](raw_outputs/EVALUATION_SUMMARY.md).
