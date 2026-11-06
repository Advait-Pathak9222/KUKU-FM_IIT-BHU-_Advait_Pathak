# NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat
**Candidate Name:** Advait Pathak | **Target Role:** AI Generalist | **Problem Chosen:** Problem 2 (AI Lawyer)  
**Live Prototype:** Streamlit + FastAPI Local / Cloud Ready | **Repository:** `https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git`

---

## 1. Problem Choice, Framing & Architectural Scope

### Why Problem 2?
Most citizens in India never access the formal legal system for everyday civil grievances—such as withheld tenancy security deposits, unpaid startup wages, or unreturned e-commerce refunds. To an ordinary person in tier-2 or tier-3 India, an advocate feels financially prohibitive, the terminology is intimidating, and drafting formal notices is overwhelming. 

While Problem 1 operates on static English screenplays, **Problem 2 touches the core Bharat audience that Kuku FM serves**: vernacular speakers who explain grievances via unstructured, emotionally charged voice notes in Hindi or Hinglish.

### The "Triage + Deep Dive" Architecture
Rather than attempting to build a superficial generalist model that claims to understand all 1,200+ Indian central and state acts, we deliberately engineered a **Triage + Deep Dive system**:
1. **Intelligent Triage Layer:** Routes incoming messy complaints into scoped civil categories (`rental_deposit`, `unpaid_salary`) or immediately flags `out_of_scope` sensitive situations.
2. **Deep-Dive Entity Extraction Machine:** Converts emotional rambling into an objective 5-part timeline: Counterparty, Transaction Value, Incident Dates, Deductions/Claims, and Available Evidence.
3. **Formal Notice Assembler:** Synthesizes verified facts into a court-ready **Legal Notice of Demand** with a 15-day statutory cure period.

---

## 2. Preventing Legal Hallucination: The Grounded State Machine

A fatal failure mode of consumer LLMs is confident hallucination—inventing fake sections of the Bharatiya Nyaya Sanhita (BNS), inapplicable IPC provisions (such as invoking IPC 420 for simple rent disputes), or non-existent High Court precedents.

NyayaMitra enforces a **Zero-Hallucination Architecture** through strict boundaries between probabilistic reasoning and deterministic code:

```
                    ┌──────────────────────────────────────────────┐
                    │ Raw Conversational Input (Voice / Hinglish)  │
                    └──────────────────────┬───────────────────────┘
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │ Entity & Timeline Extractor (LLM Perception) │
                    └──────────────────────┬───────────────────────┘
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │ SQLite State Store (Evolving Fact Record)    │
                    └──────────────────────┬───────────────────────┘
                                           ▼
             ┌────────────────────────────────────────────────────────────┐
             │       DETERMINISTIC VERIFICATION & STATUTE WHITELIST       │
             │   - Tenancy: Indian Contract Act Sec 73 + Model Tenancy    │
             │   - Salary: Sec 73 Contract Act + Order 37 CPC (Summary)   │
             │   - Strict Regex Whitelist Filter blocks invented laws     │
             └─────────────────────────────┬──────────────────────────────┘
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │ Deterministic Slot-Filling Template Notice   │
                    └──────────────────────────────────────────────┘
```

1. **What We Gave to AI:** Natural language entity extraction, conversational empathy, emotional noise filtering, and multilingual dialect understanding.
2. **What We Kept as Code:**
   * **The SQLite Fact State Loop:** Extracted entities are persisted in SQLite (`ai_lawyer.db`). State completeness is computed deterministically (`len(missing_variables) == 0`), preventing premature generation.
   * **The Missing-Proof Deadlock Breaker:** When users lack written agreements, the engine marks evidence as `oral_agreement_only`. It explicitly warns them of evidentiary challenges but does not deadlock the drafting pipeline.
   * **Strict Statute Whitelisting:** The LLM is **never** permitted to generate freeform legal citations. Legal notices are generated via deterministic templates bound to vetted statutes: *Section 73 of the Indian Contract Act, 1872*, *Principles of the Model Tenancy Act, 2021*, and *Order 37 of the CPC (Summary Suit for Debt Recovery)*.
   * **The Escalation Boundary (When a Real Lawyer is Mandatory):** If criminal assault, domestic violence, dowry, or child custody keywords are detected, the system immediately halts civil automation and provides 24x7 statutory helpline numbers: **NALSA (15100)** and **Women's Helpline (1091)**.

