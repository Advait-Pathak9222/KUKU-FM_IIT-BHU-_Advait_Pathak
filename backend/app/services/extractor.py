import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from .sarvam_client import get_sarvam_client
from ..kb import get_kb

EXTRACTION_SYSTEM_PROMPT = """You are a Legal Entity Extractor for an Indian legal assistance system.
Your job is to extract factual variables from the user's conversational message and update the existing case state.

Domain: {domain_name}
Target Schema & Descriptions:
{schema_description}

Current Extracted Facts:
{current_facts_json}

RULES:
1. ONLY extract information clearly present or implied in the user's message.
2. If a fact was previously null and is now provided, populate it.
3. If the user corrects a previous fact (e.g. changing amount or date), overwrite with the new value.
4. Do NOT hallucinate names, dates, or amounts not mentioned by the user. If a field is not mentioned, keep it as null.
5. For proof_status, select from the allowed enum values: {allowed_proof_enums}. If the user mentions having no written agreement or paying cash, classify as oral/informal.
6. Return your output STRICTLY as valid JSON matching the schema fields, with no markdown wrapping.
"""

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

    client = get_sarvam_client()
    if not client:
        # Simple heuristic fallback
        return current_facts

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"New user statement:\n\"{new_message}\""}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n", "", content)
            content = re.sub(r"\n```$", "", content)
        new_facts = json.loads(content)
        
        # Merge with current facts (only non-null updates)
        merged = dict(current_facts)
        for k, v in new_facts.items():
            if v is not None and v != "" and v != "null":
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
    client = get_sarvam_client()
    
    # Pick the top 1 or 2 most critical missing fields to avoid overwhelming the user
    primary_missing = missing_fields[:2]
    field_prompts = [kb["required_entities"][f]["clarification_prompt"] for f in primary_missing if f in kb["required_entities"]]
    
    # Identify target language
    target_lang = LANG_NAMES.get(language_code, "the user's exact regional language")
    
    if not client:
        return "Aapka mudda samajh aa gaya. Aage badhne ke liye kripya yeh batayein:\n" + "\n".join(f"- {p}" for p in field_prompts)

    system_prompt = f"""You are a helpful, empathetic legal assistant in India helping an ordinary citizen with their {kb['domain_name']}.
The user just communicated in: {target_lang}
User's message: "{user_message}"
Currently extracted facts: {json.dumps(facts, ensure_ascii=False)}

We still need to know:
{", ".join(primary_missing)}

CRITICAL LANGUAGE REQUIREMENT:
You MUST respond entirely in {target_lang}.
If the user spoke in Marathi (मराठी), your response MUST be in natural, clear Marathi (मराठी).
If the user spoke in Tamil, Telugu, Bengali, Gujarati, Kannada, or Hindi, respond in that EXACT regional language.
Do NOT default to English unless the user spoke in English.

Instruction:
1. First acknowledge their situation empathetically in 1 short sentence in {target_lang}.
2. If they asked to arrest someone under IPC 420 for unpaid salary or civil rent issue, gently clarify in {target_lang} that this is a civil/labour matter first.
3. Then ask for the missing details clearly in {target_lang}: {'; '.join(field_prompts)}.
Keep your answer concise (under 2-3 sentences). Do NOT invent legal notice text yet."""

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate the clarification response in the target language."}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Aapka mudda samajh aa gaya. Formal notice taiyaar karne ke liye kripya yeh zaroori details batayein:\n" + "\n".join(f"- {p}" for p in field_prompts)

def assemble_legal_notice(domain: str, facts: Dict[str, Any]) -> str:
    kb = get_kb(domain)
    if not kb or "legal_notice_template" not in kb:
        return ""
    
    template = kb["legal_notice_template"]
    current_date = datetime.now().strftime("%d %B, %Y")
    
    # Fill in variables with safe fallbacks
    slots = {
        "current_date": current_date,
        **{k: facts.get(k, f"[{k.replace('_', ' ').upper()}]") for k in kb["required_entities"]}
    }
    
    try:
        draft = template.format(**slots)
        return draft
    except KeyError as e:
        # In case a template variable is missing
        return template
