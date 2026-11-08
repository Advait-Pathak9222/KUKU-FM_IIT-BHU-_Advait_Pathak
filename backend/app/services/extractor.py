import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from .sarvam_client import call_llm
from ..kb import get_kb

EXTRACTION_SYSTEM_PROMPT = """You are the Senior Legal & Financial Reasoning Engine for an Indian civil legal assistant.
Your job is to analyze the full multi-turn conversation history and the user's latest message, perform any necessary financial/legal calculations (like a sharp Indian lawyer), and extract/update the structured case facts.

Domain: {domain_name}
Target Schema & Descriptions:
{schema_description}

Current Extracted Facts So Far:
{current_facts_json}

Full Conversation History So Far:
{history_text}

LAWYER INTELLIGENCE & CALCULATION RULES:
1. MULTI-TURN MEMORY & INFERENCE:
   - Read BOTH the 'Full Conversation History' and the 'Latest User Message'.
   - If the user mentioned a fact in an earlier turn (e.g., "मेरी सैलरी 2 महीने से नहीं आई", "मैं कंपनी में काम करता हूँ", "ऑफर लेटर पर मेरा नाम..."), combine it with new details from the latest turn!
   - Infer 'employment_status' naturally from context: if the user says "मैं काम करता हूँ" / "I work at..." / "मैं अभी भी वहीं काम कर रहा हूँ", set 'employment_status' to "Currently Employed". If they resigned or were fired, set "Resigned" or "Terminated".
   - Infer 'proof_status' naturally from context: if the user mentions "ऑफर लेटर" (Offer Letter), salary slips, bank transfers, UPI, rent agreement, or WhatsApp at ANY point in the conversation, immediately populate 'proof_status' from {allowed_proof_enums} without waiting to ask again!

2. FINANCIAL & ARITHMETIC REASONING (CRITICAL - DO THE MATH LIKE A REAL LAWYER!):
   - SALARY / CTC BREAKDOWN MATH: If the user provides their annual CTC or Fixed Pay instead of the exact total owed, CALCULATE 'total_amount_owed' yourself!
     * Example: If Annual CTC is ₹18,00,000 with ₹12,00,000 Fixed Pay (and ₹6,00,000 in stocks/ESOPs/joining bonus/perks) and salary is unpaid for 2 months:
       Monthly Fixed Salary = ₹12,00,000 / 12 = ₹1,00,000 per month.
       For 2 unpaid months, 'total_amount_owed' = 2 * 100000 = 200000!
     * If Monthly Salary is given (e.g. ₹60,000/month) and 3 months are unpaid, 'total_amount_owed' = 180000!
   - RENTAL DEPOSIT MATH:
     * If the user says they paid ₹80,000 deposit and the landlord returned ₹45,000, calculate 'amount_withheld' = 35000.
     * If the landlord is refusing to return the deposit at all ("पैसा नहीं दे रहा"), set 'amount_withheld' equal to 'deposit_amount_paid', and set 'landlord_deduction_reason' to the landlord's pretext or "Arbitrary refusal to refund deposit".
   - Record your exact calculation or legal deduction in the "lawyer_calculation_note" field so you can explain your math to the client!

3. CLEAN FORMATTING FOR FORMAL NOTICE SLOTS:
   - Store 'facts' values (names, company names, locations, designations) transliterated into clean English/Latin script (e.g., "Advait Pathak", "XYZ Company", "Bangalore", "Senior Software Developer") and amounts as plain integers (e.g., 200000) so they slot cleanly into the formal English Legal Notice.
   - If a field is genuinely not yet known and cannot be calculated from the conversation, keep it as null.

Return your output STRICTLY as valid JSON in this exact structure:
{{
  "facts": {{
    ...schema fields...
  }},
  "lawyer_calculation_note": "Brief explanation of any financial calculation or legal deduction performed on this turn (e.g. 'Calculated ₹2,00,000 unpaid salary for 2 months based on ₹12,00,000 annual fixed pay = ₹1,00,000/month, excluding ₹6,00,000 stocks/perks'), or null if none."
}}
"""

PROOF_HUMAN_READABLE = {
    "agreement_and_receipts": "executed Rent Agreement and payment receipts",
    "online_bank_transfer": "verified bank / UPI transfer records and written communications",
    "whatsapp_chats": "documented WhatsApp communications and possession handover records",
    "oral_agreement_only": "mutual oral tenancy arrangement and cash remittance",
    "offer_letter_and_slips": "official Offer Letter, appointment records, and salary statements",
    "bank_statement_and_emails": "verified bank salary credit statements and official emails",
    "relieving_letter": "official Offer Letter, Relieving Letter, and No-Dues clearance records",
    "informal_or_whatsapp": "documented employment communications and work delivery records"
}

