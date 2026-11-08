import ast
import json
import operator
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from .sarvam_client import call_llm
from ..kb import get_kb, get_doctrinal_context

# In-memory cache for bespoke legal notices keyed by (domain, canonical_facts_json)
_NOTICE_CACHE: Dict[str, str] = {}

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _safe_eval_math(expr: str) -> Optional[int]:
    """Deterministically evaluates arithmetic expressions (e.g., '3 * 45000 - 35000' -> 100000) via Python AST."""
    if not expr or not isinstance(expr, str):
        return None
    cleaned = expr.replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    if not re.match(r"^[\d\s\+\-\*\/\(\)\.]+$", cleaned):
        return None
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported AST node")
    try:
        val = _eval(ast.parse(cleaned, mode="eval"))
        return int(round(float(val)))
    except Exception:
        return None

EXTRACTION_SYSTEM_PROMPT = """You are the Autonomous Neuro-Symbolic Legal & Doctrinal Reasoning Engine for NyayaMitra, trained on the Bar Council of India (BCI) LL.B. curriculum.
Your task is to analyze the full multi-turn conversation transcript and the client's latest message, formulate any required financial or legal arithmetic, apply LL.B. doctrinal & procedural analysis, extract both core slots and case-specific nuances, and determine if we have sufficient facts to draft an enforceable Indian Legal Notice.

Case Domain: {domain_name} ({jurisdiction})
Core Domain Schema:
{schema_description}

BCI LL.B. Doctrinal & Procedural Toolkit for This Case:
{doctrinal_context}

Current Extracted Facts So Far:
{current_facts_json}

Full Multi-Turn Conversation Transcript:
{history_text}

UNIVERSAL LEGAL REASONING & EXTRACTION PRINCIPLES:
1. FULL MULTI-TURN SYNTHESIS & PRAGMATIC INFERENCE:
   - Synthesize details across the entire conversation transcript and the latest message.
   - Infer implicit facts naturally from context, verb tense, and socio-economic persona:
     * If a client says they currently work somewhere (present tense), infer employment status as "Currently Employed"; if they left/resigned/were fired, infer "Resigned" or "Terminated".
     * If a client is a freelancer, gig worker, daily-wage worker, or domestic worker without a corporate title, infer their role/designation from the work they describe.
     * If a client mentions ANY document, digital trail, or payment method at any point (e.g., Offer Letter, salary slip, rent agreement, UPI, bank transfer, invoice, order ID, bounced cheque, WhatsApp chat, email, or oral agreement), immediately map 'proof_status' to the closest value in {allowed_proof_enums} without asking again.
     * If the opposite party gave no reason or simply stopped responding/ghosted, record that as the deduction/default reason rather than leaving it blank.

2. NEURO-SYMBOLIC FINANCIAL & PRO-RATA ARITHMETIC:
   - Whenever a client provides component numbers instead of a single pre-calculated total—such as annual vs. monthly fixed pay, pro-rata days/months, multiple projects/invoices minus partial payments, or total deposit minus partial refund—write the exact arithmetic formula in 'claim_math_expression' (e.g., "1200000 / 12 * 2" or "3 * 45000 - 35000" or "80000 - 45000") and specify which numeric schema key it computes in 'claim_target_field' (e.g., "total_amount_owed", "amount_withheld", "claim_amount", or "principal_amount_owed").
   - Exclude non-accrued or unvested perks (like unvested stocks/ESOPs or conditional future bonuses) when calculating earned monthly wage arrears, and include unlawful arbitrary deductions when calculating refundable security deposits.
   - Explain the legal logic of your calculation in 'lawyer_calculation_note'.

3. BCI LL.B. DOCTRINAL, PROCEDURAL & EVIDENTIARY DIAGNOSTIC ('llb_doctrinal_analysis'):
   - Formulate a concise 2–3 line law-school doctrinal diagnostic covering:
     * Substantive Doctrine (e.g., Sec 73/74 ICA against penalty/forfeiture, Sec 108(m) TPA wear & tear exception, Sec 2(s) & 33C(2) ID Act workman vs. managerial forum, Sec 27 ICA void restraint on withholding relieving letter, Sec 2(7)/2(10)/2(11) CPA 2019, or Sec 138/139 NI Act presumption).
     * Forum, Territorial Jurisdiction & Limitation Act Check (e.g., 3-year civil limitation under Limitation Act 1963 / 2-year CPA limitation under Sec 69 / 30-day NI Act Sec 138 notice window; Sec 20 CPC vs. Sec 34(2)(d) CPA home-city forum).
     * Evidentiary Admissibility Rule (e.g., Section 63 Bharatiya Sakshya Adhiniyam, 2023 certificate for WhatsApp/Email/UPI records, or Section 10 & 70 ICA for oral agreement + bank transfer restitution).

4. CAPTURE CASE-SPECIFIC NUANCES (NO FACT LEFT BEHIND):
   - Capture all extra case-specific details (withheld Relieving Letter, employment bond threats, cheque number & memo date, Order ID, utility cutoff, partial payment dates) in 'case_nuances'.

5. LEGAL SUFFICIENCY EVALUATION (THE 5 PILLARS OF AN INDIAN LEGAL NOTICE):
   - Evaluate whether we have the 5 core pillars needed to issue a valid Legal Notice:
     (1) Claimant/Sender Name, (2) Opposite Party Name & City/Location, (3) Cause of Action & Timeline/Period, (4) Quantified Claim Amount in INR (stated or calculated), and (5) Evidentiary Basis.
   - If all 5 pillars are known from the conversation, fill in any remaining secondary schema fields with sensible context-inferred values so the client is never stuck in a rigid form checklist.

Return your response STRICTLY as valid JSON in this exact format:
{{
  "extracted_facts": {{
    // All schema keys for {domain_name}, with null ONLY for fields that are genuinely still unknown
  }},
  "claim_math_expression": "Pure arithmetic formula string using numbers and + - * / ( ) if calculation was needed, else null",
  "claim_target_field": "Name of the numeric field in extracted_facts that claim_math_expression computes, else null",
  "lawyer_calculation_note": "If you performed or updated any financial calculation or legal deduction analysis, explain the step-by-step logic here; otherwise null",
  "llb_doctrinal_analysis": "Concise LL.B. diagnostic: (1) Substantive Doctrine, (2) Forum, Jurisdiction & Limitation Status, (3) Section 63 BSA / Evidentiary Strategy",
  "case_nuances": "Concise summary of any additional case-specific facts, breakdowns, extra reliefs requested (e.g. Relieving Letter, interest, replacement), or chronological details mentioned by the client"
}}"""


