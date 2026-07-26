from kernel.kernel import register_action
from config import ADMIN_ID, MAIN_DB
from storage.db import get_conn


def _update(ctx, field, value):
    uid = ctx["user_id"]
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute(f"UPDATE service_seller_sessions SET {field} = ? WHERE seller_id = ?", (value, uid))
    conn.commit()
    conn.close()


def save_svc_name(ctx):
    name = ctx["text"]
    _update(ctx, "full_name", name)
    first = name.split()[0]
    ctx["bot"].send_message(ctx["user_id"],
        f"Good to meet you, {first} 🙂\n\nWhat's your business called?")


def save_svc_business(ctx):
    _update(ctx, "business_name", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        f"*{ctx['text']}* — nice.\n\nWhat service do you offer? "
        f"(Barbering, Catering, Tailoring, Laundry, whatever you do)",
        parse_mode="Markdown")


def save_svc_skill(ctx):
    from kernel.text_helpers import suggest_service_correction
    text = ctx["text"]
    suggestion = suggest_service_correction(text)

    if suggestion:
        _update(ctx, "skill_category", text)  # temp storage, overwritten properly below
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(f"✅ {suggestion}", callback_data=f"svc_skill_use_{suggestion}"))
        kb.add(InlineKeyboardButton(f"Keep \"{text}\"", callback_data="svc_skill_keep"))
        ctx["bot"].send_message(ctx["user_id"],
            f"Did you mean *{suggestion}*?",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        ctx["needs_confirm"] = True
        return

    _update(ctx, "skill_category", text)
    ctx["bot"].send_message(ctx["user_id"], f"{text} — got it.\n\nYour phone number?")


def use_suggested_skill(ctx):
    skill = ctx["text"].replace("svc_skill_use_", "")
    _update(ctx, "skill_category", skill)
    ctx["bot"].send_message(ctx["user_id"], f"{skill} — got it.\n\nYour phone number?")


def keep_typed_skill(ctx):
    uid = ctx["user_id"]
    from config import MAIN_DB
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT skill_category FROM service_seller_sessions WHERE seller_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    skill = row[0] if row else "your service"
    ctx["bot"].send_message(uid, f"Got it, keeping *{skill}*.\n\nYour phone number?", parse_mode="Markdown")


def save_svc_phone(ctx):
    _update(ctx, "phone", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Email address?")


def save_svc_email(ctx):
    _update(ctx, "email", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "When's your birthday? (DD/MM/YYYY)")


def save_svc_dob(ctx):
    _update(ctx, "dob", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Your NIN — 11 digits.")


def save_svc_nin(ctx):
    _update(ctx, "nin", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Send a clear photo of your NIN slip 📸")


def save_svc_nin_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(ADMIN_ID, f"🪪 NIN photo from service seller {user_id}")
    bot.send_message(user_id, "Got it. Now a quick selfie so we know it's you 🤳")


def save_svc_face_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(user_id,
        "That's you. 😊\n\nNow send a photo of where you work — your shop, "
        "workspace, or wherever you do the job. Helps customers trust it's real.")


def save_svc_workplace_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(ADMIN_ID, f"🏠 Workplace photo from service seller {user_id}")
    bot.send_message(user_id, "Looking good.\n\nWhat city are you based in?")


def save_svc_city(ctx):
    _update(ctx, "city", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], f"{ctx['text']}, noted.\n\nWhich LGA?")


def save_svc_lga(ctx):
    _update(ctx, "lga", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Full address?")


def save_svc_address(ctx):
    _update(ctx, "address", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Which bank do you use for payments?")


def save_svc_bank(ctx):
    _update(ctx, "bank_name", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], f"{ctx['text']} — got it.\n\nAccount number?")


def save_svc_account_no(ctx):
    _update(ctx, "account_no", ctx["text"])
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KeyboardButton("Same day"), KeyboardButton("Next day"))
    kb.row(KeyboardButton("2-3 days"), KeyboardButton("A week"))
    ctx["bot"].send_message(ctx["user_id"],
        "Got it. Last bit — how long does a typical job take you?", reply_markup=kb)


def save_svc_turnaround(ctx):
    hrs_map = {"Same day": 12, "Next day": 24, "2-3 days": 72, "A week": 168}
    hrs = hrs_map.get(ctx["text"], 24)
    _update(ctx, "delivery_hrs", hrs)
    from telebot.types import ReplyKeyboardRemove
    ctx["bot"].send_message(ctx["user_id"],
        "Tell me a bit about what you do — what makes your work good?\n\n"
        "Or type SKIP.",
        reply_markup=ReplyKeyboardRemove())


def save_svc_bio(ctx):
    bio     = None if ctx["text"].lower() == "skip" else ctx["text"]
    user_id = ctx["user_id"]
    bot     = ctx["bot"]
    _update(ctx, "bio", bio)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("""SELECT full_name, business_name, skill_category, phone, email,
                        dob, nin, city, lga, address, bank_name, account_no,
                        delivery_hrs, bio
                 FROM service_seller_sessions WHERE seller_id = ?""", (user_id,))
    s = c.fetchone()

    c.execute("""INSERT OR REPLACE INTO service_sellers
        (seller_id, full_name, business_name, skill_category, phone, email,
         dob, nin, city, lga, address, bank_name, account_no, delivery_hrs,
         is_approved, tc_agreed, tc_agreed_at, joined_at, bio)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,1,?,?,?)""",
        (user_id, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8],
         s[9], s[10], s[11], s[12], now, now, bio))
    c.execute("DELETE FROM service_seller_sessions WHERE seller_id = ?", (user_id,))
    conn.commit()
    conn.close()

    bot.send_message(user_id,
        f"You're in the queue, {s[0].split()[0]} 🎉\n\n"
        f"We'll take a look and get you live soon.")

    bot.send_message(ADMIN_ID,
        f"🛠️ New Service Seller\n\n"
        f"Name: {s[0]}\nID: {user_id}\n"
        f"Business: {s[1]}\nService: {s[2]}\n"
        f"📞 {s[3]} | 📧 {s[4]}\n"
        f"DOB: {s[5]} | NIN: {s[6]}\n"
        f"📍 {s[7]}, {s[8]} — {s[9]}\n"
        f"🏦 {s[10]} — {s[11]}\n"
        f"⏱ {s[12]}hrs turnaround\n\n"
        f"/approveservice {user_id}"
    )


def register_service_actions():
    register_action("SAVE_SVC_NAME", save_svc_name)
    register_action("SAVE_SVC_BUSINESS", save_svc_business)
    register_action("SAVE_SVC_SKILL", save_svc_skill)
    register_action("USE_SUGGESTED_SKILL", use_suggested_skill)
    register_action("KEEP_TYPED_SKILL", keep_typed_skill)
    register_action("SAVE_SVC_PHONE", save_svc_phone)
    register_action("SAVE_SVC_EMAIL", save_svc_email)
    register_action("SAVE_SVC_DOB", save_svc_dob)
    register_action("SAVE_SVC_NIN", save_svc_nin)
    register_action("SAVE_SVC_NIN_PHOTO", save_svc_nin_photo)
    register_action("SAVE_SVC_FACE_PHOTO", save_svc_face_photo)
    register_action("SAVE_SVC_WORKPLACE_PHOTO", save_svc_workplace_photo)
    register_action("SAVE_SVC_CITY", save_svc_city)
    register_action("SAVE_SVC_LGA", save_svc_lga)
    register_action("SAVE_SVC_ADDRESS", save_svc_address)
    register_action("SAVE_SVC_BANK", save_svc_bank)
    register_action("SAVE_SVC_ACCOUNT_NO", save_svc_account_no)
    register_action("SAVE_SVC_TURNAROUND", save_svc_turnaround)
    register_action("SAVE_SVC_BIO", save_svc_bio)


# ── City / LGA fuzzy match helpers ──

_PENDING_CITY = {}


def _get_pending_city(user_id):
    return _PENDING_CITY.get(user_id)


def save_svc_confirmed_city(ctx):
    city = ctx["text"].replace("city_use_", "")
    _PENDING_CITY[ctx["user_id"]] = city
    _update(ctx, "city", city)
    ctx["bot"].send_message(ctx["user_id"], f"📍 {city} — got it.\n\nWhich LGA?")


def save_svc_kept_city(ctx):
    uid = ctx["user_id"]
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT city FROM service_seller_sessions WHERE seller_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    city = row[0] if row else "your city"
    _PENDING_CITY[uid] = city
    ctx["bot"].send_message(uid, f"📍 {city} — got it.\n\nWhich LGA?")


def save_svc_confirmed_lga(ctx):
    lga = ctx["text"].replace("lga_use_", "")
    _update(ctx, "lga", lga)
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_svc_kept_lga(ctx):
    uid = ctx["user_id"]
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT lga FROM service_seller_sessions WHERE seller_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    lga = row[0] if row else "your LGA"
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_svc_lga_and_confirm(ctx):
    _update(ctx, "lga", ctx["text"])
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, ctx["text"])


def reset_svc_location(ctx):
    uid = ctx["user_id"]
    _PENDING_CITY.pop(uid, None)
    ctx["bot"].send_message(uid, "No problem — what city are you based in?")
