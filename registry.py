from . import guards
from . import actions

FLOW_REGISTRY = {
    "SELLER": {
        ("TC_PENDING", "AGREE"): {
            "guard": "agree_guard",
            "action": "SET_FULL_NAME",
            "next": "ASK_FULL_NAME"
        },

        ("ASK_FULL_NAME", "VALID_NAME"): {
            "guard": guards.name_guard,
            "action": actions.SAVE_FULL_NAME,
            "next": "ASK_SHOP_NAME"
        },

        ("ASK_SHOP_NAME", "VALID_SHOP"): {
            "guard": None,
            "action": actions.SAVE_SHOP_NAME,
            "next": "ASK_PHONE"
        },
    }
}
def register_flow(domain, transitions):
    FLOW_REGISTRY[domain] = transitions
