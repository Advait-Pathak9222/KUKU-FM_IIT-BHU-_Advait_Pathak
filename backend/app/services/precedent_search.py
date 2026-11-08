"""
Calibrated Severity Gate & Live IndianKanoon Web Precedent Search Agent.
Replicates how an Indian litigation lawyer decides WHEN a case is severe/complex enough
to warrant researching similar Supreme Court / High Court precedents on IndianKanoon,
executes live web browsing, and synthesizes applicable case law.
"""

import html
import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
import requests
from .sarvam_client import call_llm

# Calibrated threshold (0.00 to 1.00): routine/simple cases (< 0.60) skip web search;
# severe, high-value, or doctrinally complex cases (>= 0.60) trigger live precedent browsing.
SEVERITY_THRESHOLD = 0.60

# Curated Landmark Indian Supreme Court & High Court Authorities (Grounded Legal Anchors)
LANDMARK_PRECEDENT_ANCHORS = {
    "rental_deposit": [
        {
            "title": "Fateh Chand vs. Balkishan Dass (1964 AIR 1495)",
            "court": "Supreme Court of India (Constitution Bench)",
            "url": "https://indiankanoon.org/doc/1486938/",
            "snippet": "Under Section 74 of the Indian Contract Act, 1872, a party cannot forfeit a deposit or impose a penalty without proving actual legal loss or damage suffered.",
            "source_type": "Landmark SC Precedent"
        },
        {
            "title": "Kailash Nath Associates vs. Delhi Development Authority (2015) 4 SCC 136",
            "court": "Supreme Court of India",
            "url": "https://indiankanoon.org/doc/90386702/",
            "snippet": "Proof of actual damage or loss is a sine qua non under Section 73 & 74 ICA; arbitrary retention or deduction of security money without proved loss is unlawful.",
            "source_type": "Landmark SC Precedent"
        }
    ],
    "unpaid_salary": [
        {
            "title": "Central Inland Water Transport Corp. Ltd. vs. Brojo Nath Ganguly (1986 AIR 1571)",
            "court": "Supreme Court of India",
            "url": "https://indiankanoon.org/doc/477313/",
            "snippet": "Unconscionable employment terms or unilateral withholding of earned benefits/service certificates due to unequal bargaining power are void under Section 23 of the Contract Act.",
            "source_type": "Landmark SC Precedent"
        },
        {
            "title": "Mobilox Innovations Pvt. Ltd. vs. Kirusa Software Pvt. Ltd. (2018) 1 SCC 353",
            "court": "Supreme Court of India",
            "url": "https://indiankanoon.org/doc/44365206/",
            "snippet": "Operational debt including unpaid employment/service dues triggers statutory recovery under Section 8 & 9 of the Insolvency and Bankruptcy Code, 2016 unless a pre-existing genuine dispute exists.",
            "source_type": "Landmark SC Precedent"
        }
    ],
    "consumer_dispute": [
        {
            "title": "Pioneer Urban Land & Infrastructure Ltd. vs. Govindan Raghavan (2019) 5 SCC 725",
            "court": "Supreme Court of India",
            "url": "https://indiankanoon.org/doc/52586442/",
            "snippet": "One-sided, unfair clauses in standard-form consumer contracts (such as arbitrary forfeiture or 'No Refund' policies despite deficiency in service) constitute Unfair Trade Practice under the Consumer Protection Act.",
            "source_type": "Landmark SC Precedent"
        },
        {
            "title": "Laxmi Engineering Works vs. P.S.G. Industrial Institute (1995 AIR 1428)",
            "court": "Supreme Court of India",
            "url": "https://indiankanoon.org/doc/1722669/",
            "snippet": "Goods or equipment purchased by an individual for self-employment to earn their livelihood fall squarely within the definition of 'Consumer' under the Consumer Protection Act.",
            "source_type": "Landmark SC Precedent"
        }
    ],
    "money_recovery": [
        {
            "title": "Rangappa vs. Sri Mohan (2010) 11 SCC 441",
            "court": "Supreme Court of India (3-Judge Bench)",
            "url": "https://indiankanoon.org/doc/1522881/",
            "snippet": "Once execution/signature on a dishonoured cheque is admitted, Section 139 of the Negotiable Instruments Act mandates a statutory presumption that the cheque was issued for a legally enforceable debt or liability.",
            "source_type": "Landmark SC Precedent"
        },
        {
            "title": "IDBI Trusteeship Services Ltd. vs. Hubtown Ltd. (2017) 1 SCC 568",
            "court": "Supreme Court of India",
            "url": "https://indiankanoon.org/doc/194025464/",
            "snippet": "In a Summary Suit under Order XXXVII of the CPC, where the debt is backed by written contract, invoice, or acknowledged liability, the defendant must deposit security or show substantial defense to obtain leave to defend.",
            "source_type": "Landmark SC Precedent"
        }
    ]
}

