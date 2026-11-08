"""
Bar Council of India (BCI) LL.B. Curriculum Doctrinal & Procedural Reasoning Matrix.
Equips NyayaMitra with substantive, procedural, evidentiary, and clinical drafting tools across:
1. Law of Contract I & II (Indian Contract Act, 1872 & Specific Relief Act, 1963)
2. Property & Tenancy Law (Transfer of Property Act, 1882 & Model Tenancy Act, 2021)
3. Labour & Industrial Law (Payment of Wages Act, 1936; Industrial Disputes Act, 1947; Code on Wages, 2019; IBC, 2016)
4. Law of Torts & Consumer Protection (Consumer Protection Act, 2019 & E-Commerce Rules, 2020)
5. Negotiable Instruments & Commercial Recovery (NI Act, 1881 Sec 138–143A & MSMED Act, 2006)
6. Civil Procedure Code (CPC, 1908 — Order 37, Sec 20, Sec 34, Sec 80) & Limitation Act, 1963
7. Law of Evidence (Bharatiya Sakshya Adhiniyam, 2023 Sec 63 / Indian Evidence Act Sec 65B)
"""

LAW_SCHOOL_DOCTRINAL_MATRIX = {
    "universal_procedural_and_evidentiary_tools": (
        "BCI LL.B. PROCEDURAL & EVIDENTIARY TOOLKIT (APPLY ACROSS ALL CASES):\n"
        "1. ELECTRONIC EVIDENCE (Section 63, Bharatiya Sakshya Adhiniyam, 2023 / Section 65B, Indian Evidence Act):\n"
        "   - WhatsApp chats, emails, SMS, audio recordings, e-commerce order confirmations, and UPI/NEFT bank statements are legally admissible electronic records when supported by a Section 63 BSA Certificate.\n"
        "2. ORAL AGREEMENTS & RESTITUTION (Section 10, Section 65 & Section 70, Indian Contract Act, 1872):\n"
        "   - Oral agreements are valid contracts under Section 10 ICA if supported by consideration and conduct (such as bank transfers or work performed).\n"
        "   - Under Section 70 (Quantum Meruit / Obligation of person enjoying benefit of non-gratuitous act), no landlord, employer, or client can unjustly enrich themselves by retaining money or unpaid work.\n"
        "3. PENALTY VS. GENUINE PRE-ESTIMATE OF LOSS (Section 73 & Section 74, Indian Contract Act, 1872):\n"
        "   - Under Section 74 ICA, unilateral forfeiture clauses (e.g., forfeiting an entire security deposit or enforcing an unconscionable employment bond penalty) are legally unenforceable unless the party proves actual loss caused by the breach.\n"
        "4. LIMITATION ACT, 1963 (STATUTORY TIME BARS):\n"
        "   - Civil Money Recovery / Unpaid Wages / Security Deposit Refund / Breach of Contract: 3 Years from when the debt became due or refusal occurred (Articles 7, 19, 55, 113 Limitation Act, 1963).\n"
        "   - Consumer Protection Complaint: 2 Years from cause of action (Section 69, Consumer Protection Act, 2019).\n"
        "   - Section 138 NI Act Cheque Bounce Notice: Strictly 30 Days from receipt of Bank Return Memo (with 15-day cure period).\n"
        "5. SERVICE OF NOTICE PRESUMPTION (Section 27, General Clauses Act, 1897):\n"
        "   - Dispatching a Legal Notice via Registered Post A.D. (RPAD) / Speed Post to the last known address, alongside official Email/WhatsApp (recognized by the Supreme Court of India), creates a statutory presumption of valid legal service."
    ),

    "domain_doctrines": {
        "rental_deposit": (
            "LL.B. PROPERTY & TENANCY DOCTRINES (Transfer of Property Act, 1882 & Model Tenancy Act, 2021):\n"
            "- Fiduciary Nature of Deposit: Security deposit is held in trust (fiduciary capacity), not as income of the landlord.\n"
            "- Reasonable Wear & Tear Exception (Section 108(m), Transfer of Property Act, 1882): A tenant is NOT liable for ordinary wear and tear (routine wall repainting, normal aging of fixtures). Deductions require itemized GST bills proving actual damage caused by tenant negligence.\n"
            "- Unregistered Lease > 11 Months (Section 49, Registration Act, 1908): Even if a rent agreement was unregistered or oral, payment of deposit via bank/UPI is fully recoverable under Section 73/70 Contract Act and admissible for collateral purpose.\n"
            "- Essential Services Protection (Section 20, Model Tenancy Act, 2021): A landlord/PG owner cannot disconnect electricity, water, or lock out a tenant over a monetary dispute.\n"
            "- Forum & Jurisdiction (Section 20 CPC): Rent Authority / Small Causes Court / Civil Court under Order 37 CPC where the property is situated or where the landlord resides."
        ),

        "unpaid_salary": (
            "LL.B. LABOUR, INDUSTRIAL & EMPLOYMENT DOCTRINES:\n"
            "- Workman vs. Managerial Distinction (Section 2(s), Industrial Disputes Act, 1947): Employees doing operational, technical, skilled, or clerical work (including software engineers, designers, executives, and workers without hire-and-fire managerial authority) can invoke the Labour Commissioner & file a recovery application under Section 33C(2) of the Industrial Disputes Act, 1947 or the State Shops & Establishments Act. Managerial employees can file a Summary Suit under Order 37 CPC or issue a Section 8 Demand Notice under IBC, 2016.\n"
            "- Prohibition of Unauthorized Deductions (Sections 7–13, Payment of Wages Act, 1936 & Code on Wages, 2019): Earned wages cannot be withheld for employer cash-flow problems, client non-payment, or unverified performance claims.\n"
            "- Pro-Rata & Component Rules: Earned Fixed Pay + accrued allowances for actual days/months worked are statutory dues; unvested ESOPs or discretionary future bonuses are excluded unless vested.\n"
            "- Withholding Relieving / Experience Certificate & Employment Bonds (Section 27 & Section 74, Indian Contract Act, 1872): Post-employment restraint of trade is void under Section 27 ICA; an employer cannot hold a Relieving Letter or Experience Certificate hostage, nor enforce a penal employment bond without proving actual training expenditure."
        ),

        "consumer_dispute": (
            "LL.B. CONSUMER PROTECTION & TORT DOCTRINES (Consumer Protection Act, 2019):\n"
            "- Definition of Consumer & Livelihood Exception (Section 2(7) Explanation (a), CPA 2019): A person buying goods/services for personal use OR for self-employment to earn their livelihood (e.g., freelancer buying a laptop) is a valid Consumer.\n"
            "- Defect, Deficiency & Unfair Trade Practice (Sections 2(10), 2(11), 2(47), CPA 2019): Unilateral 'No Return / No Refund' clauses printed on invoices are unconscionable and void when goods are defective or services are deficient.\n"
            "- Consumer-Friendly Territorial Jurisdiction (Section 34(2)(d), CPA 2019): The consumer can file the complaint via the e-Daakhil portal in the District Commission where the CONSUMER resides or works for gain (not forced to travel to the company's head office!).\n"
            "- Pecuniary Jurisdiction & Zero Fee Rule: District Commission handles claims up to Rs. 50 Lakhs (Rs. 0 court fee up to Rs. 5 Lakhs); State Commission Rs. 50L–2Cr; National Commission > Rs. 2Cr."
        ),

        "money_recovery": (
            "LL.B. COMMERCIAL RECOVERY, SPECIAL CONTRACTS & NEGOTIABLE INSTRUMENTS DOCTRINES:\n"
            "- Section 138 Negotiable Instruments Act, 1881 (Dishonour of Cheque): Presumption of legally enforceable debt under Section 139 NI Act. Statutory timeline: Cheque presented within 3 months -> Legal Notice sent within 30 days of Bank Return Memo -> 15 days given to pay -> Criminal complaint before JMFC within 30 days thereafter (with up to 20% interim compensation under Section 143A NI Act).\n"
            "- Summary Suit under Order XXXVII CPC, 1908: Available for written contracts, invoices, dishonoured cheques, promissory notes, and acknowledged debts—defendant has no automatic right to defend without court leave.\n"
            "- MSMED Act, 2006 (Sections 15, 16 & 18): If the claimant is a registered MSME (Udyam) vendor/service provider, the buyer must pay compound interest at 3x the RBI Bank Rate via the MSME Samadhaan Facilitation Council.\n"
            "- Friendly Loans & Digital Transfers (Section 73 & 70 ICA + Order 37 CPC): Bank/UPI transfers combined with WhatsApp/email admissions (certified under Section 63 BSA) establish an actionable civil debt."
        )
    }
}


def get_doctrinal_context(domain: str) -> str:
    universal = LAW_SCHOOL_DOCTRINAL_MATRIX["universal_procedural_and_evidentiary_tools"]
    specific = LAW_SCHOOL_DOCTRINAL_MATRIX["domain_doctrines"].get(domain, "")
    return f"{universal}\n\n{specific}".strip()
