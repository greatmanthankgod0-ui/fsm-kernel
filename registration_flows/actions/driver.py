from kernel.kernel import register_action
from config import ADMIN_ID, DISPATCH_DB
from storage.db import get_conn


def _update(ctx, field, value):
    uid = ctx["user_id"]
    conn = get_conn(DISPATCH_DB)
    c = conn.cursor()
    c.execute(f"UPDATE driver_sessions SET {field} = ? WHERE driver_id = ?", (value, uid))
    conn.commit()
    conn.close()


def save_driver_name(ctx):
    name = ctx["text"]
    _update(ctx, "full_name", name)
    first = name.split()[0]
    ctx["bot"].send_message(ctx["user_id"],
        f"Good to meet you, {first} 🚴\n\nWhat's your phone number?")


def save_driver_phone(ctx):
    _update(ctx, "phone", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Got it. Email address?")


def save_driver_email(ctx):
    _update(ctx, "email", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Thanks. Date of birth? (DD/MM/YYYY)")


def save_driver_dob(ctx):
    _update(ctx, "dob", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Now your NIN — 11 digits.")


def save_driver_nin(ctx):
    _update(ctx, "nin", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Send a clear photo of your NIN slip 📸")


def save_driver_nin_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(ADMIN_ID, f"🪪 NIN photo from driver {user_id}")
    bot.send_message(user_id, "Got it. Now a clear selfie so we know it's you 🤳")


def save_driver_face_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(user_id, "That's you. 😊\n\nWhat city are you based in?")


def save_driver_city(ctx):
    _update(ctx, "city", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], f"{ctx['text']}, noted.\n\nWhich LGA?")


def save_driver_lga(ctx):
    _update(ctx, "lga", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Full address?")


def save_driver_address(ctx):
    _update(ctx, "address", ctx["text"])
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KeyboardButton("🏍️ Bike"), KeyboardButton("🚗 Car"))
    kb.row(KeyboardButton("🚐 Van"), KeyboardButton("🚛 Truck"))
    kb.row(KeyboardButton("🏎️ Tricycle (Keke)"))
    ctx["bot"].send_message(ctx["user_id"], "What do you ride or drive?", reply_markup=kb)


def save_driver_vehicle(ctx):
    _update(ctx, "vehicle_type", ctx["text"])
    from telebot.types import ReplyKeyboardRemove
    ctx["bot"].send_message(ctx["user_id"],
        f"{ctx['text']} — got it.\n\nPlate number?",
        reply_markup=ReplyKeyboardRemove())


def save_driver_plate(ctx):
    _update(ctx, "plate_number", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        f"{ctx['text']} — got it.\n\nLast thing — send a clear photo of your number plate 📸")


def save_driver_plate_photo(ctx):
    user_id = ctx["user_id"]
    bot = ctx["bot"]
    msg_id = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    conn = get_conn(DISPATCH_DB)
    c = conn.cursor()
    c.execute("""SELECT full_name, phone, email, dob, nin, city, lga, address,
                        vehicle_type, plate_number
                 FROM driver_sessions WHERE driver_id = ?""", (user_id,))
    s = c.fetchone()

    c.execute("""INSERT OR REPLACE INTO drivers
        (driver_id, full_name, phone, email, dob, nin, city, lga, address,
         vehicle_type, plate_number, is_approved, is_available, tc_agreed,
         tc_agreed_at, joined_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,0,0,1,?,?)""",
        (user_id, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], now, now))
    c.execute("DELETE FROM driver_sessions WHERE driver_id = ?", (user_id,))
    conn.commit()
    conn.close()

    bot.send_message(user_id,
        f"You're in the queue, {s[0].split()[0]} 🎉\n\n"
        f"We'll check things over and get you riding soon.")

    bot.send_message(ADMIN_ID,
        f"🚴 New Driver Application\n\n"
        f"Name: {s[0]}\nID: {user_id}\n"
        f"📞 {s[1]} | 📧 {s[2]}\n"
        f"DOB: {s[3]} | NIN: {s[4]}\n"
        f"📍 {s[5]}, {s[6]} — {s[7]}\n"
        f"🚗 {s[8]} | Plate: {s[9]}\n\n"
        f"/approvedriver {user_id}"
    )


def register_driver_actions():
    register_action("SAVE_DRIVER_NAME", save_driver_name)
    register_action("SAVE_DRIVER_PHONE", save_driver_phone)
    register_action("SAVE_DRIVER_EMAIL", save_driver_email)
    register_action("SAVE_DRIVER_DOB", save_driver_dob)
    register_action("SAVE_DRIVER_NIN", save_driver_nin)
    register_action("SAVE_DRIVER_NIN_PHOTO", save_driver_nin_photo)
    register_action("SAVE_DRIVER_FACE_PHOTO", save_driver_face_photo)
    register_action("SAVE_DRIVER_CITY", save_driver_city)
    register_action("SAVE_DRIVER_LGA", save_driver_lga)
    register_action("SAVE_DRIVER_ADDRESS", save_driver_address)
    register_action("SAVE_DRIVER_VEHICLE", save_driver_vehicle)
    register_action("SAVE_DRIVER_PLATE", save_driver_plate)
    register_action("SAVE_DRIVER_PLATE_PHOTO", save_driver_plate_photo)


# ── City / LGA fuzzy match helpers ──

_PENDING_CITY = {}


def _get_pending_city(user_id):
    return _PENDING_CITY.get(user_id)


def save_driver_confirmed_city(ctx):
    city = ctx["text"].replace("city_use_", "")
    _PENDING_CITY[ctx["user_id"]] = city
    _update(ctx, "city", city)
    ctx["bot"].send_message(ctx["user_id"], f"📍 {city} — got it.\n\nWhich LGA?")


def save_driver_kept_city(ctx):
    uid = ctx["user_id"]
    from config import DISPATCH_DB
    from storage.db import get_conn
    conn = get_conn(DISPATCH_DB)
    c = conn.cursor()
    c.execute("SELECT city FROM driver_sessions WHERE driver_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    city = row[0] if row else "your city"
    _PENDING_CITY[uid] = city
    ctx["bot"].send_message(uid, f"📍 {city} — got it.\n\nWhich LGA?")


def save_driver_confirmed_lga(ctx):
    lga = ctx["text"].replace("lga_use_", "")
    _update(ctx, "lga", lga)
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_driver_kept_lga(ctx):
    uid = ctx["user_id"]
    from config import DISPATCH_DB
    from storage.db import get_conn
    conn = get_conn(DISPATCH_DB)
    c = conn.cursor()
    c.execute("SELECT lga FROM driver_sessions WHERE driver_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    lga = row[0] if row else "your LGA"
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_driver_lga_and_confirm(ctx):
    _update(ctx, "lga", ctx["text"])
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, ctx["text"])


def reset_driver_location(ctx):
    uid = ctx["user_id"]
    _PENDING_CITY.pop(uid, None)
    ctx["bot"].send_message(uid, "No problem — what city are you based in?")
