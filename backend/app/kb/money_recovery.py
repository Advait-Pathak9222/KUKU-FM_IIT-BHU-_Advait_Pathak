"""
Grounding Knowledge Base: Money Recovery, Freelance/Vendor Invoices & Cheque Bounce
Covers unpaid freelance/vendor/MSME dues, friendly loans, contract breaches, and cheque dishonour (Sec 138 NI Act).
"""

MONEY_RECOVERY_KB = {
    "domain_id": "money_recovery",
    "domain_name": "Money Recovery, Unpaid Invoices & Cheque Bounce",
    "description": "Disputes involving unpaid freelance/vendor invoices, friendly loans, breached commercial agreements, or dishonoured cheques.",
    "jurisdiction": "India (Civil Courts - Order 37 CPC / NI Act Sec 138 / MSMED Act)",

    "required_entities": {
        "creditor_name": {
            "type": "string",
            "description": "Full legal name of the person, freelancer, or business demanding the money",
            "clarification_prompt": "Aapka poora naam (ya aapki firm/business ka naam) kya hai?"
        },
        "debtor_name": {
            "type": "string",
            "description": "Full name of the person, client, or company that owes the money",
            "clarification_prompt": "Jis vyakti ya company se paise lene hain, unka poora naam kya hai?"
        },
        "jurisdiction_city": {
            "type": "string",
            "description": "City / location where the transaction took place or where the party resides",
            "clarification_prompt": "Yeh transaction kis sheher (city) me hua ya woh party kahan rehti hai?"
        },
        "transaction_nature": {
            "type": "string",
            "description": "Nature of transaction (e.g., freelance work, vendor invoice, friendly loan, advance payment, cheque bounce)",
            "clarification_prompt": "Yeh paisa kis kaam ya transaction ka hai? (Jaise freelance work, business bill, udhaar/loan, ya cheque bounce?)"
        },
        "principal_amount_owed": {
            "type": "number",
            "description": "Total principal amount remaining unpaid (in INR)",
            "clarification_prompt": "Unpar aapka kul kitna paisa (rupaye me) baaki hai?"
        },
        "default_timeline": {
            "type": "string",
            "description": "Date or period when payment was due or when the cheque bounced",
            "clarification_prompt": "Yeh payment kab se pending hai (ya cheque kis taareekh ko bounce hua)?"
        },
        "default_reason_or_excuse": {
            "type": "string",
            "description": "Excuse given by debtor, or reason for cheque dishonour (e.g., Funds Insufficient, avoiding calls)",
            "clarification_prompt": "Saamne wali party paise na dene ka kya bahana bana rahi hai (ya bank return memo me kya reason aaya)?"
        },
        "proof_status": {
            "type": "string",
            "enum": ["written_contract_or_invoice", "bounced_cheque_and_memo", "upi_or_bank_transfer_proof", "whatsapp_or_email_admission"],
            "description": "Evidence of the debt or transaction",
            "clarification_prompt": "Aapke paas kya saboot hai? (Jaise Invoice/Agreement, Bounced Cheque + Bank Memo, UPI/Bank statement, ya WhatsApp chat?)"
        }
    },

    "grounded_legal_standing": {
        "en": (
            "Under Indian Civil & Commercial Recovery Laws:\n"
            "1. Unpaid invoices, freelance dues, or documented loans constitute an enforceable debt. Under Section 73 of the Indian Contract Act, 1872, the defaulting party is liable to pay the principal sum along with interest.\n"
            "2. You can file a fast-track Summary Suit under Order 37 of the Code of Civil Procedure, 1908 based on invoices, written contracts, bank transfers, or acknowledged debt.\n"
            "3. If a cheque has been dishonoured, issuing a statutory Legal Notice within 30 days of the bank return memo giving 15 days to pay is mandatory to initiate criminal prosecution under Section 138 of the Negotiable Instruments Act, 1881.\n"
            "4. If you are a registered MSME vendor, the buyer is statutorily liable to pay compound interest at 3x the RBI bank rate under Sections 15 & 16 of the MSMED Act, 2006."
        ),
        "hi": (
            "Bhartiya recovery aur commercial kanoon ke mutabiq:\n"
            "1. Kiye gaye kaam ka bill, freelance payment, ya bank transfer se diya gaya paisa rokna Indian Contract Act ke Section 73 ke tehat contract ka ullanghan hai.\n"
            "2. Invoice, agreement, ya लिखित/WhatsApp acknowledgement ke aadhar par aap Order 37 CPC ke tehat fast-track Summary Recovery Suit file kar sakte hain.\n"
            "3. Agar cheque bounce hua hai, toh bank return memo ke 30 din ke andar 15-day Legal Notice bhejna Section 138 Negotiable Instruments Act ke tehat criminal case ke liye anivarya hai."
        )
    },

    "permissible_statutes": [
        "Indian Contract Act, 1872 (Sections 70 & 73 - Breach of Contract & Quantum Meruit / Restitution)",
        "Code of Civil Procedure, 1908 (Order 37 - Summary Suit for Recovery of Debt; Section 20 - Jurisdiction; Section 34 - Interest)",
        "Negotiable Instruments Act, 1881 (Section 138 - Dishonour of Cheque; Section 139 - Presumption of Debt; Section 142 - 30-Day Timeline; Section 143A - 20% Interim Compensation)",
        "Micro, Small and Medium Enterprises Development (MSMED) Act, 2006 (Sections 15, 16 & 18 - Compound Interest at 3x RBI Rate & Samadhaan Council)",
        "Bharatiya Sakshya Adhiniyam, 2023 (Section 63 - Electronic Evidence Certificate for UPI/WhatsApp/Emails) & Limitation Act, 1963 (3-Year Limitation)"
    ],

    "legal_notice_template": (
        "**FORMAL LEGAL NOTICE OF DEMAND FOR RECOVERY OF DUES**\n"
        "*(Sent via Registered Post A.D. / Speed Post / Registered Email / WhatsApp)*\n\n"
        "**Date:** {current_date}\n\n"
        "**To:**\n"
        "**{debtor_name}**\n"
        "Address / Location: {jurisdiction_city}\n\n"
        "**From (Claimant / Creditor):**\n"
        "**{creditor_name}**\n"
        "Location: {jurisdiction_city}\n\n"
        "---\n\n"
        "**SUBJECT: FORMAL LEGAL NOTICE FOR IMMEDIATE PAYMENT OF OUTSTANDING DUES OF RS. {principal_amount_owed}/- ALONG WITH INTEREST**\n\n"
        "Sir/Madam,\n\n"
        "Under instructions and on behalf of **{creditor_name}**, I hereby serve upon you this Formal Legal Notice of Demand:\n\n"
        "1. **TRANSACTION & LIABILITY:** That you entered into a lawful transaction/obligation with the undersigned concerning **{transaction_nature}**, duly evidenced by {proof_status}.\n\n"
        "2. **DEFAULT IN PAYMENT:** That an aggregate principal sum of **Rs. {principal_amount_owed}/-** became lawfully due and payable by you since **{default_timeline}**. However, you have failed and neglected to clear the said dues on the pretext of \"{default_reason_or_excuse}\".\n\n"
        "3. **STATUTORY BREACH:** That your willful default constitutes an actionable breach of obligation under Section 73 of the Indian Contract Act, 1872 (and where applicable, attracts statutory penal liability under Section 138 of the Negotiable Instruments Act, 1881 / MSMED Act, 2006).\n\n"
        "4. **DEMAND (15 DAYS NOTICE):** You are hereby called upon to remit the entire outstanding amount of **Rs. {principal_amount_owed}/-** along with 18% per annum interest within **fifteen (15) days** from the receipt of this notice.\n\n"
        "5. **CONSEQUENCE OF NON-COMPLIANCE:** Take notice that upon your failure to remit the aforesaid amount within 15 days, I shall initiate appropriate legal proceedings against you, including a Summary Suit for Recovery under Order 37 of the Code of Civil Procedure, 1908 (and criminal prosecution under Section 138 NI Act if cheque dishonoured), at your sole risk as to costs and consequences.\n\n"
        "**Claimant / Sender:**\n"
        "**{creditor_name}**"
    )
}
