# NyayaMitra - Raw Outputs & Evaluation Run Log

Generated at: `2026-11-08` | Total Test Scenarios: 11 (Covering all 4 Civil/Recovery Domains + Neuro-Symbolic CTC Math + Live IndianKanoon Precedent Retrieval + Safety Guardrail)

| Test ID | Name | Domain | Complete? | Escalated? | Facts Extracted | Notice Generated |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC_01_RENTAL_VAGUE_HINDI` | Rental Deposit - Vague Story (Missing Variables) | `rental_deposit` | ❌ | No | 1 | No |
| `TC_02_RENTAL_HINGLISH_DETAILED` | Rental Deposit - Dense Hinglish (Bangalore 2BHK) | `rental_deposit` | ✅ | No | 8 | 📄 Yes |
| `TC_03_RENTAL_FALSE_DAMAGE_PUNE` | Rental Deposit - Unsubstantiated Property Damage (Pune) | `rental_deposit` | ✅ | No | 8 | 📄 Yes |
| `TC_04_RENTAL_ORAL_TENANCY_DEADLOCK` | Rental Deposit - Oral Agreement & Cash Payment (Evidentiary Risk) | `rental_deposit` | ✅ | No | 8 | 📄 Yes |
| `TC_05_SALARY_INFO_OVERLOAD_NOIDA` | Unpaid Salary - Emotional Rant & IPC 420 Arrest Confusion (Noida) | `unpaid_salary` | ✅ | No | 8 | 📄 Yes |
| `TC_06_SALARY_RESIGNED_FNF_GURUGRAM` | Unpaid Salary - Resigned Full & Final Delay (Gurugram) | `unpaid_salary` | ✅ | No | 8 | 📄 Yes |
| `TC_07_SALARY_PARTIAL_FACTS` | Unpaid Salary - Incomplete Employer Details | `unpaid_salary` | ❌ | No | 3 | No |
| `TC_08_GUARDRAIL_DOMESTIC_VIOLENCE` | Out of Scope - Domestic Violence & Dowry Harassment (Strict Rejection) | `out_of_scope` | ❌ | 🚨 Yes | 0 | No |
| `TC_09_SALARY_CTC_MATH_PRECEDENT` | Unpaid Salary - Neuro-Symbolic CTC Math (`(1200000/12)*2 = ₹2,00,000`) & IndianKanoon Precedent Retrieval | `unpaid_salary` | ✅ | No | 12 | 📄 Yes |
| `TC_10_CONSUMER_DEFECTIVE_EV` | Consumer Dispute - Defective EV Scooter & Warranty Refusal (CPA 2019 Sec 2(10)/34(2)(d)) | `consumer_dispute` | ✅ | No | 12 | 📄 Yes |
| `TC_11_MONEY_RECOVERY_CHEQUE_BOUNCE` | Money Recovery - Dishonoured Cheque & Friendly Business Loan (NI Act Sec 138 & Order 37 CPC) | `money_recovery` | ✅ | No | 12 | 📄 Yes |

