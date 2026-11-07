import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from .sarvam_client import call_llm
from ..kb import get_kb

EXTRACTION_SYSTEM_PROMPT = """You are a Legal Entity Extractor for an Indian legal assistance system.
Your job is to extract factual variables from the user's conversational message and update the existing case state.

Domain: {domain_name}
Target Schema & Descriptions:
{schema_description}

Current Extracted Facts:
{current_facts_json}

RULES:
1. ONLY extract information clearly present or directly implied in the user's message.
2. If a fact was previously null and is now provided, populate it.
3. If the user corrects a previous fact (e.g. changing amount or date), overwrite with the new value.
4. Do NOT hallucinate names, dates, or amounts not mentioned by the user. If a field is not mentioned, keep it as null.
5. SMART COMPLETENESS RULES:
   - In 'rental_deposit': If the user states the landlord is refusing to return the deposit at all (e.g. "paisa nahi dega", "not returning my deposit") and no partial return is mentioned, set 'amount_withheld' equal to 'deposit_amount_paid'. If the landlord gave a pretext (e.g. "claiming no proof exists", "saying no money right now") or gave no reason at all, record that in 'landlord_deduction_reason' (e.g. "Arbitrary refusal / claiming lack of written proof").
   - In 'unpaid_salary': If the user mentions Full and Final (FnF) settlement or notice period dues without naming specific calendar months, populate 'unpaid_months' with the period description (e.g. "Full & Final (FnF) settlement post resignation").
6. For 'proof_status', select from the allowed enum values: {allowed_proof_enums}. If the user mentions having no written agreement or paying cash, classify as 'oral_agreement_only' (or 'informal_or_whatsapp').
7. Clean formatting: Extract names, locations, and reasons transliterated into clean English/Latin script (e.g. "Ramesh Kumar", "Painting charges") and amounts as plain numbers (e.g. 35000, not "35,000") so they slot cleanly into a formal English Legal Notice.
8. Return your output STRICTLY as valid JSON matching the schema fields, with no markdown wrapping.
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

def extract_facts(
    domain: str,
    new_message: str,
    current_facts: Dict[str, Any],
    recent_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    kb = get_kb(domain)
    if not kb:
        return current_facts

    schema_desc = "\n".join([
        f"- {field}: {info['description']} (Type: {info['type']})"
        for field, info in kb["required_entities"].items()
    ])
    allowed_enums = kb["required_entities"].get("proof_status", {}).get("enum", [])

    prompt = EXTRACTION_SYSTEM_PROMPT.format(
        domain_name=kb["domain_name"],
        schema_description=schema_desc,
        current_facts_json=json.dumps(current_facts, ensure_ascii=False),
        allowed_proof_enums=", ".join(allowed_enums)
    )

    try:
        content = call_llm(
            system_prompt=prompt,
            user_prompt=f"New user statement:\n\"{new_message}\"",
            temperature=0.1
        )
        if content:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            json_str = match.group(0) if match else content
            new_facts = json.loads(json_str)

            merged = dict(current_facts)
            for k, v in new_facts.items():
                if v is not None and v != "" and v != "null":
                    # Clean numeric strings like "Rs. 80,000" -> 80000 for numeric fields
                    field_type = kb["required_entities"].get(k, {}).get("type")
                    if field_type == "number" and isinstance(v, str):
                        digits = re.sub(r"[^\d.]", "", v)
                        if digits:
                            try:
                                v = int(float(digits))
                            except ValueError:
                                pass
                    merged[k] = v
            return merged
    except Exception as e:
        print(f"Extraction error: {e}")

    return current_facts


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


def generate_clarification_response(
    domain: str,
    missing_fields: List[str],
    user_message: str,
    facts: Dict[str, Any],
    language_code: Optional[str] = None
) -> str:
    kb = get_kb(domain)
    
    # Pick the top 1 or 2 most critical missing fields to avoid overwhelming the user
    primary_missing = missing_fields[:2]
    field_prompts = [kb["required_entities"][f]["clarification_prompt"] for f in primary_missing if f in kb["required_entities"]]
    
    target_lang = LANG_NAMES.get(language_code, "the user's exact regional language")
    
    # Check if user actually asked about IPC 420 / police arrest / jail
    lower_msg = user_message.lower()
    asked_criminal = any(w in lower_msg for w in ["420", "arrest", "jail", "police", "fir"])
    criminal_instruction = (
        f"2. Since the user asked about police arrest or IPC 420, gently clarify in {target_lang} that this is primarily a civil/labour recovery matter rather than a criminal arrest case.\n"
        if asked_criminal else
        f"2. Briefly reassure them in {target_lang} that they have strong civil legal remedies to recover their money.\n"
    )

    system_prompt = f"""You are a helpful, empathetic legal assistant in India helping an ordinary citizen with their {kb['domain_name']}.
The user communicated in: {target_lang}
User's message: "{user_message}"
Currently extracted facts: {json.dumps(facts, ensure_ascii=False)}