PROOF_HUMAN_READABLE = {
    "agreement_and_receipts": "a written Rent Agreement and payment receipts",
    "online_bank_transfer": "online bank transfer / UPI records",
    "whatsapp_chats": "written WhatsApp communications and acknowledgements",
    "oral_agreement_only": "an oral tenancy agreement and witness testimony",
    "offer_letter_and_slips": "an official Offer Letter and salary slips",
    "bank_statement_and_emails": "bank account statements and official email correspondence",
    "relieving_letter": "an official Relieving Letter and Full & Final settlement communications",
    "informal_or_whatsapp": "WhatsApp messages and informal employment records",
    "tax_invoice_and_receipt": "a formal Tax Invoice and payment receipt",
    "online_order_and_payment_proof": "confirmed online Order ID and digital payment records",
    "emails_or_support_tickets": "customer support tickets and email correspondence",
    "oral_or_cash_receipt": "purchase proof and transaction records",
    "written_contract_or_invoice": "a written agreement and raised invoices",
    "bounced_cheque_and_memo": "the dishonoured cheque and official Bank Return Memo",
    "upi_or_bank_transfer_proof": "verified UPI / NEFT / IMPS bank transfer statements",
    "whatsapp_or_email_admission": "written WhatsApp and email admissions of debt"
}

