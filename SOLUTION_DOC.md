# NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat
**Candidate Name:** Advait Pathak | **Target Role:** AI Generalist | **Problem Chosen:** Problem 2 (AI Lawyer)  
**Live Prototype:** Streamlit + FastAPI Local / Cloud Ready | **Repository:** `https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git`

---

## 1. Problem Choice, Framing & Architectural Scope

### Why Problem 2?
Most citizens in India never access the formal legal system for everyday civil grievances—such as withheld tenancy security deposits, unpaid startup wages, or unreturned refunds. To an ordinary person in tier-2 or tier-3 India, an advocate feels financially prohibitive (₹2,500–₹5,000 per consultation), terminology is intimidating, and drafting formal notices is overwhelming. 

While Problem 1 operates on static English screenplays, **Problem 2 touches the core Bharat audience that Kuku FM serves**: vernacular speakers who explain grievances via unstructured, emotionally charged voice notes in Hindi, Hinglish, Marathi, etc.

### The "Triage + Deep Dive" Architecture
Rather than attempting a superficial generalist model that claims to understand all 1,200+ Indian central and state acts, we engineered a **Triage + Deep Dive system**:
1. **Intelligent Triage Layer:** Routes incoming messy complaints into scoped civil categories (`rental_deposit`, `unpaid_salary`) or immediately flags `out_of_scope` sensitive situations.
2. **Deep-Dive Entity Extraction Machine:** Converts emotional rambling into an objective 5-part timeline: Counterparty, Transaction Value, Incident Dates, Deductions/Claims, and Available Evidence.
3. **Formal Notice Assembler:** Synthesizes verified facts into a court-ready **Legal Notice of Demand** with a 15-day statutory cure period.

---

## 2. Preventing Legal Hallucination: The Grounded State Machine

A fatal failure mode of consumer LLMs is confident hallucination—inventing fake sections of the Bharatiya Nyaya Sanhita (BNS), inapplicable IPC provisions (such as invoking IPC 420 for simple rent disputes), or non-existent High Court precedents. NyayaMitra enforces a **Zero-Hallucination Architecture** through strict boundaries between probabilistic reasoning and deterministic code:

1. **What We Gave to AI:** Natural language entity extraction, conversational empathy, emotional noise filtering, and multilingual dialect understanding.
2. **What We Kept as Code:**
   * **The SQLite Fact State Loop:** Extracted entities are persisted in SQLite (`ai_lawyer.db`). State completeness is computed deterministically (`len(missing_variables) == 0`), preventing premature generation.
   * **The Missing-Proof Deadlock Breaker:** When users lack written agreements, the engine marks evidence as `oral_agreement_only`. It explicitly warns them of evidentiary challenges but does not deadlock the drafting pipeline.
   * **Strict Statute Whitelisting:** The LLM is **never** permitted to generate freeform legal citations. Legal notices are generated via deterministic templates bound to vetted statutes: *Section 73 of the Indian Contract Act, 1872*, *Principles of the Model Tenancy Act, 2021*, and *Order 37 of the CPC (Summary Suit for Debt Recovery)*.
   * **The Escalation Boundary (When a Real Lawyer is Mandatory):** If criminal assault, domestic violence, dowry, or child custody keywords are detected, the system immediately halts civil automation and serves 24x7 statutory helpline numbers: **NALSA (15100)** and **Women's Helpline (1091)**.

---

## 3. Sarvam Voice Engine, Unit Economics & Real-World Scale

### Multimodal Indic Voice & Option A UX
To ensure genuine accessibility, we integrated the Sarvam AI suite:
* **Ingestion (Sarvam Saaras STT):** Ingests raw voice recordings (WAV/MP3/WebM) and performs Indic speech-to-text with automated dialect identification (`hi-IN`, `mr-IN`, Hinglish, etc.).
* **Reasoning (Sarvam-105B-Conversations):** Culturally grounded Indic reasoning supporting natural **Indic + English code-mixing** (*"deposit"*, *"landlord"*, *"salary"*).
* **Audio Playback (Sarvam Bulbul TTS):** Generates spoken responses in natural Indic voices.
* **Latency Masking (Option A UX):** User transcription renders immediately with an animated waveform, masking the ~3.5s roundtrip until the base64 audio arrives.

### Real-World Unit Economics (Cost per Case)
Kuku FM evaluates *"what it costs at real-world volume"*. Below is the exact production unit economics per citizen served:

| Pipeline Step | Provider / Model | Computation | Cost (INR) |
| :--- | :--- | :--- | :--- |
| **Voice Ingestion** | Sarvam Saaras STT | ~20 seconds audio transcription | ₹0.15 |
| **Triage & Extraction** | Sarvam-105B-Conversations | ~1,200 tokens across 2 dialogue turns | ₹0.20 |
| **Spoken Advisory** | Sarvam Bulbul TTS | ~15 seconds synthesized audio | ₹0.15 |
| **Notice Generation & PDF** | Python Core (Deterministic) | Slot-filling + FPDF2 rendering | ₹0.00 |
| **Total Cost per Case** | **End-to-End Civil Pipeline** | **Verified Notice + Audio Consultation** | **~₹0.50 (50 paise)** |

*Impact:* Compared to a standard legal consultation (₹2,500–₹5,000), NyayaMitra delivers a **99.98% cost reduction**, making legal action accessible to any smartphone user in India.

### Scalability to 100k Monthly Grievances
* **Stateless Compute:** FastAPI services horizontally autoscaled on containers (ECS / Cloud Run) behind an ALB.
* **Database Transition:** The embedded SQLite engine transitions to PostgreSQL with connection pooling (PgBouncer) for multi-tenant production concurrency.
* **Safety Ceilings:** Strict 4-turn clarification caps prevent runaway inference costs on uncooperative users.
* **Total Infrastructure Cost at 100,000 cases/month:** ~$730/month (Compute $80 + Database $50 + Sarvam API $600).

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
1. **Ambiguous Relative Dates:** When a user states *"Diwali ke aas-paas khali kiya tha"*, the extractor captures the phrase verbatim instead of converting to a calendar date (`2024-11-01`), requiring a second clarification turn.
2. **Audio Background Noise in Vernacular Accents:** In noisy environments with mixed English-Hindi jargon, Saaras STT occasionally transcribes company names phonetically (*"TechNova"* as *"Tek Nova"*), requiring user confirmation before notice generation.
3. **Complex Multi-Claim Counterparty Deductions:** If a landlord claims both utility arrears (legitimate) and painting charges (arbitrary), the engine currently treats the entire withheld sum under one demand rather than partitioning undisputed vs. disputed amounts.

---
*Submitted for Kuku FM AI Generalist Take-Home Evaluation.*
