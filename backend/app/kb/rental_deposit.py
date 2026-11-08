"""
Grounding Knowledge Base: Rental Deposit Disputes (Tenancy)
Defines required entities, plain-language legal standing, permissible statutes,
and the deterministic Legal Notice template.
"""

RENTAL_DEPOSIT_KB = {
    "domain_id": "rental_deposit",
    "domain_name": "Tenancy Security Deposit Dispute",
    "description": "Disputes regarding landlords unlawfully withholding or making unjustified deductions from tenant security deposits.",
    "jurisdiction": "India (Civil Tenancy)",
    
    "required_entities": {
        "tenant_name": {
            "type": "string",
            "description": "Full legal name of the tenant demanding the refund",
            "clarification_prompt": "Aapka poora naam kya hai jo rent agreement ya payment receipt par darj hai?"
        },
        "landlord_name": {
            "type": "string",
            "description": "Full name of the landlord / property owner",
            "clarification_prompt": "Makaan-maalik (landlord) ka poora naam kya hai?"
        },
        "property_address": {
            "type": "string",
            "description": "Address of rented premises (locality and city minimum)",
            "clarification_prompt": "Kiraye ka makaan ya flat kis sheher aur locality me sthit tha?"
        },
        "deposit_amount_paid": {
            "type": "number",
            "description": "Total security deposit originally paid (in INR)",
            "clarification_prompt": "Aapne tenancy ke shuruat me kul kitna security deposit diya tha (rupaye me)?"
        },
        "amount_withheld": {
            "type": "number",
            "description": "Amount the landlord is refusing to return (in INR)",
            "clarification_prompt": "Makaan-maalik ne kitne rupaye wapas karne se mana kiya hai ya kaat liye hain?"
        },
        "vacating_date": {
            "type": "string",
            "description": "Date or approximate month when premises were vacated and keys handed over",
            "clarification_prompt": "Aapne premises kis taareekh ko khali kiya aur keys handover ki?"
        },
        "landlord_deduction_reason": {
            "type": "string",
            "description": "Reason claimed by landlord for deduction (e.g. painting, deep cleaning, false damages)",
            "clarification_prompt": "Makaan-maalik paise kaatne ka kya kaaran bata raha hai? (Jaise painting, safaai, ya bina kisi kaaran?)"
        },
        "proof_status": {
            "type": "string",
            "enum": ["agreement_and_receipts", "online_bank_transfer", "whatsapp_chats", "oral_agreement_only"],
            "description": "Evidence held by the tenant",
            "clarification_prompt": "Aapke paas kya saboot hain? (Jaise Rent Agreement, bank transfer receipt, ya WhatsApp chats?)"
        }
    },

    "grounded_legal_standing": {
        "en": (
            "Under Indian tenancy guidelines and the Indian Contract Act, 1872:\n"
            "1. A security deposit is the tenant's property held in trust by the landlord to safeguard against unpaid rent or genuine physical damage.\n"
            "2. Normal wear and tear (such as customary paint aging and normal usage) cannot be arbitrarily deducted from your deposit without an express contractual agreement and verified repair bills.\n"
            "3. Once vacant possession and keys are handed over, the landlord is legally obligated to settle accounts and refund the remaining deposit within a reasonable cure period (typically 15 to 30 days).\n"
            "4. Arbitrary retention without legitimate breakdown constitutes breach of trust and unlawful retention of funds."
        ),
        "hi": (
            "Bhartiya kanoon aur tenancy niyamon ke mutabiq:\n"
            "1. Security deposit aapki amaanat hoti hai jo makaan-maalik ke paas sirf genuine damages ya pending bills ke liye rakhi jaati hai.\n"
            "2. Normal wear and tear (jaise samanya deewar ka paint purana hona, regular istemaal) ka kharcha landlord bina written agreement ke aapke deposit se nahi kaat sakta.\n"
            "3. Chaabi saupne aur flat khali karne ke baad, makaan-maalik ko 15 se 30 din me hisaab karke bacha hua deposit lautaana anivarya hai.\n"
            "4. Bina kisi pakke bill ya estimation ke manmaane paise kaatna kanooni taur par anuchit hai."
        )
    },

    "permissible_statutes": [
        "Indian Contract Act, 1872 (Sections 70, 73 & 74 - Breach of Contract, Restitution & Unlawful Penalty/Forfeiture)",
        "Transfer of Property Act, 1882 (Section 108(m) - Reasonable Wear and Tear Exception; Section 106 - Lease Notice)",
        "Model Tenancy Act, 2021 (Sections 11, 15 & 20 - Security Deposit Refund & Protection of Essential Services) / State Rent Control Acts",
        "Code of Civil Procedure, 1908 (Order 37 - Summary Suit for Recovery; Section 20 - Jurisdiction; Section 34 - Interest)",
        "Bharatiya Sakshya Adhiniyam, 2023 (Section 63 - Admissibility of Electronic Records / WhatsApp & UPI Proof)",
        "Limitation Act, 1963 (3-Year Limitation Period for Recovery) & General Clauses Act, 1897 (Section 27 - Presumption of Service)"
    ],

    "legal_notice_template": (
        "**FORMAL LEGAL NOTICE OF DEMAND**\n"
        "*(Sent via Speed Post / Registered Email / WhatsApp)*\n\n"
        "**Date:** {current_date}\n\n"
        "**To:**\n"
        "**{landlord_name}**\n"
        "Address: {property_address}\n\n"
        "**From (Sender):**\n"
        "**{tenant_name}**\n"
        "Former Tenant of: {property_address}\n\n"
        "---\n\n"
        "**SUBJECT: FORMAL NOTICE FOR IMMEDIATE REFUND OF WITHHELD SECURITY DEPOSIT AMOUNTING TO RS. {amount_withheld}/- ALONG WITH INTEREST**\n\n"
        "Sir/Madam,\n\n"
        "Under instructions and on behalf of myself, **{tenant_name}**, I hereby serve upon you this Formal Notice of Demand regarding the illegal retention of my security deposit:\n\n"
        "1. **TENANCY & SECURITY DEPOSIT:** That I was a lawful tenant at **{property_address}**. At the inception of the tenancy, a total refundable security deposit of **Rs. {deposit_amount_paid}/-** was remitted to you via {proof_status}.\n\n"
        "2. **VACATION & HANDOVER:** That I lawfully vacated the tenancy premises and handed over peaceful, vacant possession along with keys on **{vacating_date}**. The premises were handed over in good order, reasonable wear and tear excepted.\n\n"
        "3. **UNLAWFUL WITHHOLDING:** That despite repeated verbal and written requests, you have failed and neglected to refund the balance sum of **Rs. {amount_withheld}/-**, citing \"{landlord_deduction_reason}\", without providing any verified inspection report, legitimate contractor invoices, or legal basis for such deduction.\n\n"
        "4. **LEGAL LIABILITY:** That the security deposit is held by the landlord in a fiduciary capacity and cannot be appropriated for routine maintenance or normal wear and tear. Your failure to return the money constitutes a willful breach of contract under Section 73 of the Indian Contract Act, 1872, and unjust enrichment.\n\n"
        "5. **DEMAND (15 DAYS NOTICE):** You are hereby called upon to refund the full withheld sum of **Rs. {amount_withheld}/-** directly into my bank account within **fifteen (15) days** of receipt of this notice.\n\n"
        "6. **CONSEQUENCE OF NON-COMPLIANCE:** Take notice that in default of compliance within the stipulated 15 days, I shall be constrained to institute appropriate civil proceedings against you, including a Summary Suit for Recovery under Order 37 of the CPC with 18% per annum penal interest, and approach the competent Rent Authority, holding you fully liable for all associated costs and consequences.\n\n"
        "**Sender:**\n"
        "**{tenant_name}**"
    )
}
