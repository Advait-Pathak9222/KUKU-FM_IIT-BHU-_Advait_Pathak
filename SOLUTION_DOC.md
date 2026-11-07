# NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat
**Candidate Name:** Advait Pathak | **Target Role:** AI Generalist | **Problem Chosen:** Problem 2 (AI Lawyer)  
**Live Prototype:** Streamlit + FastAPI (Cloud & Local Ready) | **Repository:** `https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git`

---

## 1. Problem Choice, Framing & Architectural Scope

### Why Problem 2?
Most citizens in India never access the formal legal system for everyday civil grievances—such as withheld tenancy security deposits or unpaid startup wages. To an ordinary person in tier-2 or tier-3 India, an advocate feels financially prohibitive (₹2,500–₹5,000 per consultation), terminology is intimidating, and drafting formal notices is overwhelming. 

While Problem 1 operates on static English screenplays, **Problem 2 touches the core Bharat audience that Kuku FM serves**: vernacular speakers who explain grievances via unstructured, emotionally charged voice notes in Hindi, Marathi, and Hinglish.

### End-to-End "Triage + Deep Dive + Roleplay" Architecture (Covering All 4 Brief Directions)
Rather than building a superficial generalist chatbot claiming to know all 1,200+ Indian acts, we built a scoped system covering all four problem directions:
1. **Intelligent Triage & Continuous Safety Guardrail:** Routes messy complaints into scoped civil categories (`rental_deposit`, `unpaid_salary`) or immediately halts on `out_of_scope` criminal/violence issues on any turn (Roman or Devanagari script).
2. **Build the Case (Entity Extraction Machine):** Converts emotional rambling into an objective 8-field timeline: Counterparty, Location, Amounts, Dates, Deductions, and Available Proof.
3. **Explain Standing & Prepare Paperwork:** Explains legal rights in plain regional language and synthesizes verified facts into a court-ready **Legal Notice of Demand** (Markdown & PDF) with a 15-day statutory cure period.
4. **Help Them Argue (Counterparty Negotiation Simulator):** An interactive roleplay coach that plays the stubborn Landlord or defensive HR Manager making realistic excuses, paired with live tactical coaching citing exact civil statutes.

---

## 2. Preventing Legal Hallucination: The Grounded State Machine

A fatal failure mode of consumer LLMs is confident hallucination—inventing fake sections of the Bharatiya Nyaya Sanhita (BNS) or invoking criminal IPC 420 for simple rent disputes. NyayaMitra enforces a **Zero-Hallucination Architecture** through strict separation between probabilistic reasoning and deterministic code:

1. **What We Gave to AI:** Natural language entity extraction, conversational empathy, emotional noise filtering, negotiation roleplay, and multilingual code-mixed dialogue (`sarvam-105b-conversations`, hot-swappable via `call_llm` router with OpenAI, Gemini, or Claude).
2. **What We Kept as Deterministic Code:**
   * **SQLite Fact State Loop:** Extracted entities are persisted in SQLite (`ai_lawyer.db`). Completeness is computed deterministically (`len(missing_variables) == 0`), preventing premature drafting.
   * **The Missing-Proof Deadlock Breaker:** When users lack written agreements, the engine marks evidence as `oral_agreement_only`, issues an explicit **Evidentiary Risk Advisory** (advising secondary proof like utility bills or witnesses), and proceeds without deadlocking.
   * **Strict Statute Whitelisting:** The LLM is **never** permitted to generate freeform legal citations. Legal notices are assembled via deterministic templates bound to vetted statutes: *Section 73 of the Indian Contract Act, 1872*, *Model Tenancy Act, 2021*, *Payment of Wages Act*, and *Order 37 of the CPC (Summary Suit)*.
   * **The Escalation Boundary (When a Real Lawyer is Mandatory):** If criminal assault, domestic violence, dowry, divorce, or child custody triggers are detected at any point, the system immediately halts civil drafting and serves 24x7 statutory helplines: **NALSA (15100)** and **Women's Helpline (1091)**.

---

## 3. Sarvam Voice Engine, Unit Economics & Real-World Scale

### Multimodal Indic Voice & Latency Masking
* **Ingestion (Sarvam Saaras `saaras:v3` STT):** Transcribes raw voice notes with automated dialect identification (`hi-IN`, `mr-IN`, etc.).
* **Reasoning & Code-Mixing:** Responds in the user's regional language blended naturally with conversational English loanwords (*deposit, landlord, salary, notice*).
* **Audio Synthesis (Sarvam Bulbul `bulbul:v3` TTS):** Generates natural spoken advisory with MD5 audio buffer hashing to prevent widget replay loops.

