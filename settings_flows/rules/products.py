from kernel.kernel import register_rule
from ..actions.products import *
from ..guards.products import *

PRODUCT_RULES = [
    ("MENU",              "ADD_PRODUCT_TAPPED", None,                  "START_ADD_PRODUCT",            "ASK_PRODUCT_NAME"),
    ("ASK_PRODUCT_NAME",  "VALID_NAME",          "product_name_guard", "SAVE_PRODUCT_NAME",             "ASK_PRODUCT_PRICE"),
    ("ASK_PRODUCT_PRICE", "VALID_PRICE",         "product_price_guard","SAVE_PRODUCT_PRICE",            "ASK_PRODUCT_STOCK"),
    ("ASK_PRODUCT_STOCK", "VALID_STOCK",         "product_stock_guard","SAVE_PRODUCT_STOCK",            "ASK_PRODUCT_UNIT"),
    ("ASK_PRODUCT_UNIT",  "UNIT_PICKED",         None,                  "SAVE_PRODUCT_UNIT",            "REVIEW_LIST"),
    ("ASK_PRODUCT_UNIT",  "UNIT_CUSTOM_TAPPED",  None,                  "SAVE_PRODUCT_UNIT_CUSTOM_PROMPT","ASK_PRODUCT_UNIT_CUSTOM"),
    ("ASK_PRODUCT_UNIT_CUSTOM", "VALID_UNIT",    "product_name_guard", "SAVE_PRODUCT_UNIT",             "REVIEW_LIST"),
    ("REVIEW_LIST",       "ADD_ANOTHER_TAPPED",  None,                  "START_ADD_PRODUCT",            "ASK_PRODUCT_NAME"),
    ("REVIEW_LIST",       "DONE_TAPPED",         None,                  "FINISH_PRODUCT_LIST",          "MENU"),
]


def register_product_flow():
    register_product_guards()
    register_product_actions()
    for state, event, guard, action, next_state in PRODUCT_RULES:
        register_rule(state, event, action=action, guard=guard, next_state=next_state)


def resolve_event(state, text, content_type):
    if content_type == "photo":
        return None

    event_map = {
        "ASK_PRODUCT_NAME":         ("VALID_NAME", lambda: len(text.strip()) >= 1),
        "ASK_PRODUCT_PRICE":        ("VALID_PRICE", lambda: _is_number(text)),
        "ASK_PRODUCT_STOCK":        ("VALID_STOCK", lambda: text.strip().isdigit()),
        "ASK_PRODUCT_UNIT_CUSTOM":  ("VALID_UNIT", lambda: len(text.strip()) >= 1),
    }

    entry = event_map.get(state)
    if entry:
        event_name, condition = entry
        return event_name if condition() else None
    return None


def _is_number(text):
    try:
        float(text.strip())
        return True
    except ValueError:
        return False


def resolve_callback_event(state, callback_data):
    if state == "ASK_PRODUCT_UNIT":
        if callback_data == "unit_custom":
            return "UNIT_CUSTOM_TAPPED"
        if callback_data.startswith("unit_"):
            return "UNIT_PICKED"

    callback_map = {
        ("MENU", "add_product_tapped"): "ADD_PRODUCT_TAPPED",
        ("REVIEW_LIST", "add_another_product"): "ADD_ANOTHER_TAPPED",
        ("REVIEW_LIST", "finish_product_list"): "DONE_TAPPED",
    }
    return callback_map.get((state, callback_data))