# Keywords signaling doctrinal complexity or aggravated conduct
SEVERE_CONDUCT_PATTERNS = [
    (r"\b(relieving|experience letter|service certificate|fnf|full and final|bond|penalty|forfeit|pf|gratuity|tds|esop|stocks|ctc)\b", 0.30, "Complex employment/CTC/FnF or withheld service document issue"),
    (r"\b(unregistered|whatsapp|oral|no agreement|electricity|water|lock|evict|gst bill|wear and tear|geyser|painting)\b", 0.30, "Contested evidentiary/unregistered lease or arbitrary deduction issue"),
    (r"\b(cheque|bounce|138|return memo|insufficient funds|msme|udyam|insolvency|ibc)\b", 0.35, "Statutory negotiable instrument (Sec 138 NI Act) or commercial default"),
    (r"\b(no refund|defective|warranty|harassment|compensation|livelihood|e-daakhil)\b", 0.25, "Contested consumer deficiency or unfair trade practice"),
    (r"(रिलीविंग|बॉन्ड|सीटीसी|चेक बाउंस|बिजली|पानी|बिना बिल|रिफंड|गारंटी)", 0.30, "Aggravated factual or statutory dispute"),
]

EXPLICIT_PRECEDENT_PATTERNS = [
    r"\b(precedent|case law|judgment|judgement|supreme court|high court|similar case|court order|citation|ruling)\b",
    r"(सुप्रीम कोर्ट|हाई कोर्ट|फैसला|जजमेंट|केस लॉ|पुराने केस|उदाहरण)"
]


def _extract_claim_amount(facts: Dict[str, Any]) -> float:
    for key in ("total_amount_owed", "amount_withheld", "claim_amount", "principal_amount_owed", "deposit_amount_paid"):
        val = facts.get(key)
        if val is not None:
            try:
                cleaned = re.sub(r"[^\d\.]", "", str(val))
                if cleaned:
                    return float(cleaned)
            except Exception:
                pass
    return 0.0