LANG_NAMES = {
    "mr-IN": "Marathi (मराठी)",
    "hi-IN": "Hindi (हिंदी)",
    "bn-IN": "Bengali (বাংলা)",
    "ta-IN": "Tamil (தமிழ்)",
    "te-IN": "Telugu (తెలుగు)",
    "kn-IN": "Kannada (ಕನ್ನಡ)",
    "gu-IN": "Gujarati (ગુજરાતી)",
    "ml-IN": "Malayalam (മലയാളം)",
    "pa-IN": "Punjabi (ਪੰਜਾਬੀ)",
    "od-IN": "Odia (ଓଡ଼ିଆ)",
    "en-IN": "English"
}


def _format_history(recent_history: List[Dict[str, Any]]) -> str:
    if not recent_history:
        return "(Start of conversation)"
    lines = []
    for idx, msg in enumerate(recent_history, 1):
        role_label = "Client (User)" if msg.get("role") == "user" else "NyayaMitra (AI Lawyer)"
        lines.append(f"[{idx}] {role_label}: {msg.get('content', '')}")
    return "\n".join(lines)


def extract_facts_with_reasoning(
    domain: str,
    new_message: str,
    current_facts: Dict[str, Any],
    recent_history: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], Optional[str]]:
    kb = get_kb(domain)
    if not kb:
        return current_facts, None

    schema_desc = "\n".join([
        f"- {field}: {info['description']} (Type: {info['type']})"
        for field, info in kb["required_entities"].items()
    ])
    allowed_enums = kb["required_entities"].get("proof_status", {}).get("enum", [])

    prompt = EXTRACTION_SYSTEM_PROMPT.format(
        domain_name=kb["domain_name"],
        schema_description=schema_desc,
        current_facts_json=json.dumps(current_facts, ensure_ascii=False),
        history_text=_format_history(recent_history),
        allowed_proof_enums=", ".join(allowed_enums)
    )

    calc_note = None
    try:
        content = call_llm(
            system_prompt=prompt,
            user_prompt=f"Latest Client Statement:\n\"{new_message}\"\n\nExtract/update all facts and perform any needed CTC/salary/deposit math now.",
            temperature=0.1
        )
        if content:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            json_str = match.group(0) if match else content
            parsed = json.loads(json_str)

            # Support both nested {"facts": {...}, "lawyer_calculation_note": ...} and flat JSON
            if isinstance(parsed, dict) and "facts" in parsed and isinstance(parsed["facts"], dict):
                new_facts = parsed["facts"]
                calc_note = parsed.get("lawyer_calculation_note")
            else:
                new_facts = parsed

            merged = dict(current_facts)
            for k, v in new_facts.items():
                if k in kb["required_entities"] and v is not None and v != "" and v != "null":
                    field_type = kb["required_entities"].get(k, {}).get("type")
                    if field_type == "number" and isinstance(v, str):
                        digits = re.sub(r"[^\d.]", "", v)
                        if digits:
                            try:
                                v = int(float(digits))
                            except ValueError:
                                pass
                    merged[k] = v
            return merged, calc_note
    except Exception as e:
        print(f"Extraction error: {e}")

    return current_facts, None


