from kernel.kernel import register_rule
from ..actions.buyer import *
from ..guards.buyer import *

BUYER_RULES = [
    ("REG_NAME",    "VALID_NAME",  "buyer_name_guard",  "SAVE_BUYER_NAME",    "REG_PHONE"),
    ("REG_PHONE",   "VALID_PHONE", "buyer_phone_guard", "SAVE_BUYER_PHONE",   "REG_EMAIL"),
    ("REG_EMAIL",   "VALID_EMAIL", "buyer_email_guard", "SAVE_BUYER_EMAIL",   "REG_DOB"),
    ("REG_DOB",     "VALID_DOB",   "buyer_dob_guard",   "SAVE_BUYER_DOB",     "REG_NIN"),
    ("REG_NIN",     "VALID_NIN",   "buyer_nin_guard",   "SAVE_BUYER_NIN",     "REG_CITY"),
    ("REG_CITY",    "VALID_CITY",  None,                "SAVE_BUYER_CITY",    "REG_LGA"),
    ("REG_LGA",     "VALID_LGA",   None,                "SAVE_BUYER_LGA",     "REG_ADDRESS"),
    ("REG_ADDRESS", "VALID_ADDR",  None,                "SAVE_BUYER_ADDRESS", "BROWSING"),
]


def register_buyer_flow():
    register_buyer_guards()
    register_buyer_actions()
    for state, event, guard, action, next_state in BUYER_RULES:
        register_rule(state, event, action=action, guard=guard, next_state=next_state)


def resolve_event(state, text, content_type):
    lower = text.lower().strip()
    event_map = {
        "REG_NAME":    ("VALID_NAME",  lambda: len(text) >= 2),
        "REG_PHONE":   ("VALID_PHONE", lambda: text.replace("+","").isdigit() and len(text) >= 10),
        "REG_EMAIL":   ("VALID_EMAIL", lambda: "@" in text and "." in text),
        "REG_DOB":     ("VALID_DOB",   lambda: len(text) >= 8),
        "REG_NIN":     ("VALID_NIN",   lambda: text.isdigit() and len(text) == 11),
        "REG_CITY":    ("VALID_CITY",  lambda: len(text) >= 2),
        "REG_LGA":     ("VALID_LGA",   lambda: len(text) >= 2),
        "REG_ADDRESS": ("VALID_ADDR",  lambda: len(text) >= 5),
    }
    entry = event_map.get(state)
    if entry:
        event_name, condition = entry
        return event_name if condition() else None
    return None
