from .rental_deposit import RENTAL_DEPOSIT_KB
from .unpaid_salary import UNPAID_SALARY_KB
from .consumer_dispute import CONSUMER_DISPUTE_KB
from .money_recovery import MONEY_RECOVERY_KB

GROUNDING_KBS = {
    "rental_deposit": RENTAL_DEPOSIT_KB,
    "unpaid_salary": UNPAID_SALARY_KB,
    "consumer_dispute": CONSUMER_DISPUTE_KB,
    "money_recovery": MONEY_RECOVERY_KB,
}

def get_kb(domain: str):
    return GROUNDING_KBS.get(domain)