def extract_facts(
    domain: str,
    new_message: str,
    current_facts: Dict[str, Any],
    recent_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Backward-compatible wrapper returning updated facts dict."""
    updated_facts, _ = extract_facts_with_reasoning(domain, new_message, current_facts, recent_history)
    return updated_facts


def check_missing_variables(domain: str, facts: Dict[str, Any]) -> List[str]:
    kb = get_kb(domain)
    if not kb:
        return []
    missing = []
    for field, info in kb["required_entities"].items():
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
    Context-aware, non-repetitive Multi-Turn AI Lawyer Dialogue Generator.
    Uses full conversation history, explains any CTC/deposit calculations performed,
    never repeats stock empathy phrases across turns, and either asks naturally for
    remaining details OR delivers the final grounded legal standing when complete.
    """
    kb = get_kb(domain)
    if not kb:
        return "Kripya apni samasya ke baare me thoda aur vistar se batayein."

    target_lang = LANG_NAMES.get(language_code, "the user's exact language and script")
    is_complete = len(missing_fields) == 0
    turn_count = len([m for m in recent_history if m.get("role") == "assistant"])

    primary_missing = missing_fields[:2]
    missing_descriptions = [
        f"{f} ({kb['required_entities'][f]['description']})"
        for f in primary_missing if f in kb["required_entities"]
    ]

    proof_val = str(facts.get("proof_status", ""))
    oral_risk_note = (
        "Also include an honest Evidentiary Risk Note: since their proof is oral/informal, advise them to gather secondary proof (like bank statements, utility bills, emails, or witness testimony) while confirming that sending this Legal Notice is still their strongest first step."
        if is_complete and proof_val in ("oral_agreement_only", "informal_or_whatsapp") else ""
    )

    if is_complete:
        task_instruction = f"""ALL 8 CASE FACTS ARE NOW COMPLETE AND VERIFIED!
Your task on this turn:
1. DIRECTLY ADDRESS THE USER'S LATEST MESSAGE:
   - If you just performed a calculation (Calculation Note: {calculation_note or 'None'}) or if the user asked you to calculate/verify their salary or deposit breakdown, clearly walk through the exact math (e.g. ₹12,00,000 Fixed Pay / 12 = ₹1,00,000/month × 2 unpaid months = ₹2,00,000, and explain why unvested stocks/joining bonus after 4 months are excluded from monthly wage arrears).
2. AVOID REPEATING PREVIOUS TURNS:
   - Check 'Conversation History So Far'. If you have NOT yet explained their Legal Standing, explain it clearly and concisely in {target_lang} using ONLY these grounded legal principles:
     {kb['grounded_legal_standing']['en']}
     Permissible Statutes to cite: {', '.join(kb['permissible_statutes'])}
     (Do NOT invent any other laws or sections!)
   - If you ALREADY explained their Legal Standing and Legal Notice in the previous turn and the client is asking a follow-up question or confirming a detail, answer their specific question directly and naturally without repeating the entire previous explanation!
3. {oral_risk_note}
4. Let them know their **Formal Legal Notice of Demand** (for ₹{facts.get('total_amount_owed') or facts.get('deposit_amount')}) is ready in the Legal Notice panel to download as a PDF.
5. CRITICAL: Do NOT write or draft the full Legal Notice document inside this chat reply. Keep your spoken response crisp, natural, and conversational (4–6 sentences max)!"""
    else:
        task_instruction = f"""We are in an active multi-turn legal consultation (Assistant previous turns: {turn_count}).
Your task on this turn:
1. DIRECTLY ENGAGE WITH WHAT THE CLIENT JUST SAID:
   - If the client shared a CTC breakdown, salary math, or deduction details (Calculation Note: {calculation_note or 'None'}), explicitly confirm the exact numbers you calculated and recorded (e.g., "आपके ₹12 लाख Fixed Pay के हिसाब से महीने की सैलरी ₹1,00,000 बनती है, यानी 2 महीने का ₹2,00,000 बकाया हमने नोट कर लिया है, और स्टॉक्स/बोनस को इसमें शामिल नहीं किया है").
   - If the client asked about arresting someone under IPC 420 / police FIR, gently clarify that unpaid salary or rent deposit is primarily a civil/labour recovery matter first.
2. STRICT ANTI-REPETITION RULE (CRITICAL!):
   - Look at the 'Conversation History So Far' below.
   - If you ALREADY expressed sympathy or said "strong civil legal remedies मौजूद हैं" / "समझ सकता हूँ कि यह stressful है" in a previous turn, DO NOT REPEAT IT AGAIN! Real human lawyers do not repeat canned sympathy lines on every single turn. Jump straight into the substance!
3. NATURALLY ASK FOR THE NEXT MISSING DETAILS:
   - We still need: {', '.join(missing_descriptions)}.
   - Ask for these naturally and conversationally in 1-2 crisp sentences without sounding like a robotic form."""

    system_prompt = f"""You are NyayaMitra, a sharp, empathetic, and practical Indian Civil & Labour Lawyer speaking with a client.
Client's Language: {target_lang} (Match the client's script and natural conversational style—blending regional language with common English terms like 'CTC', 'Fixed Pay', 'Offer Letter', 'deposit', 'Legal Notice', 'HR').

Conversation History So Far:
{_format_history(recent_history)}

Latest Client Message:
"{user_message}"

Verified Case Facts Extracted So Far:
{json.dumps(facts, ensure_ascii=False)}

Calculation / Reasoning Performed on This Turn:
{calculation_note or "None"}

{task_instruction}"""

    try:
        reply = call_llm(
            system_prompt=system_prompt,
            user_prompt="Generate your next conversational lawyer response now, strictly avoiding any repetition of previous turns.",
            temperature=0.2
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
    kb = get_kb(domain)
    if not kb or "legal_notice_template" not in kb:
        return ""
    
    template = kb["legal_notice_template"]
    current_date = datetime.now().strftime("%d %B, %Y")
    
    formatted_facts = dict(facts)
    raw_proof = str(formatted_facts.get("proof_status", ""))
    if raw_proof in PROOF_HUMAN_READABLE:
        formatted_facts["proof_status"] = PROOF_HUMAN_READABLE[raw_proof]
    elif "_" in raw_proof:
        formatted_facts["proof_status"] = raw_proof.replace("_", " ")

    slots = {
        "current_date": current_date,
        **{k: formatted_facts.get(k, f"[{k.replace('_', ' ').upper()}]") for k in kb["required_entities"]}
    }
    
    try:
        draft = template.format(**slots)
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
    Uses full conversation history, financial calculation reasoning, and missing-fact elicitation.
    """
    kb = get_kb(domain)
    target_lang = LANG_NAMES.get(language_code, "Hinglish / the user's language")
    counterparty_role = "Stubborn Landlord (Makaan-Maalik)" if domain == "rental_deposit" else "Defensive Company HR / Management"
    
    if missing_fields is None:
        missing_fields = check_missing_variables(domain, facts)
    primary_missing = missing_fields[:2]
    missing_descriptions = [
        f"{f} ({kb['required_entities'][f]['description']})"
        for f in primary_missing if kb and f in kb["required_entities"]
    ]

    missing_guidance = (
        f"CRITICAL FACT-CAPTURE GOAL: We still need to capture these missing case facts from the user: {', '.join(missing_descriptions)}. "
        f"Make the {counterparty_role} naturally challenge or question the user about {', '.join(primary_missing)} in character (e.g., questioning the exact amount, date, property/company name, or proof), "
        f"and make the Coach Tip + Suggested Argument explicitly guide the user to state {', '.join(primary_missing)} in their next reply!"
        if primary_missing else
        "All 8 case facts are already verified! Make the counterparty push back on the dispute merits (or start conceding if the user cites Section 73 Contract Act / Order 37 CPC)."
    )

    system_prompt = f"""You are running an Interactive Legal Negotiation & Fact-Capture Roleplay Simulator for an ordinary citizen in India.
Case Domain: {kb['domain_name'] if kb else domain}
Currently Captured Facts: {json.dumps(facts, ensure_ascii=False)}
Calculation / Reasoning Note: {calculation_note or 'None'}
Missing Facts Still Needed: {json.dumps(primary_missing, ensure_ascii=False)}
Permissible Legal Statutes: {json.dumps(kb['permissible_statutes'] if kb else [], ensure_ascii=False)}
Recent Conversation History:
{_format_history(recent_history or [])}

The user is arguing their case against the {counterparty_role}.
User's latest argument: "{user_argument}"

{missing_guidance}

Respond STRICTLY in valid JSON with three keys in natural conversational {target_lang} (Indic + English loanwords, without repeating previous turns):
{{
  "counterparty_reply": "In-character response from the {counterparty_role} in {target_lang} (1-2 realistic sentences pushing back AND, if facts are missing, challenging the user on {', '.join(primary_missing) if primary_missing else 'their legal claim'} so they state those facts next).",
  "coach_tip": "Tactical coaching feedback from NyayaMitra in {target_lang} (1-2 sentences rating their argument, confirming any calculation performed, noting what facts are captured vs. still needed [{', '.join(primary_missing) if primary_missing else 'All facts complete!'}], and which statute like Section 73 Contract Act or Order 37 CPC to cite).",
  "suggested_argument": "A strong, ready-to-speak next argument in first-person ('Main...') in {target_lang} that weaves in the user's captured facts ({json.dumps(facts, ensure_ascii=False)}), fills in or states {', '.join(primary_missing) if primary_missing else 'the 15-day Legal Notice ultimatum'}, and cites the relevant law."
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
                "coach_tip": data.get("coach_tip", "Unhe yaad dilayein ki Section 73 Indian Contract Act ke tehat bina pakke bill ke paise rokna kanoonan galat hai."),
                "suggested_argument": data.get("suggested_argument", "")
            }
    except Exception as e:
        print(f"Roleplay error: {e}")

    if domain == "rental_deposit":
        return {
            "counterparty_reply": "Dekho bhai, flat me painting aur cleaning ka kharcha toh katega hi, aur tumhare paas kya saboot hai ki kitna deposit diya tha?",
            "coach_tip": "Landlord ko apna exact deposit amount, flat address, aur proof batayein, aur bolein ki *normal wear and tear* Section 73 Contract Act ke tehat nahi kat sakta.",
            "suggested_argument": "Maine aapko bank transfer se poora deposit diya tha aur flat saaf halat me khali kiya hai. Section 73 Indian Contract Act ke mutabiq bina pakke bill ke aap paisa nahi kaat sakte!"
        }
    return {
        "counterparty_reply": "Dekhiye, abhi company ke paas client se funds nahi aaye hain, isliye aapka FnF settlement hold par hai.",
        "coach_tip": "HR ko apna exact pending salary amount, mahine, aur designation batayein, aur bolein ki *client payment delay* ka bahana banakar earned salary rokna illegal hai.",
        "suggested_argument": "Client payment delay company ka business risk hai. Payment of Wages Act aur Section 73 Contract Act ke mutabiq meri earned salary 15 din me clear kijiye warna main Order 37 CPC me recovery suit file karunga."
    }
