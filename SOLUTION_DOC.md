# NyayaMitra (न्यायमित्र) — Conversational AI Lawyer for Everyday Bharat
**Candidate Name:** Advait Pathak | **Target Role:** AI Generalist | **Problem Chosen:** Problem 2 (AI Lawyer)  
**Live Prototype:** Streamlit + FastAPI (Cloud & Local Ready) | **Repository:** `https://github.com/Advait-Pathak9222/KUKU-FM_IIT-BHU-_Advait_Pathak.git`

---

## 1. Problem Choice, Framing & Architectural Scope

### Why Problem 2?
Most citizens in India never access the formal legal system for everyday civil grievances—such as withheld tenancy security deposits, unpaid startup salaries/CTC disputes, defective consumer goods, or bounced freelance cheques. To an ordinary citizen in Bharat, an advocate feels financially prohibitive (₹2,500–₹5,000 per consultation), legal terminology is intimidating, and drafting formal pre-litigation notices is overwhelming. 

While Problem 1 operates on static English screenplays, **Problem 2 touches the core Bharat audience that Kuku FM serves**: vernacular speakers who explain grievances via unstructured, emotionally charged voice notes in Hindi, Marathi, and Hinglish.

### End-to-End 5-Layer Legal Architecture (Covering All Problem Directions)
Rather than building a rigid form-filler or an ungrounded chatbot, we engineered a **Neuro-Symbolic + BCI LL.B. Doctrinal Architecture**:
1. **4-Domain Triage & Safety Escalation Guardrail:** Routes messy complaints into 4 scoped civil recovery domains (`rental_deposit`, `unpaid_salary`, `consumer_dispute`, `money_recovery`) or immediately halts on `out_of_scope` criminal/domestic-violence issues on any turn (serving NALSA 15100 / 1091 / 112).
2. **Neuro-Symbolic Financial & Pro-Rata AST Calculator:** Converts natural-language financial narratives (e.g., `₹18L CTC = ₹12L Fixed + ₹6L unvested ESOPs`, pro-rata unpaid months, or multiple freelance invoices minus partial UPI payments) into symbolic arithmetic expressions evaluated deterministically via Python's AST engine (`_safe_eval_math`).
3. **BCI LL.B. Curriculum Doctrinal & Procedural Engine:** Evaluates every case across 7 core Bar Council of India LL.B. subjects—Contract Law (Sec 10, 27, 70, 73, 74 ICA), Tenancy Law (Sec 108(m) TPA wear & tear exception), Labour Law (Sec 2(s) & 33C(2) ID Act workman vs. managerial forum), Consumer Protection (Sec 2(7) livelihood & Sec 34(2)(d) home-city e-Daakhil jurisdiction), NI Act Sec 138/139, CPC Order 37 & Limitation Act, and **Section 63 Bharatiya Sakshya Adhiniyam (BSA), 2023** for electronic evidence (WhatsApp/UPI).
4. **Calibrated Severity Gate (`≥ 0.60`) & Live IndianKanoon.org Precedent Web Agent:** Scores case severity (`0.00–1.00`) based on monetary quantum, coercive conduct (withheld relieving letter, employment bond, unregistered lease defense, cheque bounce), and doctrinal complexity. Simple turns (`< 0.60`) skip web search for speed; severe cases (`≥ 0.60`) browse **IndianKanoon.org** (`doctypes:judgments`) live and pair results with Landmark Supreme Court precedents.
5. **Bespoke DPC Legal Notice Draftsman + Voice Roleplay Simulator:** Synthesizes verified facts, exact math breakdowns, and retrieved precedents into a custom **Formal Legal Notice of Demand (PDF & Markdown)**, paired with a **Voice + Text Counterparty Roleplay Coach** (`🥊 Practice Arguing`) that captures facts live while arguing.

---

## 2. Preventing Legal Hallucination: Neuro-Symbolic & Closed-World Grounding

A fatal failure mode of consumer LLMs is confident hallucination—inventing fake sections, miscalculating multi-step salary/deposit math, or invoking criminal IPC 420 for civil recovery. NyayaMitra enforces a **Zero-Hallucination Architecture**:

1. **What We Gave to AI:** Multi-turn context synthesis, symbolic equation formulation (`claim_math_expression`), case-specific nuance capture (`_case_nuances`), LL.B. doctrinal diagnostic, non-repetitive multilingual lawyer dialogue, and counterparty negotiation roleplay (`sarvam-105b-conversations`, hot-swappable via `call_llm` with OpenAI, Gemini, or Claude).
2. **What We Kept as Deterministic / Closed-World Code:**
   * **Deterministic AST Math Execution:** The LLM writes the formula (`1200000 / 12 * 2` or `3 * 45000 - 35000`), and Python AST computes the exact rupee figure (`₹2,00,000` / `₹1,00,000`).
   * **Closed-World Statutory & Precedent Whitelisting:** The Bespoke DPC Legal Notice Draftsman is strictly restricted to the domain's verified statute whitelist (*Indian Contract Act Sec 27/70/73/74, Transfer of Property Act Sec 108(m), Payment of Wages Act, ID Act Sec 33C(2), Consumer Protection Act 2019 Sec 2/34/35, NI Act Sec 138/139, Order 37 CPC, Sec 63 BSA 2023*) and verified IndianKanoon/SC precedents (*Fateh Chand, Central Inland Water Transport, Kailash Nath, Rangappa, Pioneer Urban*).
   * **The Escalation Boundary:** Criminal assault, domestic violence, dowry, divorce, or child custody triggers immediately halt civil drafting and route to **NALSA (15100)** and **Women's Helpline (1091)**.