def evaluate_case_severity(
    domain: str,
    user_msg: str,
    facts: Dict[str, Any],
    is_complete: bool
) -> Dict[str, Any]:
    """
    Calibrates whether the current case & turn warrant live web precedent research.
    Returns severity_score (0.0 to 1.0), threshold (0.60), reasons, and trigger decision.
    """
    public_facts = {k: v for k, v in facts.items() if not str(k).startswith("_")}
    combined_text = f"{user_msg} {facts.get('_case_nuances', '')} {facts.get('_calculation_note', '')} {json.dumps(public_facts, ensure_ascii=False)}".lower()

    score = 0.0
    reasons: List[str] = []

    # 1. Explicit user request for case law / precedents -> Immediate trigger
    explicit_request = any(re.search(p, combined_text) for p in EXPLICIT_PRECEDENT_PATTERNS)
    if explicit_request:
        score += 0.65
        reasons.append("Client explicitly requested court precedents / case law")

    # 2. Monetary Quantum Calibration
    amount = _extract_claim_amount(public_facts)
    if amount >= 150000:
        score += 0.35
        reasons.append(f"High monetary stakes (₹{int(amount):,} ≥ ₹1,50,000)")
    elif amount >= 75000:
        score += 0.25
        reasons.append(f"Substantial monetary claim (₹{int(amount):,})")
    elif amount >= 25000:
        score += 0.15
        reasons.append(f"Moderate monetary claim (₹{int(amount):,})")
    elif amount > 0:
        score += 0.05

    # 3. Aggravated Conduct / Doctrinal Complexity Calibration
    matched_conduct = False
    for pattern, weight, desc in SEVERE_CONDUCT_PATTERNS:
        if re.search(pattern, combined_text) and not matched_conduct:
            score += weight
            reasons.append(desc)
            matched_conduct = True

    # 4. Multi-component Financial Calculation present
    if facts.get("_calculation_note") and "Exact Formula:" in str(facts.get("_calculation_note")):
        score += 0.15
        reasons.append("Multi-component financial/pro-rata calculation required")

    # 5. Readiness & Sufficiency Gate:
    # Do not waste time web-searching on Turn 1 if we barely know any facts (< 3 facts) unless explicitly asked!
    if is_complete and score >= 0.45:
        score += 0.20
        reasons.append("All core case facts verified — ready for precedent-backed Legal Notice")

    final_score = round(min(1.0, score), 2)
    enough_context = (len(public_facts) >= 3) or is_complete or explicit_request
    already_searched = bool(facts.get("_precedent_search", {}).get("triggered"))

    # Trigger search if score >= threshold AND we have enough context AND either not yet searched or explicitly asked
    should_trigger = (
        final_score >= SEVERITY_THRESHOLD
        and enough_context
        and (not already_searched or explicit_request or (is_complete and not facts.get("_precedent_search", {}).get("searched_on_complete")))
    )

    if not reasons:
        reasons.append("Routine fact-gathering turn (simple claim)")

    return {
        "severity_score": final_score,
        "threshold": SEVERITY_THRESHOLD,
        "is_severe": final_score >= SEVERITY_THRESHOLD,
        "should_trigger_search": should_trigger,
        "reasons": reasons
    }


def _build_indiankanoon_query(domain: str, facts: Dict[str, Any], user_msg: str) -> str:
    """Constructs a high-precision, phrase-locked IndianKanoon judgment query for the specific dispute."""
    combined = f"{user_msg} {facts.get('_case_nuances', '')}".lower()

    if domain == "unpaid_salary":
        if "relieving" in combined or "experience" in combined or "bond" in combined:
            return '"salary arrears" "relieving letter" doctypes:judgments'
        return '"unpaid salary" "recovery" "employment" doctypes:judgments'

    if domain == "rental_deposit":
        if "painting" in combined or "wear and tear" in combined or "deduct" in combined or "kaat" in combined:
            return '"security deposit" "wear and tear" tenant doctypes:judgments'
        return '"security deposit" "refund" landlord tenant doctypes:judgments'

    if domain == "money_recovery":
        if "cheque" in combined or "bounce" in combined or "138" in combined:
            return '"section 138" "dishonour of cheque" "presumption" doctypes:judgments'
        return '"order 37" "summary suit" "recovery" invoice doctypes:judgments'

    if domain == "consumer_dispute":
        return '"deficiency in service" "refund" "consumer" doctypes:judgments'

    return '"legal notice" "recovery" "breach of contract" doctypes:judgments'


