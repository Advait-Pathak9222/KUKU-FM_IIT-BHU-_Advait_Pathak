"""
Grounding Knowledge Base: Consumer Disputes & Defective Goods/Services
Covers e-commerce refunds, defective products, service deficiency (airlines, banking, telecom,
edtech/coaching, hospitals, builders, insurance), and unfair trade practices in India.
"""

CONSUMER_DISPUTE_KB = {
    "domain_id": "consumer_dispute",
    "domain_name": "Consumer Protection & Refund Dispute",
    "description": "Disputes involving defective goods, deficient services, e-commerce refund refusals, or unfair trade practices.",
    "jurisdiction": "India (Consumer Disputes Redressal Commission - CPA 2019)",

    "required_entities": {
        "consumer_name": {
            "type": "string",
            "description": "Full legal name of the consumer / buyer filing the notice",
            "clarification_prompt": "Aapka poora naam kya hai jo bill, invoice ya order par darj hai?"
        },
        "opposite_party_name": {
            "type": "string",
            "description": "Name of the company, brand, seller, e-commerce platform, or service provider",
            "clarification_prompt": "Jis company, seller ya service provider ke khilaf complaint hai, uska naam kya hai?"
        },
        "company_or_consumer_location": {
            "type": "string",
            "description": "City / location of the consumer or seller branch",
            "clarification_prompt": "Aap kis sheher (city) me rehte hain ya yeh transaction kahan hua?"
        },
        "product_or_service_details": {
            "type": "string",
            "description": "Description of the product bought or service availed (and order/invoice reference if any)",
            "clarification_prompt": "Aapne kaunsa product kharida tha ya kaunsi service li thi?"
        },
        "claim_amount": {
            "type": "number",
            "description": "Total amount paid or refund/compensation demanded (in INR)",
            "clarification_prompt": "Aapne kul kitne rupaye pay kiye the ya kitना refund/claim maang rahe hain?"
        },
        "transaction_date": {
            "type": "string",
            "description": "Date or month of purchase, booking, or deficiency",
            "clarification_prompt": "Yeh kharidari ya payment lagbhag kis taareekh ya mahine me hui thi?"
        },
        "nature_of_grievance": {
            "type": "string",
            "description": "Specific defect, service deficiency, non-delivery, or refusal of refund",
            "clarification_prompt": "Product ya service me kya kharabi aayi aur company ne kya jawaab diya?"
        },
        "proof_status": {
            "type": "string",
            "enum": ["tax_invoice_and_receipt", "online_order_and_payment_proof", "emails_or_support_tickets", "oral_or_cash_receipt"],
            "description": "Evidence held by the consumer (invoice, order ID, UPI/bank payment, support tickets)",
            "clarification_prompt": "Aapke paas kya proof hai? (Jaise bill/invoice, order ID, UPI/bank payment screenshot, ya customer care emails?)"
        }
    },

    "grounded_legal_standing": {
        "en": (
            "Under the Consumer Protection Act, 2019 and E-Commerce Rules, 2020:\n"
            "1. Delivering defective goods (Section 2(10)) or deficient services (Section 2(11)) or refusing a legitimate refund constitutes an Unfair Trade Practice (Section 2(47)).\n"
            "2. No seller or service provider can enforce arbitrary 'No Refund' policies when the product is defective or the service promised was not rendered.\n"
            "3. A consumer has the statutory right to seek a full refund with interest, replacement, and compensation for mental agony before the District Consumer Disputes Redressal Commission (Section 35) via the e-Daakhil portal (where no court fee is charged for claims up to Rs. 5 Lakhs)."
        ),
        "hi": (
            "Consumer Protection Act, 2019 ke mutabiq:\n"
            "1. Kharab product dena (Defect - Section 2(10)) ya adhuri/galat service dena (Deficiency in Service - Section 2(11)) aur refund se mana karna Unfair Trade Practice (Section 2(47)) hai.\n"
            "2. Agar product defective hai ya service nahi di gayi, toh koi bhi company 'No Refund Policy' ka bahana nahi bana sakti.\n"
            "3. Aap poora refund, byaj (interest) aur mansik pareshani ke muawze (compensation) ke haqdaar hain, aur e-Daakhil portal ke zariye District Consumer Commission (Section 35) me complaint file kar sakte hain."
        )
    },

    "permissible_statutes": [
        "Consumer Protection Act, 2019 (Section 2(10) - Defect, Section 2(11) - Deficiency in Service, Section 2(47) - Unfair Trade Practice)",
        "Consumer Protection Act, 2019 (Section 35 - Jurisdiction of District Consumer Disputes Redressal Commission)",
        "Consumer Protection (E-Commerce) Rules, 2020",
        "Indian Contract Act, 1872 (Section 73 - Compensation for Loss or Damage Caused by Breach of Contract)"
    ],

    "legal_notice_template": (
        "**FORMAL LEGAL NOTICE UNDER THE CONSUMER PROTECTION ACT, 2019**\n"
        "*(Sent via Registered Post A.D. / Speed Post / Registered Email)*\n\n"
        "**Date:** {current_date}\n\n"
        "**To:**\n"
        "**The Grievance Officer / Authorised Signatory**\n"
        "**{opposite_party_name}**\n"
        "Location / Jurisdiction: {company_or_consumer_location}\n\n"
        "**From (Consumer / Complainant):**\n"
        "**{consumer_name}**\n"
        "Resident of: {company_or_consumer_location}\n\n"
        "---\n\n"
        "**SUBJECT: LEGAL NOTICE FOR DEFICIENCY IN SERVICE / DEFECTIVE GOODS AND IMMEDIATE REFUND OF RS. {claim_amount}/- WITH COMPENSATION**\n\n"
        "Sir/Madam,\n\n"
        "Under instructions from and on behalf of **{consumer_name}**, I hereby serve upon you this Formal Legal Notice under the provisions of the Consumer Protection Act, 2019:\n\n"
        "1. **TRANSACTION DETAILS:** That I am a bona fide consumer within the meaning of Section 2(7) of the Consumer Protection Act, 2019, having purchased/availed **{product_or_service_details}** from **{opposite_party_name}** on/around **{transaction_date}**, evidenced by {proof_status}.\n\n"
        "2. **DEFECT / DEFICIENCY IN SERVICE:** That the said product/service suffered from grave defects and deficiency: **{nature_of_grievance}**. Despite repeated complaints and follow-ups, you have failed to rectify the issue or process the rightful refund.\n\n"
        "3. **STATUTORY VIOLATION:** That your conduct squarely amounts to 'Defect' under Section 2(10), 'Deficiency in Service' under Section 2(11), and 'Unfair Trade Practice' under Section 2(47) of the Consumer Protection Act, 2019, as well as breach of contract under Section 73 of the Indian Contract Act, 1872.\n\n"
        "4. **DEMAND (15 DAYS NOTICE):** You are hereby called upon to refund/settle the sum of **Rs. {claim_amount}/-** along with 18% p.a. interest within **fifteen (15) days** from the receipt of this notice.\n\n"
        "5. **CONSEQUENCE OF NON-COMPLIANCE:** Failing compliance within 15 days, I shall file a formal Consumer Complaint under Section 35 of the Consumer Protection Act, 2019 before the competent Consumer Disputes Redressal Commission seeking principal refund, penal interest, litigation costs, and compensation for mental harassment, entirely at your risk and cost.\n\n"
        "**Complainant / Sender:**\n"
        "**{consumer_name}**"
    )
}