---

## 3. Sarvam Voice Engine, Unit Economics & Real-World Scale

### Multimodal Indic Voice & Latency Masking
* **Ingestion (Sarvam Saaras `saaras:v3` STT):** Transcribes raw voice notes across 11 Indian languages (`hi-IN`, `mr-IN`, `ta-IN`, `te-IN`, etc.).
* **Audio Synthesis (Sarvam Bulbul `bulbul:v3` TTS):** Generates spoken advisory and spoken roleplay pushback with MD5 audio buffer hashing to prevent widget replay loops.

### Real-World Unit Economics (~55 Paise per Case)

| Pipeline Step | Provider / Model | Computation | Cost (INR) |
| :--- | :--- | :--- | :--- |
| **Voice Ingestion** | Sarvam Saaras (`saaras:v3`) | ~20 seconds audio transcription | ₹0.15 |
| **Doctrinal, Math & Draft Engine** | Sarvam-105B-Conversations | ~1,800 tokens across multi-turn intake | ₹0.25 |
| **Live Precedent Search** | IndianKanoon HTTP + AST Math | Triggered only when Severity ≥ 0.60 | ₹0.00 |
| **Spoken Advisory** | Sarvam Bulbul (`bulbul:v3`) | ~15 seconds synthesized audio | ₹0.15 |
| **Total Cost per Case** | **End-to-End Civil Pipeline** | **Verified Notice PDF + Audio Consultation** | **~₹0.55 (55 paise)** |

---

## 4. Quality Checking, Evaluation Runs, AI Tool Audit & Honest Failure Modes

We evaluated NyayaMitra across **10 end-to-end test scenarios** (including 4-turn Hindi CTC/Fixed-pay math, unregistered lease wear-and-tear deduction, freelance cheque bounce, and live IndianKanoon precedent retrieval):

| Test Case | Scenario Description | Domain & Severity | Result | Key Capability Verified |
| :--- | :--- | :--- | :--- | :--- |
| **TC_01–04** | Bangalore/Pune/Delhi deposit & oral lease cases | `rental_deposit` | **PASSED** | Sec 108(m) TPA wear & tear, Sec 63 BSA WhatsApp/UPI proof, `150000 - 65000 = ₹85,000` math. |
| **TC_05–07** | 4-turn Hindi CTC breakdown (`₹18L CTC / ₹12L Fixed`) & bond | `unpaid_salary` (Sev `1.00`) | **PASSED** | Computed `₹12L / 12 × 2 = ₹2,00,000`, excluded unvested ESOPs, cited *Central Inland Water Transport (SC)*. |
| **TC_08** | Freelance 3 projects (`3×45k - 35k UPI`) + Cheque Bounce | `money_recovery` (Sev `0.85`) | **PASSED** | AST math `₹1,00,000`, Sec 138/139 NI Act 30-day memo check, cited *Rangappa v. Sri Mohan (SC)*. |
| **TC_09** | Defective product / unfair "No Refund" clause | `consumer_dispute` | **PASSED** | Sec 2(7) livelihood & Sec 34(2)(d) home-city e-Daakhil jurisdiction, cited *Pioneer Urban (SC)*. |
| **TC_10** | Domestic violence, dowry & child custody | `out_of_scope` | **PASSED** | **Strict Refusal:** Halted civil drafting; served NALSA 15100 & 1091 helplines. |

### AI Tools Used & Honest Failure Modes
* **AI Tools Used & Debugging:** Used coding assistants for scaffolding and Sarvam AI (`saaras:v3`, `bulbul:v3`, `sarvam-105b-conversations`) for runtime reasoning. Early iterations suffered from stateless turn blindness (forgetting Turn 3 CTC numbers on Turn 4), LLM mental subtraction slips (`135k - 35k = 95k`), and repetitive sympathy lines—all of which we solved via full-transcript memory, our Neuro-Symbolic AST Math Evaluator, and strict anti-repetition prompting.
* **Remaining Failure Modes:** (1) Ambiguous relative dates (*"Diwali ke aas-paas"*) are captured verbatim unless clarified. (2) Heavy background traffic noise can cause phonetic transcription drift on unfamiliar English company names.
