# ⚖️ NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat

> **Kuku FM Take-Home Assignment | AI Generalist Role**  
> **Candidate:** Advait Pathak (IIT BHU)  
> **Problem Chosen:** Problem 2 — Build an AI Lawyer  
> **Live Prototype:** [https://kuku-fm-iit-bhu-advait-pathak.streamlit.app](https://kuku-fm-iit-bhu-advait-pathak.streamlit.app)  
> **GitHub Repository:** [https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak](https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak)  
> **Solution Document (2-Page PDF):** [SOLUTION_DOC.pdf](SOLUTION_DOC.pdf)  
> **Raw Evaluation Outputs:** [raw_outputs/](raw_outputs/)

[![Live Prototype](https://img.shields.io/badge/Live%20Prototype-Streamlit%20Cloud-FF4B4B.svg?style=for-the-badge&logo=streamlit)](https://kuku-fm-iit-bhu-advait-pathak.streamlit.app)
[![Solution Document](https://img.shields.io/badge/Solution%20Doc-2--Page%20PDF-B83A2A.svg?style=for-the-badge&logo=adobeacrobatreader)](SOLUTION_DOC.pdf)
[![GitHub Repo](https://img.shields.io/badge/Source%20Code-GitHub-181717.svg?style=for-the-badge&logo=github)](https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Sarvam AI](https://img.shields.io/badge/AI%20Suite-Sarvam%20AI-6366F1.svg)](https://www.sarvam.ai/)
[![Guardrails](https://img.shields.io/badge/Guardrails-Statute%20Whitelisted-success.svg)](#-5-layer-neuro-symbolic-architecture)

---

## 📋 Quick Links for Evaluators & Reviewers

| Deliverable | Description | Link |
| :--- | :--- | :--- |
| **🚀 Live Prototype** | Fully deployed on Streamlit Community Cloud. In-process backend, live browser microphone recording, Sarvam STT/TTS, AST claim math, live IndianKanoon precedent search, and PDF generation. | [**Open Live App**](https://kuku-fm-iit-bhu-advait-pathak.streamlit.app) |
| **📄 Solution Document** | Exact 2-page executive solution document with high-density system architecture flow diagram, unit economics, evaluation matrix, and failure analyses. | [**View SOLUTION_DOC.pdf**](SOLUTION_DOC.pdf) |
| **📂 Raw Outputs Folder** | Unedited raw JSON conversation traces, extracted fact states, and drafted legal notices across all 11 test scenarios. | [**Browse raw_outputs/**](raw_outputs/) |
| **🎥 Video Demo Script** | Step-by-step presentation script in spoken Roman Hindi used for the 5-minute showcase video. | [**View DEMO_VIDEO_SCRIPT.pdf**](DEMO_VIDEO_SCRIPT.pdf) |

---

## 🎯 Problem Framing & The "Everyday Bharat" Reality

In India, over **90% of ordinary citizens** never approach a lawyer for everyday civil grievances:
- Landlords arbitrarily withholding ₹20,000 – ₹80,000 rental deposits.
- Startups withholding 2–3 months of fixed salary under threats of 2-year service bonds.
- Refusals to replace defective electronics under the Consumer Protection Act.
- Dishonoured cheques for freelance or small business loans.

A formal advocate consultation costs **₹2,500 – ₹5,000** (often 20% to 50% of the disputed sum), legal English jargon is intimidating, and drafting a proper legal notice is out of reach. Regional-language speakers explain their problem in long, emotionally charged voice notes rather than structured forms.

### Why Generalist LLMs Fail (And What NyayaMitra Solves):
1. **Hallucinated Criminal Sections:** General chatbots reach for *IPC 420 (Cheating)* or criminal arrest for simple rent disputes. NyayaMitra enforces a **deterministic statute whitelist** (*Section 73 ICA, Section 108(m) TPA, CPA 2019, Section 138 NI Act*).
2. **Arithmetic Incompetence:** LLMs consistently fail multi-turn wage calculations (e.g., miscalculating ₹18L CTC with ₹12L fixed over 2 unpaid months as ₹95,000 instead of ₹2,00,000). NyayaMitra isolates all math into a **restricted Python AST evaluator (`_safe_eval_math`)**.
3. **Absence of Procedural Grounding:** NyayaMitra applies **7 Bar Council of India (BCI) LL.B. curriculum doctrines**, including Section 63 *Bharatiya Sakshya Adhiniyam, 2023 (BSA)* electronic evidence certificates for WhatsApp and UPI screenshots.
4. **Calibrated Case Precedents:** Evaluates grievance severity (0–1 score). For severe matters ($\ge 0.60$), it launches a **live IndianKanoon.org web search agent** to ground demand notices in Supreme Court authorities.
5. **Zero-Tolerance Safety Escalation:** Criminal violence, domestic abuse, dowry harassment, divorce, and child custody are strictly halted with statutory helplines (**NALSA 15100**, **Women's Helpline 1091**).

---

## 🏗️ 5-Stage Neuro-Symbolic Architecture

NyayaMitra strictly decouples **probabilistic language understanding** from **deterministic legal logic and arithmetic**:

```
                               ┌────────────────────────────────────────────────────────┐
                               │           Citizen (Voice Note or Text in Hindi/Hinglish)│
                               └───────────────────────────┬────────────────────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. MULTIMODAL INTAKE & SESSION STATE STORE                                                                              │
│    • Sarvam Saaras (`saaras:v3`): Indic Speech-to-Text with auto-detected code-mixing (11 languages)                    │
│    • FastAPI + SQLite Persistence: Atomic session state, preserving full transcript history across turns               │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. TRIAGE & MANDATORY SAFETY GUARDRAIL                                                                                  │
│    • Domain Classifier: Routes to Rental Deposit, Unpaid Salary, Consumer Dispute, or Money Recovery (NI Act 138)       │
│    • 🛑 Zero-Tolerance Guardrail: If Criminal / Domestic Violence / Dowry / Custody detected:                           │
│      └─► Halts automated drafting immediately ──► Serves NALSA (15100), Women's Helpline (1091), or 112               │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. NEURO-SYMBOLIC REASONING CORE                                                                                        │
│    • Conversational Extraction: `sarvam-105b-conversations` extracts structured case variables                          │
│    • Deterministic AST Calculator (`_safe_eval_math`): Evaluates arithmetic formulas e.g. `1200000 / 12 * 2`            │
│    • 7 LL.B. Doctrinal Engines: ICA (Sec 10/27/70/73/74), TPA 108(m), ID Act 2(s)/33C(2), CPA 2019, NI 138, CPC, BSA  │
│    • Completeness Gate: If facts missing, asks ≤ 2 targeted follow-ups (zero repetitive sympathy scripts)               │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. CALIBRATED SEVERITY GATE & LIVE RAG PRECEDENT AGENT                                                                  │
│    • Severity Gate (0–1): Evaluates claim quantum, coercion (bonds, withheld relieving letters), and legal friction     │
│    • If Score ≥ 0.60 (Severe): Live IndianKanoon.org web search (`doctypes:judgments`) + 5 SC Landmark Anchors         │
│    • If Score < 0.60 (Routine): Direct fast-path (< 2 seconds) bypassing external web overhead                          │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. ACTIONABLE PAPERWORK & ADVERSARIAL PRACTICE DOJO                                                                     │
│    • Bespoke Legal Notice of Demand: Slot-filled statutory template + judicial precedents (PDF & Markdown)              │
│    • Spoken Advisory: Sarvam Bulbul (`bulbul:v3`) regional Indic voice guidance                                        │
│    • Voice Role-Play Dojo: Simulates stubborn landlord or HR manager; new facts revealed dynamically sync back to state │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ The 7 BCI LL.B. Syllabus Doctrines Embedded in Code

| Subject Pillar | Statutes & Sections | Practical Legal Purpose in NyayaMitra |
| :--- | :--- | :--- |
| **Law of Contract** | ICA 1872: Sec 10, 27, 70, 73, 74 | Voids illegal employment bonds/non-competes (Sec 27); quantifies actual damages vs. penal forfeitures (*Fateh Chand* & *Kailash Nath*). |
| **Property & Tenancy Law** | TPA 1882: Sec 108(m); Model Tenancy | Rebuts arbitrary painting/deep-cleaning deductions under "reasonable wear and tear"; accommodates unwritten leases without deadlock. |
| **Labour & Industrial Law** | ID Act 1947: Sec 2(s), 33C(2); Wages Act | Distinguishes individual workmen from managerial staff; cites *Central Inland Water Transport* against unconscionable termination clauses. |
| **Consumer Protection** | CPA 2019: Sec 2(7), 2(10), 34(2)(d) | Identifies product defects and unfair trade practices; invokes e-Daakhil filing from the consumer's home city (*Pioneer Urban*). |
| **Negotiable Instruments** | NI Act 1881: Sec 138, 139, 143A | Issues statutory 15-day notice of demand post-cheque bounce; establishes statutory presumption of debt (*Rangappa v. Sri Mohan*). |
| **Civil Procedure & Limitation** | CPC 1908: Order 37; Limitation Act 1963 | Warns respondents of summary suit procedures with 3-year commercial debt limitation periods. |
| **Law of Evidence** | Bharatiya Sakshya Adhiniyam, 2023: Sec 63 | Formulates Section 63 electronic evidence conditions for admitting WhatsApp chats, UPI screenshots, and call logs into evidence. |

---

## 🧪 Comprehensive Evaluation Suite (11 Test Cases)

NyayaMitra was tested on **11 multi-turn, noisy, vernacular test scenarios** covering every civil recovery domain and safety edge cases. All unedited raw JSON state snapshots, multi-turn dialogue histories, and generated Legal Notices are committed in [`raw_outputs/`](raw_outputs/):

| Test ID | Scenario Description | Detected Domain | Complete? | Severity | Precedents Retrieved | Notice Generated |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `TC_01` | Rental Deposit — Vague Hindi Story | `rental_deposit` | ❌ *(Needs facts)* | 0.40 | Fast-Path | Follow-up Turn |
| `TC_02` | Rental Deposit — Dense Hinglish (Bangalore 2BHK) | `rental_deposit` | ✅ | 0.50 | Fast-Path | 📄 Yes |
| `TC_03` | Rental Deposit — Bogus Damage Deduction (Pune) | `rental_deposit` | ✅ | 0.50 | Fast-Path | 📄 Yes |
| `TC_04` | Rental Deposit — Oral Agreement & Cash (Deadlock Test) | `rental_deposit` | ✅ | 0.55 | Fast-Path | 📄 Yes (Evidentiary Warning) |
| `TC_05` | Unpaid Salary — Emotional Rant & IPC 420 Myth (Noida) | `unpaid_salary` | ✅ | 0.65 | Live IndianKanoon | 📄 Yes |
| `TC_06` | Unpaid Salary — Resigned Full & Final Delay (Gurugram) | `unpaid_salary` | ✅ | 0.70 | Live IndianKanoon | 📄 Yes |
| `TC_07` | Unpaid Salary — Incomplete Employer Details | `unpaid_salary` | ❌ *(Needs facts)* | 0.40 | Fast-Path | Follow-up Turn |
| `TC_08` | Domestic Violence & Dowry Harassment (Safety Guardrail) | `out_of_scope` | ❌ *(Halted)* | N/A | None | 🚨 **HALTED: NALSA 15100** |
| `TC_09` | Unpaid Salary — CTC Math (`₹18L CTC, ₹12L fixed`) & Bond | `unpaid_salary` | ✅ | **0.85** | *Central Inland Water Transport* | 📄 **Yes (`₹2,00,000` exact)** |
| `TC_10` | Consumer Dispute — Defective EV Battery & Warranty Refusal | `consumer_dispute` | ✅ | 0.50 | *Pioneer Urban* | 📄 Yes (e-Daakhil) |
| `TC_11` | Money Recovery — Bounced Loan Cheque (`NI Act Sec 138`) | `money_recovery` | ✅ | **0.85** | *Rangappa v. Sri Mohan* | 📄 Yes (15-Day Demand) |

To run the automated test suite locally:
```bash
python generate_raw_outputs.py
```

---

## 💰 Unit Economics & Real-World Production Scale

| Pipeline Step | Provider & Model | Average Workload | Cost (INR) |
| :--- | :--- | :--- | :--- |
| **Voice Transcription** | Sarvam Saaras (`saaras:v3`) | ~20 seconds of audio intake | ₹0.15 |
| **Reasoning, Extraction, & Drafting** | `sarvam-105b-conversations` | ~1,800 tokens across turns | ₹0.25 |
| **Precedent Web Search** | IndianKanoon HTTP + Python AST | Only when severity score $\ge 0.60$ | ₹0.00 |
| **Spoken Advisory** | Sarvam Bulbul (`bulbul:v3`) | ~15 seconds synthesized audio | ₹0.15 |
| **Legal Notice PDF Generation** | Python FPDF2 Core (Vector) | Local CPU rendering | ₹0.00 |
| **Total Cost per Case** | **End-to-End Civil Consultation** | **Full Audio Intake + Notice PDF** | **~₹0.55** |

> **Economic Verdict:** At **₹0.55 per grievance**, NyayaMitra is **99.98% cheaper** than a traditional advocate consultation (₹2,500 – ₹5,000), making access to justice accessible to any smartphone user in India.

### Monthly Run-Rate for 100,000 Grievances
- **Compute:** Containerized FastAPI on AWS ECS / GCP Cloud Run: ~$80/month
- **Database:** Managed Postgres on Supabase / Neon: ~$50/month
- **Sarvam AI API Volume:** 100,000 cases × ₹0.55 = ₹55,000 (~$660/month)
- **Total Run-Rate:** **~$790 / month (~₹66,000)** to serve 100,000 citizens.

---

## 💻 Optional: Running Locally / Self-Hosting

The live prototype is already hosted on [Streamlit Community Cloud](https://kuku-fm-iit-bhu-advait-pathak.streamlit.app). To run the project locally on your machine:

### 1. Clone & Install
```bash
git clone https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git
cd KUKU-FM_IIT-BHU-_Advait_Pathak
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```ini
SARVAM_API_KEY=your_sarvam_api_key_here
LLM_PROVIDER=sarvam
LLM_MODEL=sarvam-105b-conversations
USE_MOCK_SARVAM=False   # Set True to run offline without consuming API credits
```

### 3. Launch App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser. (Root `app.py` automatically initializes SQLite and runs the state machine in-process if a separate backend is not running).

*(Optional Microservice Mode)* Run FastAPI backend on port 8000:
```bash
uvicorn backend.app.main:app --port 8000
```
FastAPI interactive Swagger docs: `http://localhost:8000/docs`

---

## 📂 Repository Structure

```
├── app.py                      # Root Streamlit app (with in-process cloud fallback)
├── .streamlit/
│   ├── config.toml             # Headless server & typography configurations
│   └── secrets.toml.example    # Cloud secrets template reference
├── backend/
│   └── app/
│       ├── main.py             # FastAPI routes (/chat, /audio-chat, /notice/{id}/pdf)
│       ├── database.py         # SQLite persistence (chat_history & case_state)
│       ├── config.py           # Config with automatic st.secrets cloud fallback
│       ├── models.py           # Pydantic schemas
│       ├── kb/                 # 4 Civil Domains & BCI LL.B. Doctrinal Reasoning
│       └── services/           # Extractor, AST Math, IndianKanoon Precedent Agent, Voice & PDF
├── test_cases/
│   └── test_cases.json         # 11 comprehensive conversational test scenarios
├── raw_outputs/                # Unedited evaluation JSON traces & drafted notices
├── SOLUTION_DOC.md             # Solution document markdown
├── SOLUTION_DOC.pdf            # Compiled 2-page submission PDF with architecture diagram
├── DEMO_VIDEO_SCRIPT.pdf       # Roman-Hindi script used for video presentation
└── requirements.txt            # Minimal production dependencies
```

---

*Authored by **Advait Pathak** (IIT BHU) for the Kuku FM AI Generalist Take-Home Assignment.*
