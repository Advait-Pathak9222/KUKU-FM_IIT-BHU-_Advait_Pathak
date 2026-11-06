from .rental_deposit import RENTAL_DEPOSIT_KB
from .unpaid_salary import UNPAID_SALARY_KB

GROUNDING_KBS = {
    "rental_deposit": RENTAL_DEPOSIT_KB,
    "unpaid_salary": UNPAID_SALARY_KB
}

def get_kb(domain: str):
    return GROUNDING_KBS.get(domain)