---

## 3. Sarvam AI Voice Engine & System Scalability

### Multimodal Indic Voice Processing
To ensure genuine accessibility for non-English speakers, we integrated the Sarvam AI suite:
* **Ingestion (Sarvam Saaras STT):** Ingests raw voice recordings (WAV/MP3/WebM) and performs Indic speech-to-text with automated dialect identification (`hi-IN`, Hinglish, etc.).
* **Reasoning (Sarvam-105B-Conversations):** Culturally grounded Indic reasoning that extracts entities and handles Hinglish colloquialisms (*"makaan-maalik"*, *"paint ka katenge"*).
* **Audio Playback (Sarvam Bulbul TTS):** Generates spoken responses in natural Indic voices, allowing semi-literate users to listen to their legal rights without parsing dense legalese.

### Frontend Latency Masking: Option A Strategy
End-to-end multimodal processing requires ~3.5 seconds (STT ~1.0s + Fact Extraction ~1.2s + TTS ~1.3s). To deliver a rock-solid user experience on free-tier hosting (Streamlit Cloud / HF Spaces) without WebSocket complexity:
* **Optimistic Instant Display:** User voice transcription and loading waveform appear immediately.
* **Stateless HTTP Resolution:** Once the payload arrives, standard HTML5 audio auto-plays the base64 WAV stream while the sidebar renders real-time SQLite extracted variables and one-click PDF downloads.
* **Credit Safeguard:** Built-in `USE_MOCK_SARVAM` toggle enables deterministic local offline development to conserve API credits.

---

## 4. Quality Checking, Real Evaluation Runs & Honest Failure Modes

We evaluated NyayaMitra across **8 intentional, unedited test cases** (available in `/raw_outputs`):

| Test Case | Scenario Description | Expected Triage | Result | Handled Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **TC_01** | Vague Hindi rental complaint | `rental_deposit` | **PASSED** | Acknowledged emotionally; queried 2 primary missing facts. |
| **TC_02** | Bangalore 2BHK Hinglish story | `rental_deposit` | **PASSED** | Extracted 7 facts; prompted for tenant name, drafted notice. |
| **TC_03** | Pune tile damage dispute | `rental_deposit` | **PASSED** | Single-turn completion; generated formal demand notice. |
| **TC_04** | Delhi oral tenancy cash payment | `rental_deposit` | **PASSED** | Handled missing-proof deadlock; warned user on oral evidence. |
| **TC_05** | Noida startup unpaid salary rant | `unpaid_salary` | **PASSED** | Filtered emotional noise; dispelled IPC 420 arrest misconception. |
| **TC_06** | Gurugram 90-day FnF delay | `unpaid_salary` | **PASSED** | Complete corporate demand letter under Contract Act Sec 73. |
| **TC_07** | Partial wage facts missing company | `unpaid_salary` | **PASSED** | Targeted follow-up for registered corporate entity name. |
| **TC_08** | Domestic violence & dowry | `out_of_scope` | **PASSED** | **Strict Refusal:** Refused drafting; served NALSA 15100 helpline. |

### Honest Failure Modes (Where the Tool Struggles)
1. **Ambiguous Relative Dates:** When a user states *"Diwali ke aas-paas khali kiya tha"* (vacated around Diwali), the extractor captures the phrase verbatim instead of resolving to a specific calendar date (`2024-11-01`), requiring a second clarification turn.
2. **Audio Background Noise in Vernacular Accents:** When recording in noisy outdoor environments with mixed English-Hindi technical jargon, Saaras STT occasionally transcribes company names phonetically (e.g., *"TechNova"* as *"Tek Nova"*), requiring user confirmation before notice generation.
3. **Complex Multi-Claim Counterparty Deductions:** If a landlord claims both utility bill arrears (legitimate) and painting charges (arbitrary), the engine currently treats the entire withheld sum under one demand rather than partitioning undisputed vs. disputed amounts.

---
*Submitted for Kuku FM AI Generalist Take-Home Evaluation.*
