import json
import re
from typing import Optional
from .sarvam_client import call_llm
from ..models import TriageResult

TRIAGE_SYSTEM_PROMPT = """You are a Legal Triage Classifier for an Indian legal assistance system.
Your job is to categorize the user's situation into ONE of three categories:
1. 'rental_deposit': Disputes where a landlord refuses to return a security deposit or makes arbitrary deductions (painting, repairs, etc.).
2. 'unpaid_salary': Disputes where an employer/company has withheld earned salary, FnF settlement, or wages.
3. 'out_of_scope': Situations involving criminal offenses, physical violence, domestic harassment, dowry, divorce, child custody, police complaints, suicide/bodily harm, or cyber crimes.

CRITICAL SAFETY RULES:
- If the user mentions physical assault, domestic violence, dowry, child custody, or divorce, you MUST classify it as 'out_of_scope' with is_escalation: true.
- Do NOT classify criminal matters as civil.

Return your response strictly as valid JSON with no markdown wrapping:
{
  "domain": "rental_deposit" | "unpaid_salary" | "out_of_scope",
  "confidence": 0.0 to 1.0,
  "explanation": "Short justification",
  "is_escalation": true | false,
  "escalation_reason": "Specific safety or out-of-scope trigger if is_escalation is true, else null"
}"""

# Deterministic regex safeguard keywords for immediate escalation (Roman + Devanagari Hindi/Marathi)
ESCALATION_KEYWORDS = [
    r"\bdahej\b", r"\bdowry\b", r"\bmaar-peet\b", r"\bmarpeet\b", r"\bmaarpeet\b", r"\bmaar peet\b",
    r"\bdomestic violence\b", r"\bdomestic abuse\b", r"\bdivorce\b", r"\btalaq\b",
    r"\bchild custody\b", r"\bpolice complaint\b", r"\bfir\b", r"\brape\b", r"\bmolest",
    r"\bmurder\b", r"\bsuicide\b", r"\bphysical assault\b", r"\bthreatened to kill\b",
    r"\bjaan se maar", r"\bkidnap", r"\bextortion\b",
    # Devanagari equivalents (Hindi & Marathi) from Saaras STT transcripts
    r"दहेज", r"हुंडा", r"मारपीट", r"मारहाण", r"घरेलू हिंसा", r"कौटुंबिक हिंसाचार",
    r"तलाक", r"घटस्फोट", r"आत्महत्या", r"हत्या", r"बलात्कार", r"जीवे मारण्याची", r"जान से मारने"
]

def check_deterministic_escalation(text: str) -> Optional[TriageResult]:
    lower_text = text.lower()
    for pattern in ESCALATION_KEYWORDS:
        if re.search(pattern, lower_text):
            return TriageResult(
                domain="out_of_scope",
                confidence=1.0,
                explanation="Deterministic safety trigger matched sensitive out-of-scope or criminal keywords.",
                is_escalation=True,
                escalation_reason="Criminal, matrimonial, or domestic violence issue detected. Automated civil drafting is strictly prohibited."
            )
    return None

def classify_user_intent(message: str) -> TriageResult:
    # 1. Fast deterministic keyword guardrail check
    safety_override = check_deterministic_escalation(message)
    if safety_override:
        return safety_override

    # 2. Call universal LLM router (or fallback if mock/offline)
    try:
        content = call_llm(
            system_prompt=TRIAGE_SYSTEM_PROMPT,
            user_prompt=f"Classify this user statement:\n\"{message}\"",
            temperature=0.1
        )
        if content:
            # Extract JSON object resiliently even if wrapped in markdown or prose
            match = re.search(r"\{.*\}", content, re.DOTALL)
            json_str = match.group(0) if match else content
            data = json.loads(json_str)
            return TriageResult(**data)
    except Exception as e:
        print(f"Triage LLM error: {e}")

    # 3. Deterministic heuristic fallback if mock mode or LLM parse error
    lower = message.lower()
    if any(w in lower for w in ["deposit", "landlord", "flat", "kiraya", "makaan", "घरमालक", "डिपॉझिट", "भाडे", "किराया", "मकान"]):
        return TriageResult(domain="rental_deposit", confidence=0.8, explanation="Rule-based keyword match for tenancy.")
    elif any(w in lower for w in ["salary", "boss", "company", "vetan", "hr", "relieving", "पगार", "वेतन", "कंपनी"]):
        return TriageResult(domain="unpaid_salary", confidence=0.8, explanation="Rule-based keyword match for salary.")
    return TriageResult(domain="out_of_scope", confidence=0.5, explanation="Unrecognized domain.", is_escalation=True)
