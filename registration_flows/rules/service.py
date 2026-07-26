from kernel.kernel import register_rule
from ..actions.service import *
from ..guards.service import *

SERVICE_RULES = [
    ("TC_PENDING",       "AGREE_TAPPED",      None,               None,                  "ASK_FULL_NAME"),
    ("TC_PENDING",       "DECLINE_TAPPED",    None,               None,                  "TC_PENDING"),
    ("ASK_FULL_NAME",    "VALID_NAME",        "svc_name_guard",   "SAVE_SVC_NAME",       "ASK_BUSINESS"),
    ("ASK_BUSINESS",     "VALID_BUSINESS",    None,               "SAVE_SVC_BUSINESS",   "ASK_SKILL"),
    ("ASK_SKILL",        "VALID_SKILL",       None,               "SAVE_SVC_SKILL",      "ASK_PHONE"),
    ("ASK_SKILL",        "SKILL_NEEDS_CONFIRM", None,               None,                  "CONFIRM_SKILL"),
    ("CONFIRM_SKILL",    "SKILL_CONFIRMED",     None,               "USE_SUGGESTED_SKILL", "ASK_PHONE"),
    ("CONFIRM_SKILL",    "SKILL_KEPT",          None,               "KEEP_TYPED_SKILL",    "ASK_PHONE"),
    ("ASK_PHONE",        "VALID_PHONE",       "svc_phone_guard",  "SAVE_SVC_PHONE",      "ASK_EMAIL"),
    ("ASK_EMAIL",        "VALID_EMAIL",       "svc_email_guard",  "SAVE_SVC_EMAIL",      "ASK_DOB"),
    ("ASK_DOB",          "VALID_DOB",         None,               "SAVE_SVC_DOB",        "ASK_NIN"),
    ("ASK_NIN",          "VALID_NIN",         "svc_nin_guard",    "SAVE_SVC_NIN",        "ASK_NIN_PHOTO"),
    ("ASK_NIN_PHOTO",    "PHOTO_RECEIVED",    "svc_photo_guard",  "SAVE_SVC_NIN_PHOTO",  "ASK_FACE_PHOTO"),
    ("ASK_FACE_PHOTO",   "PHOTO_RECEIVED",    "svc_photo_guard",  "SAVE_SVC_FACE_PHOTO", "ASK_WORKPLACE_PHOTO"),
    ("ASK_WORKPLACE_PHOTO", "PHOTO_RECEIVED", "svc_photo_guard",  "SAVE_SVC_WORKPLACE_PHOTO", "ASK_CITY"),
    ("ASK_CITY",         "VALID_CITY",        None,               "SAVE_SVC_CITY",       "ASK_LGA"),
    ("ASK_LGA",          "VALID_LGA",         None,               "SAVE_SVC_LGA",        "ASK_ADDRESS"),
    ("ASK_ADDRESS",      "VALID_ADDRESS",     None,               "SAVE_SVC_ADDRESS",    "ASK_BANK"),
    ("ASK_BANK",         "VALID_BANK",        None,               "SAVE_SVC_BANK",       "ASK_ACCOUNT_NO"),
    ("ASK_ACCOUNT_NO",   "VALID_ACCOUNT_NO",  "svc_account_guard","SAVE_SVC_ACCOUNT_NO", "ASK_TURNAROUND"),
    ("ASK_TURNAROUND",   "VALID_TURNAROUND",  None,               "SAVE_SVC_TURNAROUND","ASK_BIO"),
    ("ASK_BIO",          "VALID_BIO",         None,               "SAVE_SVC_BIO",        "DONE"),
]


def register_service_flow():
    register_service_guards()
    register_service_actions()
    for state, event, guard, action, next_state in SERVICE_RULES:
        register_rule(state, event, action=action, guard=guard, next_state=next_state)


def resolve_event(state, text, content_type):
    if content_type == "photo":
        return "PHOTO_RECEIVED"

    lower = text.lower().strip()

    event_map = {
        "ASK_FULL_NAME":   ("VALID_NAME", lambda: len(text) >= 2),
        "ASK_BUSINESS":    ("VALID_BUSINESS", lambda: len(text) >= 2),
        "ASK_SKILL":       ("VALID_SKILL", lambda: len(text) >= 2),
        "ASK_PHONE":       ("VALID_PHONE", lambda: text.replace("+","").isdigit() and len(text) >= 10),
        "ASK_EMAIL":       ("VALID_EMAIL", lambda: "@" in text and "." in text),
        "ASK_DOB":         ("VALID_DOB", lambda: len(text) >= 8),
        "ASK_NIN":         ("VALID_NIN", lambda: text.isdigit() and len(text) == 11),
        "ASK_CITY":        ("VALID_CITY", lambda: len(text) >= 2),
        "ASK_LGA":         ("VALID_LGA", lambda: len(text) >= 2),
        "ASK_ADDRESS":     ("VALID_ADDRESS", lambda: len(text) >= 5),
        "ASK_BANK":        ("VALID_BANK", lambda: len(text) >= 2),
        "ASK_ACCOUNT_NO":  ("VALID_ACCOUNT_NO", lambda: text.isdigit() and len(text) >= 10),
        "ASK_TURNAROUND":  ("VALID_TURNAROUND", lambda: text in ["Same day", "Next day", "2-3 days", "A week"]),
        "ASK_BIO":         ("VALID_BIO", lambda: True),
    }

    entry = event_map.get(state)
    if entry:
        event_name, condition = entry
        return event_name if condition() else None
    return None


def resolve_callback_event(state, callback_data):
    callback_map = {
        ("TC_PENDING", "service_agree"): "AGREE_TAPPED",
        ("TC_PENDING", "service_decline"): "DECLINE_TAPPED",
    }
    return callback_map.get((state, callback_data))