LANG_NAMES = {
    "hi-IN": "Hindi (Devanagari script, natural conversational style with common English terms)",
    "mr-IN": "Marathi (Devanagari script, natural conversational style)",
    "ta-IN": "Tamil (Tamil script)",
    "te-IN": "Telugu (Telugu script)",
    "kn-IN": "Kannada (Kannada script)",
    "bn-IN": "Bengali (Bengali script)",
    "gu-IN": "Gujarati (Gujarati script)",
    "ml-IN": "Malayalam (Malayalam script)",
    "pa-IN": "Punjabi (Gurmukhi script)",
    "od-IN": "Odia (Odia script)",
    "en-IN": "Indian English"
}


def _format_history(recent_history: Optional[List[Dict[str, Any]]]) -> str:
    if not recent_history:
        return "No prior turns (this is Turn 1)."
    lines = []
    for idx, msg in enumerate(recent_history[-14:], 1):
        role = "Client" if msg.get("role") == "user" else "NyayaMitra (Lawyer)"
        content = msg.get("content", "").strip()
        lines.append(f"[Turn {idx} - {role}]: {content}")
    return "\n".join(lines)


def _public_facts(facts: Dict[str, Any]) -> Dict[str, Any]:
    """Returns user-facing schema facts without internal underscore metadata keys."""
    return {k: v for k, v in facts.items() if not str(k).startswith("_")}