We still need to know:
{", ".join(primary_missing)}

LANGUAGE & TONE GUIDELINES (NATURAL INDIC + ENGLISH CODE-MIXING):
1. Respond using the user's regional language ({target_lang}) naturally blended with common English loanwords (e.g., Marathi + English, Hinglish, Tanglish, etc.), exactly how people speak conversationally in everyday life across Bharat.
2. Freely use common conversational terms like 'deposit', 'landlord', 'rent agreement', 'flat', 'notice', 'salary', 'company', 'HR', 'full name', 'civil dispute'.
3. Avoid overly archaic, academic, or pure textbook Sanskritized vocabulary when common conversational terms are clearer and more relatable.
4. Keep the grammatical base in the user's primary regional language ({target_lang}).

Instruction:
1. First acknowledge their situation empathetically in 1 short sentence in {target_lang}.
{criminal_instruction}3. Then ask for the missing details clearly: {'; '.join(field_prompts)}.
Keep your answer concise (under 2-3 sentences). Do NOT invent legal notice text yet."""

    try:
        reply = call_llm(
            system_prompt=system_prompt,
            user_prompt="Generate the clarification response in the target language.",
            temperature=0.2
        )
        if reply:
            return reply
    except Exception:
        pass

    return "Aapka mudda samajh aa gaya. Formal notice taiyaar karne ke liye kripya yeh zaroori details batayein:\n" + "\n".join(f"- {p}" for p in field_prompts)


def assemble_legal_notice(domain: str, facts: Dict[str, Any]) -> str:
    kb = get_kb(domain)
    if not kb or "legal_notice_template" not in kb:
        return ""
    
    template = kb["legal_notice_template"]
    current_date = datetime.now().strftime("%d %B, %Y")
    
    # Format proof_status into clean legal prose instead of raw snake_case enum
    formatted_facts = dict(facts)
    raw_proof = str(formatted_facts.get("proof_status", ""))
    if raw_proof in PROOF_HUMAN_READABLE:
        formatted_facts["proof_status"] = PROOF_HUMAN_READABLE[raw_proof]
    elif "_" in raw_proof:
        formatted_facts["proof_status"] = raw_proof.replace("_", " ")

    # Fill in variables with safe fallbacks
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
    language_code: Optional[str] = None
) -> Dict[str, str]:
    """
    Implements Problem 2 Direction #4: 'Help them argue, for example by playing the other side so they can practise'.
    Simulates the stubborn Landlord or Employer HR pushing back, paired with a Tactical Legal Coach tip.
    """
    kb = get_kb(domain)
    target_lang = LANG_NAMES.get(language_code, "Hinglish / the user's language")
    counterparty_role = "Stubborn Landlord (Makaan-Maalik)" if domain == "rental_deposit" else "Defensive Company HR / Management"
    
    system_prompt = f"""You are running a Legal Negotiation Roleplay Simulator for an ordinary citizen in India.
Case Domain: {kb['domain_name'] if kb else domain}
Extracted Case Facts: {json.dumps(facts, ensure_ascii=False)}
Permissible Legal Grounds: {json.dumps(kb['permissible_statutes'] if kb else [], ensure_ascii=False)}

The user is practicing how to argue their case against the {counterparty_role}.
User's statement to the counterparty: "{user_argument}"

Respond STRICTLY in valid JSON with two keys:
{{
  "counterparty_reply": "In-character response from the {counterparty_role} in natural {target_lang} (1-2 realistic sentences pushing back with common excuses like 'paint kharab tha', 'agreement nahi hai', or 'client payment nahi aaya', or conceding if the user made a strong legal argument).",
  "coach_tip": "Tactical coaching feedback from NyayaMitra in {target_lang} (1-2 sentences rating the user's argument and telling them which exact fact or law—such as Section 73 Contract Act, normal wear & tear rule, or 15-day Legal Notice consequence—to use next)."
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
                "coach_tip": data.get("coach_tip", "Unhe yaad dilayein ki Section 73 Indian Contract Act ke tehat bina pakke bill ke paise rokna kanoonan galat hai.")
            }
    except Exception as e:
        print(f"Roleplay error: {e}")

    if domain == "rental_deposit":
        return {
            "counterparty_reply": "Dekho bhai, flat me painting aur cleaning ka kharcha toh katega hi, bina kaate deposit wapas nahi milega.",
            "coach_tip": "💡 **Coach Tip:** Landlord ko spasht bolein ki *normal wear and tear* tenant ki zimmedari nahi hoti, aur bina contractor bill ke deduction Section 73 Contract Act ke khilaf hai."
        }
    return {
        "counterparty_reply": "Dekhiye, abhi company ke paas client se funds nahi aaye hain, isliye aapka FnF settlement hold par hai.",
        "coach_tip": "💡 **Coach Tip:** HR ko bolein ki *client payment delay* ka bahana banakar earned salary rokna illegal hai, aur 15 din me payment na hone par aap Order 37 CPC aur Labour Commissioner me jayenge."
    }
