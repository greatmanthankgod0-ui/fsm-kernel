from kernel.kernel import register_rule
from ..actions.seller import *
from ..guards.seller import *

SELLER_RULES = [
    ("TC_PENDING",        "AGREE_TAPPED",       None,                 None,                  "ASK_FULL_NAME"),
    ("TC_PENDING",        "DECLINE_TAPPED",     None,                 "CANCEL_APPLICATION",  "START"),
    ("ASK_FULL_NAME",     "VALID_NAME",         "name_guard",         "SAVE_FULL_NAME",      "ASK_SHOP_NAME"),
    ("ASK_SHOP_NAME",     "VALID_SHOP",         None,                 "SAVE_SHOP_NAME",      "ASK_PHONE"),
    ("ASK_PHONE",         "VALID_PHONE",        "phone_guard",        "SAVE_PHONE",          "ASK_EMAIL"),
    ("ASK_EMAIL",         "VALID_EMAIL",        "email_guard",        "SAVE_EMAIL",          "ASK_DOB"),
    ("ASK_DOB",           "VALID_DOB",          "dob_guard",          "SAVE_DOB",            "ASK_NIN"),
    ("ASK_NIN",           "VALID_NIN",          "nin_guard",          "SAVE_NIN",            "ASK_NIN_PHOTO"),
    ("ASK_NIN_PHOTO",     "PHOTO_RECEIVED",     "photo_guard",        "SAVE_NIN_PHOTO",      "ASK_FACE_PHOTO"),
    ("ASK_FACE_PHOTO",    "PHOTO_RECEIVED",     "photo_guard",        "SAVE_FACE_PHOTO",     "ASK_SHOP_PHOTO"),
    ("ASK_SHOP_PHOTO",    "PHOTO_RECEIVED",     "photo_guard",        "SAVE_SHOP_PHOTO",     "ASK_CITY"),
    ("ASK_CITY",          "VALID_CITY",         None,                 "SAVE_CITY",           "ASK_LGA"),
    ("ASK_CITY",          "CITY_NEEDS_CONFIRM", None,                 None,                  "CONFIRM_CITY"),
    ("CONFIRM_CITY",      "CITY_CONFIRMED",     None,                 "SAVE_CONFIRMED_CITY", "ASK_LGA"),
    ("CONFIRM_CITY",      "CITY_KEPT",          None,                 "SAVE_KEPT_CITY",      "ASK_LGA"),
    ("ASK_LGA",           "VALID_LGA",          None,                 "SAVE_LGA",            "ASK_ADDRESS"),
    ("ASK_LGA",           "LGA_NEEDS_CONFIRM",  None,                 None,                  "CONFIRM_LGA"),
    ("CONFIRM_LGA",       "LGA_CONFIRMED",      None,                 "SAVE_CONFIRMED_LGA",  "ASK_ADDRESS"),
    ("CONFIRM_LGA",       "LGA_KEPT",           None,                 "SAVE_KEPT_LGA",       "ASK_ADDRESS"),
    ("ASK_ADDRESS",       "VALID_ADDRESS",      None,                 "SAVE_ADDRESS",        "ASK_BANK"),
    ("ASK_BANK",          "VALID_BANK",         None,                 "SAVE_BANK",           "ASK_ACCOUNT_NO"),
    ("ASK_ACCOUNT_NO",    "VALID_ACCOUNT_NO",   "account_no_guard",   "SAVE_ACCOUNT_NO",     "ASK_ACCOUNT_NAME"),
    ("ASK_ACCOUNT_NAME",  "VALID_ACCOUNT_NAME", None,                 "SAVE_ACCOUNT_NAME",   "ASK_DELIVERY_HRS"),
    ("ASK_DELIVERY_HRS",  "VALID_DELIVERY_HRS", "delivery_hrs_guard", "SAVE_DELIVERY_HRS",   "ASK_BIO"),
    ("ASK_BIO",           "VALID_BIO",          None,                 "SAVE_BIO_DRAFT",      "CONFIRM_SUBMIT"),
    ("CONFIRM_SUBMIT",    "SUBMIT_TAPPED",      None,                 "SUBMIT_APPLICATION",  "DONE"),
    ("CONFIRM_SUBMIT",    "CANCEL_TAPPED",      None,                 "CANCEL_APPLICATION",  "TC_PENDING"),
]


def register_seller_flow():
    register_seller_guards()
    register_seller_actions()
    for state, event, guard, action, next_state in SELLER_RULES:
        register_rule(state, event, action=action, guard=guard, next_state=next_state)


def resolve_event(state, text, content_type):
    if content_type == "photo":
        return "PHOTO_RECEIVED"

    lower = text.lower().strip()

    event_map = {
        "ASK_FULL_NAME":     ("VALID_NAME", lambda: len(text) >= 2),
        "ASK_SHOP_NAME":     ("VALID_SHOP", lambda: len(text) >= 1),
        "ASK_PHONE":         ("VALID_PHONE", lambda: text.replace("+","").isdigit() and len(text) >= 10),
        "ASK_EMAIL":         ("VALID_EMAIL", lambda: "@" in text and "." in text),
        "ASK_DOB":           ("VALID_DOB", lambda: len(text) >= 8),
        "ASK_NIN":           ("VALID_NIN", lambda: text.isdigit() and len(text) == 11),
        "ASK_CITY":          ("VALID_CITY", lambda: len(text) >= 2),
        "ASK_LGA":           ("VALID_LGA", lambda: len(text) >= 2),
        "ASK_ADDRESS":       ("VALID_ADDRESS", lambda: len(text) >= 5),
        "ASK_BANK":          ("VALID_BANK", lambda: len(text) >= 2),
        "ASK_ACCOUNT_NO":    ("VALID_ACCOUNT_NO", lambda: text.isdigit() and len(text) >= 10),
        "ASK_ACCOUNT_NAME":  ("VALID_ACCOUNT_NAME", lambda: len(text) >= 2),
        "ASK_DELIVERY_HRS":  ("VALID_DELIVERY_HRS", lambda: text in ["6 hours","12 hours","24 hours","48 hours"]),
        "ASK_BIO":           ("VALID_BIO", lambda: True),
    }

    entry = event_map.get(state)
    if entry:
        event_name, condition = entry
        return event_name if condition() else None
    return None


def resolve_callback_event(state, callback_data):
    callback_map = {
        ("TC_PENDING", "seller_agree"): "AGREE_TAPPED",
        ("TC_PENDING", "seller_decline"): "DECLINE_TAPPED",
        ("CONFIRM_SUBMIT", "seller_submit"): "SUBMIT_TAPPED",
        ("CONFIRM_SUBMIT", "seller_cancel"): "CANCEL_TAPPED",
    }
    return callback_map.get((state, callback_data))
