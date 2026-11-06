import json
import re
from typing import Optional
from .sarvam_client import get_sarvam_client
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

# Deterministic regex safeguard keywords for immediate escalation
ESCALATION_KEYWORDS = [
    r"\bdahej\b", r"\bdowry\b", r"\bmaar-peet\b", r"\bmarpeet\b", r"\bdomestic violence\b",
    r"\bdivorce\b", r"\btalaq\b", r"\bchild custody\b", r"\bpolice complaint\b", r"\bfir\b",
    r"\brape\b", r"\bmurder\b", r"\bsuicide\b", r"\bphysical assault\b", r"\bthreatened to kill\b"
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

    # 2. Check for mock toggle or client availability
    from ..config import USE_MOCK_SARVAM
    client = get_sarvam_client()
    if USE_MOCK_SARVAM or not client:
        # Fallback keyword heuristic if API key is unavailable
        lower = message.lower()
        if any(w in lower for w in ["deposit", "landlord", "flat", "kiraya", "makaan"]):
            return TriageResult(domain="rental_deposit", confidence=0.8, explanation="Rule-based keyword match for tenancy.")
        elif any(w in lower for w in ["salary", "boss", "company", "vetan", "hr", "relieving"]):
            return TriageResult(domain="unpaid_salary", confidence=0.8, explanation="Rule-based keyword match for salary.")
        return TriageResult(domain="out_of_scope", confidence=0.5, explanation="Unrecognized domain.", is_escalation=True)

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify this user statement:\n\"{message}\""}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        # Clean markdown formatting if present
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n", "", content)
            content = re.sub(r"\n```$", "", content)
        data = json.loads(content)
        return TriageResult(**data)
    except Exception as e:
        # Fallback to rental_deposit or unpaid_salary if LLM JSON parse failed
        lower = message.lower()
        if "deposit" in lower or "landlord" in lower or "flat" in lower:
            return TriageResult(domain="rental_deposit", confidence=0.7, explanation=f"Fallback match. Error: {e}")
        elif "salary" in lower or "company" in lower or "resigned" in lower:
            return TriageResult(domain="unpaid_salary", confidence=0.7, explanation=f"Fallback match. Error: {e}")
        return TriageResult(domain="out_of_scope", confidence=0.5, explanation="Fallback out-of-scope.", is_escalation=True)