### Real-World Unit Economics (50 Paise per Case)

| Pipeline Step | Provider / Model | Computation | Cost (INR) |
| :--- | :--- | :--- | :--- |
| **Voice Ingestion** | Sarvam Saaras (`saaras:v3`) | ~20 seconds audio transcription | ₹0.15 |
| **Triage & Extraction** | Sarvam-105B-Conversations | ~1,200 tokens across 2 dialogue turns | ₹0.20 |
| **Spoken Advisory** | Sarvam Bulbul (`bulbul:v3`) | ~15 seconds synthesized audio | ₹0.15 |
| **Notice Generation & PDF** | Python Core (Deterministic) | Slot-filling + FPDF2 rendering | ₹0.00 |
| **Total Cost per Case** | **End-to-End Civil Pipeline** | **Verified Notice + Audio Consultation** | **~₹0.50 (50 paise)** |

*Economic Impact & 100k Scale:* Delivers a **99.98% cost reduction** vs. ₹2,500+ advocate consultations. At **100,000 monthly grievances**, horizontal FastAPI containers + managed Postgres + Redis caching + Sarvam APIs cost **~$730/month (~₹61,000)** total.

---

## 4. Quality Checking, Real Evaluation Runs, AI Tool Audit & Honest Failure Modes

We evaluated NyayaMitra across **8 intentional, unedited test cases** (available in `/raw_outputs`):

| Test Case | Scenario Description | Expected Triage | Result | Handled Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **TC_01** | Vague Hindi rental complaint | `rental_deposit` | **PASSED** | Acknowledged empathetically; queried top 2 missing facts. |
| **TC_02** | Bangalore 2BHK Hinglish story | `rental_deposit` | **PASSED** | Extracted 7 facts; prompted for tenant name, drafted notice. |
| **TC_03** | Pune tile damage dispute | `rental_deposit` | **PASSED** | Single-turn completion; generated formal demand notice. |
| **TC_04** | Delhi oral tenancy cash payment | `rental_deposit` | **PASSED** | Broke missing-proof deadlock; issued oral evidence warning + notice. |
| **TC_05** | Noida startup unpaid salary rant | `unpaid_salary` | **PASSED** | Filtered emotional rant; dispelled IPC 420 arrest misconception. |
| **TC_06** | Gurugram 90-day FnF delay | `unpaid_salary` | **PASSED** | Single-turn corporate demand letter under Contract Act Sec 73. |
| **TC_07** | Partial wage facts missing company | `unpaid_salary` | **PASSED** | Targeted follow-up for registered corporate entity name. |
| **TC_08** | Domestic violence & dowry | `out_of_scope` | **PASSED** | **Strict Refusal:** Halted drafting; served NALSA 15100 helpline. |

### AI Tools Used & Where AI Got It Wrong During Development
* **Tools Used:** Cursor / Gemini coding assistants for boilerplate scaffolding, Sarvam AI (`saaras:v3`, `bulbul:v3`, `sarvam-105b-conversations`) for runtime Indic perception and reasoning.
* **Where AI Got It Wrong:** (1) Coding assistants hallucinated OpenAI's `client.chat.completions.create()` syntax and deprecated `bulbul:v2` for Sarvam's SDK, causing runtime crashes until we inspected the live `sarvamai` package signatures. (2) AI-generated Streamlit audio code caused an infinite 6x voice reply loop on `st.rerun()` because `st.audio_input` retains its byte buffer across reruns—which we solved by engineering deterministic MD5 audio buffer de-duplication.

### Honest Failure Modes (Where Our Prototype Struggles)
1. **Ambiguous Relative Dates:** Phrases like *"Diwali ke aas-paas khali kiya"* are extracted verbatim rather than normalized to `ISO-8601` calendar dates.
2. **Phonetic Brand Names in Noisy Audio:** In heavy traffic noise, Saaras STT occasionally transcribes English startup names phonetically into Devanagari, requiring text confirmation before final PDF generation.
3. **Multi-Part Counterclaims:** If a landlord deducts both legitimate unpaid electricity bills and bogus painting charges, the template currently demands the aggregate withheld sum rather than netting out undisputed utility bills automatically.
