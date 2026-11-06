"""
Grounding Knowledge Base: Unpaid Salary & Employment Dues
Defines required entities, plain-language legal standing, permissible statutes,
and the deterministic Legal Demand Notice template.
"""

UNPAID_SALARY_KB = {
    "domain_id": "unpaid_salary",
    "domain_name": "Unpaid Salary and Employment Dues",
    "description": "Disputes where an employer has withheld earned wages, full and final settlement (FnF), or severance pay.",
    "jurisdiction": "India (Labour & Civil Employment Law)",

    "required_entities": {
        "employee_name": {
            "type": "string",
            "description": "Full legal name of the employee demanding payment",
            "clarification_prompt": "Aapka poora naam kya hai jo company ke records ya offer letter par darj hai?"
        },
        "employer_company_name": {
            "type": "string",
            "description": "Registered name of the employer company or entity",
            "clarification_prompt": "Company ya employer ka poora naam kya hai?"
        },
        "office_location": {
            "type": "string",
            "description": "City or office location where the employee was working",
            "clarification_prompt": "Aapka office kis sheher me sthit hai jahan aap kaam karte the?"
        },
        "designation": {
            "type": "string",
            "description": "Job title or role held by the employee",
            "clarification_prompt": "Company me aapki designation ya role kya tha?"
        },
        "total_amount_owed": {
            "type": "number",
            "description": "Total outstanding salary and dues (in INR)",
            "clarification_prompt": "Company par aapki kul kitni salary baaki hai (rupaye me)?"
        },
        "unpaid_months": {
            "type": "string",
            "description": "Specific months or period for which salary was withheld (e.g. September and October 2024)",
            "clarification_prompt": "Kaun se mahinon ki salary roki gayi hai?"
        },
        "employment_status": {
            "type": "string",
            "description": "Whether currently employed, resigned, or terminated",
            "clarification_prompt": "Kya aap abhi bhi wahan kaam kar rahe hain, ya resign kar chuke hain?"
        },
        "proof_status": {
            "type": "string",
            "enum": ["offer_letter_and_slips", "bank_statement_and_emails", "relieving_letter", "informal_or_whatsapp"],
            "description": "Documentation available with employee",
            "clarification_prompt": "Aapke paas kya documents hain? (Jaise Offer Letter, purani Salary Slips, Relieving Letter, ya resignation email?)"
        }
    },

    "grounded_legal_standing": {
        "en": (
            "Under Indian Labour and Contract Laws:\n"
            "1. Earned wages are the legal right of the employee. An employer cannot legally withhold earned salary citing business losses, client payment delays, or lack of funds.\n"
            "2. Non-payment of salary is a civil and contractual breach, not typically a criminal fraud under IPC 420 unless fraudulent intent existed at inception.\n"
            "3. Once notice period is served or employment ends, the company is legally mandated to clear the Full and Final (FnF) settlement within statutory timeframes (typically within 7 to 30 days).\n"
            "4. The employee is entitled to claim the principal amount along with interest, and can approach the Labour Commissioner or file a Summary Suit for recovery under Order 37 of CPC or Section 9 Demand Notice under IBC (for corporate debtors)."
        ),
        "hi": (
            "Bhartiya shram kanoon aur contractual rules ke mutabiq:\n"
            "1. Kaam ki gayi avadhi ka vetan (earned salary) aapka kanooni adhikar hai. Company client payment delay ya fund ki kami ka bahana banakar salary nahi rok sakti.\n"
            "2. Salary na milna ek civil aur labour matter hai, samanyata isme criminal FIR (jaise 420) nahi banti jab tak shuruat se hi dhokhadhadi ka irada na ho.\n"
            "3. Notice period poora hone ya resignation ke baad, company ko Full and Final settlement niyamit samay me karna anivarya hai.\n"
            "4. Aap poora baaki vetan byaj (interest) sahit maangne ke haqdaar hain aur Labour Commissioner ya Civil Court me Summary Suit ke jariye claim kar sakte hain."
        )
    },

    "permissible_statutes": [
        "Payment of Wages Act, 1936 / Industrial Disputes Act, 1947",
        "Indian Contract Act, 1872 (Section 73 - Breach of Contract)",
        "Code of Civil Procedure, 1908 (Order 37 - Summary Suit for Recovery of Debt)",
        "Insolvency and Bankruptcy Code, 2016 (Section 8/9 - Demand Notice by Operational Creditor)"
    ],

    "legal_notice_template": (
        "**FORMAL LEGAL NOTICE OF DEMAND FOR UNPAID SALARY AND DUES**\n"
        "*(Sent via Registered Email / Speed Post)*\n\n"
        "**Date:** {current_date}\n\n"
        "**To:**\n"
        "**The Management / Directors**\n"
        "**{employer_company_name}**\n"
        "Address: {office_location}\n\n"
        "**From (Sender):**\n"
        "**{employee_name}**\n"
        "Designation: {designation}\n\n"
        "---\n\n"
        "**SUBJECT: FORMAL DEMAND NOTICE FOR PAYMENT OF OUTSTANDING SALARY AMOUNTING TO RS. {total_amount_owed}/- AND ISSUANCE OF SERVICE DOCUMENTS**\n\n"
        "Sir/Madam,\n\n"
        "Under instructions and on behalf of myself, **{employee_name}**, I hereby issue this Formal Notice of Demand regarding the illegal withholding of my legitimate earned remuneration:\n\n"
        "1. **EMPLOYMENT & ROLE:** That I was employed with **{employer_company_name}** at your **{office_location}** office as **{designation}**. My employment is evidenced by valid documentation including {proof_status}.\n\n"
        "2. **SERVICE & SEPARATION:** That I discharged my professional duties diligently. My employment status is **{employment_status}**, having fulfilled all contractual obligations including handover.\n\n"
        "3. **DEFAULT IN PAYMENT:** That despite continuous service and multiple reminders, you have unlawfully withheld and failed to disburse my earned salary for the period of **{unpaid_months}**, aggregating to a total outstanding sum of **Rs. {total_amount_owed}/-**.\n\n"
        "4. **LEGAL LIABILITY:** That salary earned is a fundamental property right under law. Unilateral withholding under pretexts such as client delays or operational fund deficits is illegal and constitutes a clear breach of contract under Section 73 of the Indian Contract Act, 1872, as well as applicable labour welfare statutes.\n\n"
        "5. **DEMAND (15 DAYS NOTICE):** You are hereby called upon to remit the entire outstanding dues of **Rs. {total_amount_owed}/-** along with my Relieving Certificate and Full & Final statement directly to my designated bank account within **fifteen (15) days** from the receipt of this notice.\n\n"
        "6. **CONSEQUENCE OF DEFAULT:** Please note that if you fail to comply with this demand within the stipulated period, I shall be constrained to initiate appropriate legal proceedings before the competent Labour Court/Authority, file a Summary Suit for Recovery under Order 37 CPC with interest, and explore statutory remedies under the Insolvency and Bankruptcy Code (IBC), 2016, holding your company and its officers liable for all costs and consequences.\n\n"
        "**Sender:**\n"
        "**{employee_name}**"
    )
}
