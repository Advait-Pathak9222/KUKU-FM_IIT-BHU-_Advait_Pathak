import json
import re
from typing import Optional
from .sarvam_client import call_llm
from ..models import TriageResult

TRIAGE_SYSTEM_PROMPT = """You are the Senior Legal Triage Classifier for NyayaMitra, an Indian AI Legal Assistance System.
Categorize the user's situation into ONE of five categories:
1. 'rental_deposit': Tenancy, flat/house/PG/hostel security deposit or advance refund disputes, arbitrary deductions (painting, cleaning, repairs, electricity), or landlord-tenant lease breaches.
2. 'unpaid_salary': Employment wages, CTC/fixed/variable pay arrears, Full & Final (FnF) settlement delays, withheld Relieving/Experience letters, PF/Gratuity issues, or unpaid worker wages.
3. 'consumer_dispute': Defective goods/products, e-commerce refund refusals, deficient services (airlines, telecom, banking, coaching/edtech, insurance, hospitals, builders), or unfair trade practices under the Consumer Protection Act, 2019.
4. 'money_recovery': Unpaid freelance/consultant/vendor/MSME invoices, dishonoured/bounced cheques (Section 138 NI Act), friendly loans via bank/UPI not returned, or commercial breach of contract.
5. 'out_of_scope': Criminal offenses (murder, rape, kidnapping, extortion, physical assault), domestic violence, dowry harassment, divorce/matrimonial disputes, child custody, or self-harm/suicide.

CRITICAL TRIAGE RULES:
- If the user has a civil/labour/consumer/recovery issue (Categories 1–4) and merely asks "Can I file a police FIR / 420 case against my landlord/boss/seller?", classify it into the appropriate civil category (1–4) with is_escalation: false so the AI lawyer can explain why civil recovery applies instead of a criminal FIR.
- If the situation genuinely involves physical violence, domestic abuse, dowry, sexual assault, divorce, child custody, or violent crime, you MUST classify it as 'out_of_scope' with is_escalation: true.

Return your response strictly as valid JSON:
{
  "domain": "rental_deposit" | "unpaid_salary" | "consumer_dispute" | "money_recovery" | "out_of_scope",
  "confidence": 0.0 to 1.0,
  "explanation": "Short justification",
  "is_escalation": true | false,
  "escalation_reason": "Specific safety or out-of-scope trigger if is_escalation is true, else null"
}"""

# Deterministic regex safeguard keywords for genuine violent/matrimonial/criminal escalation
ESCALATION_KEYWORDS = [
    r"\bdahej\b", r"\bdowry\b", r"\bmaar-peet\b", r"\bmarpeet\b", r"\bmaarpeet\b", r"\bmaar peet\b",
    r"\bdomestic violence\b", r"\bdomestic abuse\b", r"\bdivorce\b", r"\btalaq\b",
    r"\bchild custody\b", r"\brape\b", r"\bmolest",
    r"\bmurder\b", r"\bsuicide\b", r"\bphysical assault\b", r"\bthreatened to kill\b",
    r"\bjaan se maar", r"\bkidnap", r"\bextortion\b",
    # Devanagari equivalents (Hindi & Marathi)
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
                explanation="Deterministic safety trigger matched sensitive criminal, violent, or matrimonial keywords.",
                is_escalation=True,
                escalation_reason="Criminal, matrimonial, or domestic violence issue detected. Automated civil drafting is strictly prohibited."
            )
    return None

def classify_user_intent(message: str) -> TriageResult:
    # 1. Fast deterministic keyword guardrail check
    safety_override = check_deterministic_escalation(message)
    if safety_override:
        return safety_override

    # 2. Call universal LLM router
    try:
        content = call_llm(
            system_prompt=TRIAGE_SYSTEM_PROMPT,
            user_prompt=f"Classify this user statement:\n\"{message}\"",
            temperature=0.1
        )
        if content:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            json_str = match.group(0) if match else content
            data = json.loads(json_str)
            return TriageResult(**data)
    except Exception as e:
        print(f"Triage LLM error: {e}")

    # 3. Deterministic heuristic fallback if offline
    lower = message.lower()
    if any(w in lower for w in ["deposit", "landlord", "flat", "pg", "hostel", "kiraya", "makaan", "घरमालक", "डिपॉझिट", "भाडे", "किराया", "मकान"]):
        return TriageResult(domain="rental_deposit", confidence=0.8, explanation="Keyword match for tenancy/deposit.")
    elif any(w in lower for w in ["salary", "boss", "company", "ctc", "vetan", "hr", "relieving", "पगार", "वेतन", "कंपनी", "सैलरी"]):
        return TriageResult(domain="unpaid_salary", confidence=0.8, explanation="Keyword match for salary/employment.")
    elif any(w in lower for w in ["refund", "defective", "product", "order", "amazon", "flipkart", "warranty", "service", "consumer", "रिफंड", "खराब"]):
        return TriageResult(domain="consumer_dispute", confidence=0.8, explanation="Keyword match for consumer dispute.")
    elif any(w in lower for w in ["cheque", "bounce", "invoice", "freelance", "client", "loan", "udhaar", "चेक", "उधार", "बिल"]):
        return TriageResult(domain="money_recovery", confidence=0.8, explanation="Keyword match for money recovery/cheque bounce.")
    return TriageResult(domain="out_of_scope", confidence=0.5, explanation="Unrecognized domain.", is_escalation=True)