def browse_indiankanoon_precedents(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Executes a live HTTP web search against IndianKanoon.org (`doctypes:judgments`)
    and extracts real Supreme Court / High Court / Tribunal case titles, courts, URLs, and holdings.
    """
    encoded_q = quote_plus(query)
    url = f"https://indiankanoon.org/search/?formInput={encoded_q}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    results: List[Dict[str, str]] = []
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            pattern = re.compile(
                r'result_title">.*?<a href="([^"]+)"[^>]*>(.*?)</a>.*?<div class="headline">(.*?)</div>.*?<span class="docsource">(.*?)</span>',
                re.DOTALL
            )
            for match in pattern.finditer(resp.text):
                href, raw_title, raw_headline, raw_source = match.groups()
                title = html.unescape(re.sub(r"<[^>]+>", "", raw_title)).strip()
                snippet = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw_headline))).strip()
                court = html.unescape(re.sub(r"<[^>]+>", "", raw_source)).strip()
                doc_id_match = re.search(r"/doc(?:fragment)?/(\d+)/", href)
                clean_url = f"https://indiankanoon.org/doc/{doc_id_match.group(1)}/" if doc_id_match else f"https://indiankanoon.org{href}"

                # Skip raw statutory Act pages if any slipped through
                if " - Act" in court:
                    continue

                results.append({
                    "title": title,
                    "court": court,
                    "url": clean_url,
                    "snippet": snippet[:240] + ("..." if len(snippet) > 240 else ""),
                    "source_type": "Live IndianKanoon Web Search"
                })
                if len(results) >= max_results:
                    break
    except Exception as e:
        print(f"Live IndianKanoon web search error: {e}")

    return results


def run_calibrated_precedent_agent(
    domain: str,
    user_msg: str,
    facts: Dict[str, Any],
    is_complete: bool
) -> Dict[str, Any]:
    """
    Main entry point for the Calibrated Legal Precedent Web Agent:
    1. Evaluates severity score against SEVERITY_THRESHOLD (0.60).
    2. If below threshold (or already searched without new trigger), skips web search (or returns cached results).
    3. If >= threshold, browses IndianKanoon live + attaches landmark Supreme Court precedent anchors,
       and synthesizes a brief Lawyer Precedent Note.
    """
    eval_res = evaluate_case_severity(domain, user_msg, facts, is_complete)
    existing_search = facts.get("_precedent_search")

    if not eval_res["should_trigger_search"]:
        if existing_search and existing_search.get("triggered"):
            # Preserve previously retrieved precedents while updating current severity score
            updated = dict(existing_search)
            updated["severity_score"] = max(existing_search.get("severity_score", 0.0), eval_res["severity_score"])
            updated["just_searched_this_turn"] = False
            return updated
        return {
            "triggered": False,
            "just_searched_this_turn": False,
            "severity_score": eval_res["severity_score"],
            "threshold": eval_res["threshold"],
            "is_severe": eval_res["is_severe"],
            "reasons": eval_res["reasons"],
            "search_query": None,
            "precedents": [],
            "precedent_synthesis": None
        }

    # Build targeted query & browse IndianKanoon live
    search_query = _build_indiankanoon_query(domain, facts, user_msg)
    live_cases = browse_indiankanoon_precedents(search_query, max_results=2)
    landmark_cases = LANDMARK_PRECEDENT_ANCHORS.get(domain, [])[:2]

    combined_precedents = landmark_cases + live_cases

    # Synthesize a crisp 2-line lawyer application note linking the precedents to the client's facts
    public_facts = {k: v for k, v in facts.items() if not str(k).startswith("_")}
    synthesis_note = None
    try:
        synth_prompt = f"""You are a Senior Indian Litigation Researcher.
Client's Case Facts: {json.dumps(public_facts, ensure_ascii=False)}
Case Nuances: {facts.get('_case_nuances', 'None')}
Retrieved Court Precedents (Landmark SC + Live IndianKanoon Web Search):
{json.dumps(combined_precedents, ensure_ascii=False, indent=2)}

Write a concise 2-sentence 'Precedent Application Note' explaining how the most relevant 1-2 judgments from the list above directly support this client's claim and strengthen their Legal Notice. ONLY cite case names from the list above."""
        synthesis_note = call_llm(
            system_prompt=synth_prompt,
            user_prompt="Synthesize the precedent application note in 2 crisp sentences.",
            temperature=0.15
        )
    except Exception as e:
        print(f"Precedent synthesis error: {e}")

    if not synthesis_note and combined_precedents:
        top = combined_precedents[0]
        synthesis_note = f"Supported by {top['title']} ({top['court']}): {top['snippet']}"

    return {
        "triggered": True,
        "just_searched_this_turn": True,
        "searched_on_complete": is_complete,
        "severity_score": eval_res["severity_score"],
        "threshold": eval_res["threshold"],
        "is_severe": True,
        "reasons": eval_res["reasons"],
        "search_query": search_query,
        "precedents": combined_precedents,
        "precedent_synthesis": synthesis_note
    }