def extract_facts_with_reasoning(
    domain: str,
    new_message: str,
    current_facts: Dict[str, Any],
    recent_history: Optional[List[Dict[str, Any]]] = None
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Multi-turn, context-aware fact extraction + Neuro-Symbolic financial & LL.B. doctrinal reasoning.
    Returns (updated_facts, lawyer_calculation_note).
    """
    kb = get_kb(domain)
    if not kb:
        return current_facts, None

    schema_lines = []
    allowed_proof_enums = []
    for field, info in kb["required_entities"].items():
        enum_str = f" (Allowed values: {info['enum']})" if "enum" in info else ""
        if "enum" in info:
            allowed_proof_enums = info["enum"]
        schema_lines.append(f"- {field} ({info['type']}): {info['description']}{enum_str}")

    schema_description = "\n".join(schema_lines)
    history_text = _format_history(recent_history)
    doctrinal_context = get_doctrinal_context(domain)

    prompt = EXTRACTION_SYSTEM_PROMPT.format(
        domain_name=kb["domain_name"],
        jurisdiction=kb.get("jurisdiction", "India"),
        schema_description=schema_description,
        doctrinal_context=doctrinal_context,
        current_facts_json=json.dumps(_public_facts(current_facts), ensure_ascii=False, indent=2),
        history_text=history_text,
        allowed_proof_enums=json.dumps(allowed_proof_enums)
    )

    calc_note = None
    try:
        content = call_llm(
            system_prompt=prompt,
            user_prompt=f"Latest Client Message:\n\"{new_message}\"\n\nAnalyze the full transcript + latest message, formulate any needed math expression and LL.B. doctrinal diagnostic, and return the JSON.",
            temperature=0.1
        )
        if content:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            json_str = match.group(0) if content and match else content
            parsed = json.loads(json_str)

            if "extracted_facts" in parsed and isinstance(parsed["extracted_facts"], dict):
                extracted = parsed["extracted_facts"]
                calc_note = parsed.get("lawyer_calculation_note")
                case_nuances = parsed.get("case_nuances")
                doctrinal_analysis = parsed.get("llb_doctrinal_analysis")
                math_expr = parsed.get("claim_math_expression")
                target_field = parsed.get("claim_target_field")
            else:
                extracted = parsed
                case_nuances = None
                doctrinal_analysis = None
                math_expr = None
                target_field = None

            merged = dict(current_facts)
            for k, v in extracted.items():
                if k in kb["required_entities"] and v is not None and v != "" and v != "null":
                    merged[k] = v

            # Deterministic Python AST evaluation of symbolic math expression
            if math_expr and str(math_expr).lower() != "null":
                exact_val = _safe_eval_math(str(math_expr))
                if exact_val is not None:
                    if target_field and target_field in kb["required_entities"]:
                        merged[target_field] = exact_val
                    else:
                        # Auto-bind to the primary claim amount field of the domain
                        for cand in ("total_amount_owed", "amount_withheld", "claim_amount", "principal_amount_owed"):
                            if cand in kb["required_entities"]:
                                merged[cand] = exact_val
                                break
                    verified_str = f"Exact Formula: {math_expr} = ₹{exact_val:,}"
                    calc_note = f"{verified_str}. {calc_note or ''}".strip()

            if calc_note and str(calc_note).lower() != "null":
                merged["_calculation_note"] = str(calc_note)
            if doctrinal_analysis and str(doctrinal_analysis).lower() != "null":
                merged["_doctrinal_analysis"] = str(doctrinal_analysis)
            if case_nuances and str(case_nuances).lower() != "null":
                prev_nuances = merged.get("_case_nuances", "")
                if str(case_nuances) not in prev_nuances:
                    merged["_case_nuances"] = f"{prev_nuances} | {case_nuances}".strip(" |")

            return merged, calc_note
    except Exception as e:
        print(f"Fact extraction error: {e}")

    return current_facts, None


def extract_facts(
    domain: str,
    new_message: str,
    current_facts: Dict[str, Any],
    recent_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Backward-compatible wrapper returning updated_facts dict."""
    updated_facts, _ = extract_facts_with_reasoning(domain, new_message, current_facts, recent_history)
    return updated_facts


def check_missing_variables(domain: str, facts: Dict[str, Any]) -> List[str]:
    kb = get_kb(domain)
    if not kb:
        return []
    missing = []
    for field in kb["required_entities"]:
        val = facts.get(field)
        if val is None or val == "" or val == "null":
            missing.append(field)
    return missing


def generate_lawyer_turn_response(
    domain: str,
    missing_fields: List[str],
    user_message: str,
    facts: Dict[str, Any],
    recent_history: List[Dict[str, Any]],
    calculation_note: Optional[str] = None,
    language_code: Optional[str] = None
) -> str:
    """
    Dynamic, non-hardcoded Multi-Turn AI Lawyer Dialogue Engine equipped with
    Bar Council of India (BCI) LL.B. Doctrinal, Procedural, and Evidentiary Reasoning.
    """
    kb = get_kb(domain)
    if not kb:
        return "Kripya apni samasya ke baare me thoda aur vistar se batayein."

    target_lang = LANG_NAMES.get(language_code, "the client's exact language and script")
    is_complete = len(missing_fields) == 0
    turn_count = len([m for m in recent_history if m.get("role") == "assistant"])

    primary_missing = missing_fields[:2]
    missing_descriptions = [
        f"{f} ({kb['required_entities'][f]['description']})"
        for f in primary_missing if f in kb["required_entities"]
    ]

    proof_val = str(facts.get("proof_status", ""))
    oral_risk_note = (
        "Include a brief Evidentiary Strategy Note: explain how even oral/informal agreements are enforceable via Section 10 & Section 70 (Restitution / Quantum Meruit) of the Indian Contract Act, 1872 when corroborated by digital records (UPI/WhatsApp/SMS) certified under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023."
        if is_complete and ("oral" in proof_val or "informal" in proof_val) else ""
    )

    active_calc = calculation_note or facts.get("_calculation_note")
    nuances = facts.get("_case_nuances")
    doctrinal_diag = facts.get("_doctrinal_analysis")
    doctrinal_context = get_doctrinal_context(domain)
    prec_info = facts.get("_precedent_search", {})
    prec_synthesis = prec_info.get("precedent_synthesis") if prec_info.get("triggered") else None
    prec_list_str = json.dumps(prec_info.get("precedents", []), ensure_ascii=False) if prec_info.get("triggered") else "None (Simple/routine turn below severity threshold)"

    if is_complete:
        task_instruction = f"""CASE INTAKE STATUS: COMPLETE — All essential facts for the Legal Notice are verified!
Your objectives for this response:
1. ADDRESS THE CLIENT'S LATEST INPUT & SHOW ANY MATH:
   - If a calculation or breakdown was performed ({active_calc or 'None'}) or if the client asked a specific question, walk through the exact arithmetic and reasoning clearly.
2. DELIVER LL.B.-GRADE GROUNDED LEGAL STANDING & PRECEDENT SUPPORT (OR ANSWER FOLLOW-UP WITHOUT REPETITION):
   - Check the Conversation Transcript below. If this is the first turn where the case completed, explain their Legal Standing clearly in {target_lang} using the LL.B. Doctrinal Analysis above and ONLY these verified Indian statutes:
     Principles: {kb['grounded_legal_standing']['en']}
     Permissible Statutes: {', '.join(kb['permissible_statutes'])}
   - If Precedent Research was triggered for this severe case ({prec_synthesis or 'None'}), briefly cite the 1 most relevant Supreme Court / High Court precedent from 'Retrieved Court Precedents' to reassure the client! (Do NOT invent any unverified case names!)
   - If you ALREADY explained their Legal Standing in a previous turn and the client is now asking a follow-up question or modifying a detail, answer their specific question directly without repeating your earlier speech!
3. {oral_risk_note}
4. Point the client to their custom-drafted **Formal Legal Notice of Demand** in the Legal Notice panel (ready for PDF download and dispatch via Registered Post A.D. / Speed Post / Official Email / WhatsApp under Section 27 General Clauses Act).
5. VOICE & UX CONCISENESS: Do NOT paste the raw Legal Notice document inside this chat bubble (the UI renders the formatted Legal Notice document and PDF button automatically). Keep your spoken reply natural, sharp, and 4–6 sentences long."""
    else:
        task_instruction = f"""CASE INTAKE STATUS: IN PROGRESS (Previous lawyer turns: {turn_count}).
Your objectives for this response:
1. APPLY LL.B. LEGAL REASONING TO WHAT THE CLIENT JUST SAID (NO CANNED TEMPLATES!):
   - Engage directly with what the client just said in "{user_message}".
   - If you performed any financial calculation or legal deduction analysis ({active_calc or 'None'}), state the exact numbers you computed and why.
   - If the client raised a doctrinal, procedural, or evidentiary concern, or if live Precedent Research was triggered on this turn ({prec_synthesis or 'None'}), briefly reference the applicable statutory rule and/or retrieved precedent ({', '.join(kb['permissible_statutes'])}).
2. ZERO REPETITION ACROSS TURNS (CRITICAL):
   - Read the 'Conversation Transcript So Far'.
   - NEVER repeat stock sympathy lines, greetings, or reassurances that you already said in an earlier turn. Speak with natural human continuity.
3. GATHER THE NEXT ESSENTIAL DETAILS NATURALLY:
   - To complete the Legal Notice, we still need: {', '.join(missing_descriptions)}.
   - Ask for these organically in 1–2 conversational sentences tailored to the client's situation (do not sound like a rigid questionnaire)."""

    system_prompt = f"""You are NyayaMitra, a sharp, seasoned Indian Advocate trained in the Bar Council of India (BCI) LL.B. curriculum, advising a client on {kb['domain_name']} ({kb.get('jurisdiction', 'India')}).
Language Directive: Respond in {target_lang}, matching the client's script and natural register.

BCI LL.B. Doctrinal & Procedural Toolkit:
{doctrinal_context}

Case-Specific LL.B. Doctrinal Diagnostic:
{doctrinal_diag or "Apply the BCI LL.B. Doctrinal Toolkit above."}

Retrieved Court Precedents (Live IndianKanoon & Landmark SC Search):
{prec_list_str}
Precedent Application Synthesis:
{prec_synthesis or "None"}

Conversation Transcript So Far:
{_format_history(recent_history)}

Latest Client Message:
"{user_message}"

Verified Case Facts Extracted So Far:
{json.dumps(_public_facts(facts), ensure_ascii=False)}

Additional Case Nuances Captured:
{nuances or "None"}

Financial / Legal Calculation Performed:
{active_calc or "None"}

{task_instruction}"""

    try:
        reply = call_llm(
            system_prompt=system_prompt,
            user_prompt="Generate your next natural, non-repetitive, doctrinally sharp lawyer response now.",
            temperature=0.25
        )
        if reply:
            return reply
    except Exception as e:
        print(f"Lawyer response error: {e}")

    if is_complete:
        standing_text = kb["grounded_legal_standing"]["hi"]
        return (
            f"✅ **Aapke sabhi zaroori facts verify ho chuke hain.**\n\n"
            f"**Aapki Kanooni Sthiti (Legal Standing):**\n{standing_text}\n\n"
            f"Maine aapke liye ek Formal Legal Notice of Demand draft kar diya hai."
        )
    field_prompts = [kb["required_entities"][f]["clarification_prompt"] for f in primary_missing if f in kb["required_entities"]]
    return "Aage badhne ke liye kripya yeh details batayein:\n" + "\n".join(f"- {p}" for p in field_prompts)


def generate_clarification_response(
    domain: str,
    missing_fields: List[str],
    user_message: str,
    facts: Dict[str, Any],
    language_code: Optional[str] = None,
    recent_history: Optional[List[Dict[str, Any]]] = None,
    calculation_note: Optional[str] = None
) -> str:
    """Wrapper that delegates to the context-aware multi-turn generate_lawyer_turn_response."""
    return generate_lawyer_turn_response(
        domain=domain,
        missing_fields=missing_fields,
        user_message=user_message,
        facts=facts,
        recent_history=recent_history or [],
        calculation_note=calculation_note,
        language_code=language_code
    )


def assemble_legal_notice(domain: str, facts: Dict[str, Any]) -> str:
    """
    BCI Clinical Legal Education ('Drafting, Pleading & Conveyancing') Bespoke Legal Notice Draftsman.
    Synthesizes all captured facts, Neuro-Symbolic math breakdowns, LL.B. doctrinal diagnostics,
    retrieved court precedents, and case nuances into an enforceable Indian Legal Notice.
    """
    kb = get_kb(domain)
    if not kb:
        return ""

    current_date = datetime.now().strftime("%d %B, %Y")
    cache_key = f"{domain}:{current_date}:{json.dumps(facts, sort_keys=True, ensure_ascii=False)}"
    if cache_key in _NOTICE_CACHE:
        return _NOTICE_CACHE[cache_key]

    public_facts = _public_facts(facts)
    calc_note = facts.get("_calculation_note")
    case_nuances = facts.get("_case_nuances")
    doctrinal_diag = facts.get("_doctrinal_analysis")
    doctrinal_context = get_doctrinal_context(domain)
    prec_info = facts.get("_precedent_search", {})
    prec_list = prec_info.get("precedents", []) if prec_info.get("triggered") else []

    raw_proof = str(public_facts.get("proof_status", ""))
    readable_proof = PROOF_HUMAN_READABLE.get(raw_proof, raw_proof.replace("_", " "))

    drafting_prompt = f"""You are a Senior Indian Advocate & Clinical Professor of 'Drafting, Pleading and Conveyancing' (BCI LL.B. Standard) preparing a formal, enforceable pre-litigation **LEGAL NOTICE OF DEMAND** in English.

Dispute Category: {kb['domain_name']} ({kb.get('jurisdiction', 'India')})
Date of Notice: {current_date}

Verified Structured Case Facts:
{json.dumps(public_facts, ensure_ascii=False, indent=2)}

Evidentiary Basis Description: {readable_proof}
Neuro-Symbolic Financial Calculation Breakdown: {calc_note or "Use the principal claim amount in Verified Facts"}
LL.B. Doctrinal, Forum & Evidentiary Analysis: {doctrinal_diag or "Apply standard domain doctrines"}
Additional Case-Specific Nuances & Grievances: {case_nuances or "None"}

Retrieved Judicial Precedents (ONLY cite from this list if applicable):
{json.dumps(prec_list, ensure_ascii=False, indent=2)}

BCI LL.B. Doctrinal Reference for Drafting:
{doctrinal_context}

CLOSED-WORLD STATUTORY & PRECEDENT GROUNDING (CRITICAL):
1. You may ONLY cite statutes from: {json.dumps(kb['permissible_statutes'])}
2. You may ONLY cite judicial precedents from the 'Retrieved Judicial Precedents' list above. Do NOT invent any fake case laws or phantom sections!

DRAFTING, PLEADING & CONVEYANCING (DPC) REQUIREMENTS:
1. Format the document cleanly in Markdown as a formal Indian Legal Notice:
   - Top Line: `**WITHOUT PREJUDICE**`
   - Header: `**FORMAL LEGAL NOTICE OF DEMAND**` and `*(Dispatched via Registered Post A.D. / Speed Post / Registered Email / WhatsApp under Section 27 of the General Clauses Act, 1897)*`
   - `**Date:** {current_date}`
   - `**To:**` (Opposite party name and address/location from facts)
   - `**From (Claimant / Noticee Sender):**` (Claimant name and role/location from facts)
   - `**SUBJECT:**` (Bold, uppercase subject line stating the exact nature of demand, statutory provisions invoked, and exact claim amount in Rs.)
2. Chronological Numbered Paragraphs (`1.`, `2.`, `3.`, `4.`, `5.`, `6.`, `7.`):
   - Tailor the factual narrative specifically to this client's case!
   - Explicitly include the exact mathematical calculation breakdown from 'Neuro-Symbolic Financial Calculation Breakdown' and any extra reliefs from 'Additional Case-Specific Nuances'.
   - Invoke the applicable substantive doctrines and, if 'Retrieved Judicial Precedents' is non-empty, cite the most relevant landmark precedent from that list to fortify the legal demand!
   - Explicitly state that all digital/electronic records (WhatsApp, emails, UPI/bank statements) are preserved for production with a **Section 63 Certificate under the Bharatiya Sakshya Adhiniyam, 2023**.
   - Include an unequivocal **15-Day Statutory Cure / Demand Clause** specifying the exact principal amount in INR plus 18% p.a. interest (Section 34 CPC) and any non-monetary relief.
   - Include a formal **Jurisdiction & Consequences of Non-Compliance Clause** identifying the exact competent Forum/Court and warning of civil/statutory proceedings *"at your sole risk as to costs and consequences."*
3. Sign-off with the Claimant's name at the bottom. Output ONLY the Legal Notice markdown text."""

    try:
        bespoke_draft = call_llm(
            system_prompt=drafting_prompt,
            user_prompt="Draft the complete, case-specific Formal Legal Notice of Demand now.",
            temperature=0.15
        )
        if bespoke_draft and len(bespoke_draft.strip()) > 200:
            cleaned = bespoke_draft.strip()
            _NOTICE_CACHE[cache_key] = cleaned
            return cleaned
    except Exception as e:
        print(f"Bespoke notice drafting error, falling back to template: {e}")

    # Deterministic template fallback if offline
    template = kb.get("legal_notice_template", "")
    formatted_facts = dict(public_facts)
    formatted_facts["proof_status"] = readable_proof
    slots = {
        "current_date": current_date,
        **{k: formatted_facts.get(k, f"[{k.replace('_', ' ').upper()}]") for k in kb["required_entities"]}
    }
    try:
        draft = template.format(**slots)
        _NOTICE_CACHE[cache_key] = draft
        return draft
    except KeyError:
        return template


def generate_roleplay_response(
    domain: str,
    facts: Dict[str, Any],
    user_argument: str,
    language_code: Optional[str] = None,
    missing_fields: Optional[List[str]] = None,
    recent_history: Optional[List[Dict[str, Any]]] = None,
    calculation_note: Optional[str] = None
) -> Dict[str, str]:
    """
    Implements Problem 2 Direction #4: 'Help them argue, for example by playing the other side so they can practise'.
    Adapts dynamically to any counterparty role (Landlord, HR/Employer, Seller/Service Provider, or Debtor/Client).
    """
    kb = get_kb(domain)
    target_lang = LANG_NAMES.get(language_code, "Hinglish / the user's language")

    role_map = {
        "rental_deposit": "Stubborn Landlord / Property Owner",
        "unpaid_salary": "Defensive Company HR / Management",
        "consumer_dispute": "Evasive Company Grievance Officer / Seller",
        "money_recovery": "Defaulting Client / Debtor"
    }
    counterparty_role = role_map.get(domain, "Opposite Party")

    if missing_fields is None:
        missing_fields = check_missing_variables(domain, facts)
    primary_missing = missing_fields[:2]
    missing_descriptions = [
        f"{f} ({kb['required_entities'][f]['description']})"
        for f in primary_missing if kb and f in kb["required_entities"]
    ]

    active_calc = calculation_note or facts.get("_calculation_note")
    public_facts = _public_facts(facts)

    missing_guidance = (
        f"FACT-CAPTURE GOAL: We still need these details from the user: {', '.join(missing_descriptions)}. "
        f"Have the {counterparty_role} naturally challenge the user on {', '.join(primary_missing)} in character, "
        f"and make the Coach Tip + Suggested Argument guide the user to state {', '.join(primary_missing)} in their next reply!"
        if primary_missing else
        "All core case facts are captured! Make the counterparty push back realistically on the merits (or begin conceding if the user cites the applicable Indian statutes and 15-day Legal Notice)."
    )

    system_prompt = f"""You are running an Interactive Legal Negotiation & Fact-Capture Roleplay Simulator for a citizen in India.
Case Domain: {kb['domain_name'] if kb else domain}
Counterparty Role: {counterparty_role}
Currently Captured Facts: {json.dumps(public_facts, ensure_ascii=False)}
Calculation / Reasoning Note: {active_calc or 'None'}
Missing Facts Still Needed: {json.dumps(primary_missing, ensure_ascii=False)}
Permissible Legal Statutes: {json.dumps(kb['permissible_statutes'] if kb else [], ensure_ascii=False)}
Recent Conversation History:
{_format_history(recent_history or [])}

User's latest argument: "{user_argument}"

{missing_guidance}

Respond STRICTLY in valid JSON with three keys in natural conversational {target_lang} (without repeating previous turns):
{{
  "counterparty_reply": "In-character response from the {counterparty_role} in {target_lang} (1-2 realistic sentences pushing back AND, if facts are missing, challenging the user on {', '.join(primary_missing) if primary_missing else 'their legal claim'}).",
  "coach_tip": "Tactical coaching feedback from NyayaMitra in {target_lang} (1-2 sentences rating their argument, confirming any calculation performed, noting what facts are captured vs. still needed, and which statute from Permissible Legal Statutes to cite).",
  "suggested_argument": "A strong, ready-to-speak next argument in first-person in {target_lang} that weaves in the user's captured facts, fills in {', '.join(primary_missing) if primary_missing else 'the 15-day Legal Notice ultimatum'}, and cites the relevant law."
}}"""

    try:
        content = call_llm(
            system_prompt=system_prompt,
            user_prompt="Generate the JSON roleplay response.",
            temperature=0.3
        )
        if content:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            json_str = match.group(0) if match else content
            data = json.loads(json_str)
            return {
                "counterparty_reply": data.get("counterparty_reply", "Main abhi paise wapas nahi kar sakta."),
                "coach_tip": data.get("coach_tip", "Apne facts aur evidence ke saath Section 73 Contract Act ka hawala dein."),
                "suggested_argument": data.get("suggested_argument", "")
            }
    except Exception as e:
        print(f"Roleplay error: {e}")

    return {
        "counterparty_reply": "Dekhiye, hamारी policy ke hisaab se abhi yeh payment process nahi ho sakta.",
        "coach_tip": "Saamne wali party ko apna exact claim amount, timeline aur proof batate hue 15-day Legal Notice ki chetavni dein.",
        "suggested_argument": "Mere paas saare saboot maujood hain. Kanoon ke mutabiq agar 15 din me mera bकाया clear nahi hua toh main legal notice aur recovery case file karunga."
    }
