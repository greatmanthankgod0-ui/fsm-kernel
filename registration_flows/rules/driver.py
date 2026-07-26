from kernel.kernel import register_rule
from ..actions.driver import *
from ..guards.driver import *

DRIVER_RULES = [
    ("TC_PENDING",       "AGREE_TAPPED",       None,                   None,                       "ASK_FULL_NAME"),
    ("TC_PENDING",       "DECLINE_TAPPED",     None,                   None,                       "TC_PENDING"),
    ("ASK_FULL_NAME",    "VALID_NAME",         "driver_name_guard",    "SAVE_DRIVER_NAME",         "ASK_PHONE"),
    ("ASK_PHONE",        "VALID_PHONE",        "driver_phone_guard",   "SAVE_DRIVER_PHONE",        "ASK_EMAIL"),
    ("ASK_EMAIL",        "VALID_EMAIL",        None,                   "SAVE_DRIVER_EMAIL",        "ASK_DOB"),
    ("ASK_DOB",          "VALID_DOB",          None,                   "SAVE_DRIVER_DOB",          "ASK_NIN"),
    ("ASK_NIN",          "VALID_NIN",          "driver_nin_guard",     "SAVE_DRIVER_NIN",          "ASK_NIN_PHOTO"),
    ("ASK_NIN_PHOTO",    "PHOTO_RECEIVED",     "driver_photo_guard",   "SAVE_DRIVER_NIN_PHOTO",    "ASK_FACE_PHOTO"),
    ("ASK_FACE_PHOTO",   "PHOTO_RECEIVED",     "driver_photo_guard",   "SAVE_DRIVER_FACE_PHOTO",   "ASK_CITY"),
    ("ASK_CITY",         "VALID_CITY",         None,                   "SAVE_DRIVER_CITY",         "ASK_LGA"),
    ("ASK_LGA",          "VALID_LGA",          None,                   "SAVE_DRIVER_LGA",          "ASK_ADDRESS"),
    ("ASK_ADDRESS",      "VALID_ADDRESS",      None,                   "SAVE_DRIVER_ADDRESS",      "ASK_VEHICLE"),
    ("ASK_VEHICLE",      "VALID_VEHICLE",      "driver_vehicle_guard", "SAVE_DRIVER_VEHICLE",      "ASK_PLATE"),
    ("ASK_PLATE",        "VALID_PLATE",        None,                   "SAVE_DRIVER_PLATE",        "ASK_PLATE_PHOTO"),
    ("ASK_PLATE_PHOTO",  "PHOTO_RECEIVED",     "driver_photo_guard",  "SAVE_DRIVER_PLATE_PHOTO",  "DONE"),
]


def register_driver_flow():
    register_driver_guards()
    register_driver_actions()
    for state, event, guard, action, next_state in DRIVER_RULES:
        register_rule(state, event, action=action, guard=guard, next_state=next_state)


def resolve_event(state, text, content_type):
    if content_type == "photo":
        return "PHOTO_RECEIVED"

    lower = text.lower().strip()

    event_map = {
        "ASK_FULL_NAME":  ("VALID_NAME", lambda: len(text) >= 2),
        "ASK_PHONE":      ("VALID_PHONE", lambda: text.replace("+","").isdigit() and len(text) >= 10),
        "ASK_EMAIL":      ("VALID_EMAIL", lambda: "@" in text and "." in text),
        "ASK_DOB":        ("VALID_DOB", lambda: len(text) >= 8),
        "ASK_NIN":        ("VALID_NIN", lambda: text.isdigit() and len(text) == 11),
        "ASK_CITY":       ("VALID_CITY", lambda: len(text) >= 2),
        "ASK_LGA":        ("VALID_LGA", lambda: len(text) >= 2),
        "ASK_ADDRESS":    ("VALID_ADDRESS", lambda: len(text) >= 5),
        "ASK_VEHICLE":    ("VALID_VEHICLE", lambda: lower in ["🏍️ bike", "🚗 car", "🚐 van", "🚛 truck", "🏎️ tricycle (keke)"]),
        "ASK_PLATE":      ("VALID_PLATE", lambda: len(text) >= 3),
    }

    entry = event_map.get(state)
    if entry:
        event_name, condition = entry
        return event_name if condition() else None
    return None


def resolve_callback_event(state, callback_data):
    callback_map = {
        ("TC_PENDING", "driver_agree"): "AGREE_TAPPED",
        ("TC_PENDING", "driver_decline"): "DECLINE_TAPPED",
    }
    return callback_map.get((state, callback_data))
