from kernel.kernel import register_action
from config import ADMIN_ID
from wiring.seller import update_field as _update_field


def _update(ctx, field, value):
    oil = ctx.get("oil", False)
    uid = ctx["user_id"]
    _update_field(uid, field, value, oil=oil)


def save_full_name(ctx):
    name = ctx["text"]
    _update(ctx, "full_name", name)
    first = name.split()[0]
    ctx["bot"].send_message(ctx["user_id"],
        f"Nice to meet you, {first} 👋\n\nWhat should we call your shop?")


def save_shop_name(ctx):
    _update(ctx, "shop_name", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        f"*{ctx['text']}* — good name. 🏪\n\nWhat's the best number to reach you on?",
        parse_mode="Markdown")


def save_phone(ctx):
    _update(ctx, "phone", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Got that saved. What's your email?")


def save_email(ctx):
    _update(ctx, "email", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "Perfect. When's your birthday? (DD/MM/YYYY)")


def save_dob(ctx):
    _update(ctx, "dob", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        "Thanks for that.\n\nNow I need your NIN — 11 digits, no spaces.")


def save_nin(ctx):
    _update(ctx, "nin", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        "Almost done with the paperwork.\n\nSend a clear photo of your NIN slip 📸")


def save_nin_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(ADMIN_ID, f"🪪 NIN photo from seller {user_id}")
    bot.send_message(user_id, "Got it, thank you.\n\nNow a quick selfie so we know it's really you 🤳")


def save_face_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(user_id,
        "That's you alright. 😊\n\nOne more photo — your shop front, gate, or street, "
        "so buyers know where to find you.")


def save_shop_photo(ctx):
    bot     = ctx["bot"]
    user_id = ctx["user_id"]
    msg_id  = ctx["message_id"]
    bot.forward_message(ADMIN_ID, user_id, msg_id)
    bot.send_message(ADMIN_ID, f"🏪 Shop photo from seller {user_id}")
    bot.send_message(user_id, "Looking good. What city is your shop in?")


def save_city(ctx):
    _update(ctx, "city", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], f"{ctx['text']}, noted.\n\nWhich LGA?")


def save_lga(ctx):
    _update(ctx, "lga", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        "Last bit of location info — your full shop address?")


def save_address(ctx):
    _update(ctx, "address", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"],
        "Now for payments — which bank do you use? (GTBank, Opay, Palmpay, whatever works)")


def save_bank(ctx):
    _update(ctx, "bank_name", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], f"{ctx['text']} — got it.\n\nAccount number?")


def save_account_no(ctx):
    _update(ctx, "account_no", ctx["text"])
    ctx["bot"].send_message(ctx["user_id"], "And the name on that account?")


def save_account_name(ctx):
    _update(ctx, "account_name", ctx["text"])
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KeyboardButton("6 hours"), KeyboardButton("12 hours"))
    kb.row(KeyboardButton("24 hours"), KeyboardButton("48 hours"))
    ctx["bot"].send_message(ctx["user_id"],
        "We're almost there.\n\nHow long does delivery usually take you?",
        reply_markup=kb)


def save_delivery_hrs(ctx):
    hrs_map = {"6 hours": 6, "12 hours": 12, "24 hours": 24, "48 hours": 48}
    hrs = hrs_map[ctx["text"]]
    _update(ctx, "delivery_hrs", hrs)
    from telebot.types import ReplyKeyboardRemove
    ctx["bot"].send_message(ctx["user_id"],
        "Last thing — tell me a little about your shop. What do you sell, what makes it good?\n\n"
        "Or just type SKIP if you'd rather not.",
        reply_markup=ReplyKeyboardRemove())


def save_bio_draft(ctx):
    bio = None if ctx["text"].lower() == "skip" else ctx["text"]
    _update(ctx, "bio", bio)

    oil     = ctx.get("oil", False)
    user_id = ctx["user_id"]
    bot     = ctx["bot"]

    from wiring.seller import get_session_row
    s = get_session_row(user_id, oil=oil)

    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Submit", callback_data="seller_submit"),
        InlineKeyboardButton("❌ Cancel", callback_data="seller_cancel")
    )

    bot.send_message(user_id,
        f"Here's what I've got for *{s[1]}*:\n\n"
        f"📍 {s[6]}, {s[7]}\n"
        f"🏦 {s[9]} — {s[10]}\n"
        f"⏱ Delivery in {s[12]}hrs\n"
        f"Bio: {bio or 'None'}\n\n"
        f"Look right to you?",
        reply_markup=kb,
        parse_mode="Markdown"
    )


def submit_application(ctx):
    oil     = ctx.get("oil", False)
    user_id = ctx["user_id"]
    bot     = ctx["bot"]

    from wiring.seller import get_session_row, save_seller, delete_session
    s = get_session_row(user_id, oil=oil)

    if not s:
        bot.send_message(user_id, "Hmm, something went sideways there. Let's start over — type /start.")
        return

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    bio = s[13] if len(s) > 13 else None

    save_seller({
        "seller_id": user_id, "full_name": s[0], "shop_name": s[1],
        "phone": s[2], "email": s[3], "dob": s[4], "nin": s[5],
        "city": s[6], "lga": s[7], "address": s[8],
        "bank_name": s[9], "account_no": s[10], "account_name": s[11],
        "delivery_hrs": s[12], "bio": bio, "is_approved": 0,
        "tc_agreed": 1, "tc_agreed_at": now, "joined_at": now, "oil": oil
    })
    delete_session(user_id, oil=oil)

    bot.send_message(user_id,
        f"You're in the queue, {s[0].split()[0]} 🎉\n\n"
        f"We just need to look things over, then you're live. "
        f"Won't take long.")

    bot.send_message(ADMIN_ID,
        f"🏪 New {'Oil' if oil else 'Multi-Store'} Seller\n\n"
        f"Name: {s[0]}\nID: {user_id}\nShop: {s[1]}\n"
        f"📍 {s[6]}, {s[7]} — {s[8]}\n"
        f"📞 {s[2]} | 📧 {s[3]}\n"
        f"DOB: {s[4]} | NIN: {s[5]}\n"
        f"🏦 {s[9]} — {s[10]} ({s[11]})\n"
        f"⏱ {s[12]}hrs\n\n"
        f"/approve {user_id}{'_oil' if oil else ''}"
    )


def cancel_application(ctx):
    oil     = ctx.get("oil", False)
    user_id = ctx["user_id"]
    bot     = ctx["bot"]
    from wiring.seller import delete_session
    delete_session(user_id, oil=oil)
    bot.send_message(user_id, "No problem — nothing's saved. Come back whenever you're ready, just type /start.")


def register_seller_actions():
    register_action("SAVE_FULL_NAME", save_full_name)
    register_action("SAVE_SHOP_NAME", save_shop_name)
    register_action("SAVE_PHONE", save_phone)
    register_action("SAVE_EMAIL", save_email)
    register_action("SAVE_DOB", save_dob)
    register_action("SAVE_NIN", save_nin)
    register_action("SAVE_NIN_PHOTO", save_nin_photo)
    register_action("SAVE_FACE_PHOTO", save_face_photo)
    register_action("SAVE_SHOP_PHOTO", save_shop_photo)
    register_action("SAVE_CITY", save_city)
    register_action("SAVE_LGA", save_lga)
    register_action("SAVE_ADDRESS", save_address)
    register_action("SAVE_BANK", save_bank)
    register_action("SAVE_ACCOUNT_NO", save_account_no)
    register_action("SAVE_ACCOUNT_NAME", save_account_name)
    register_action("SAVE_DELIVERY_HRS", save_delivery_hrs)
    register_action("SAVE_BIO_DRAFT", save_bio_draft)
    register_action("SUBMIT_APPLICATION", submit_application)
    register_action("CANCEL_APPLICATION", cancel_application)


# ── City / LGA fuzzy match helpers ──

_PENDING_CITY = {}  # user_id -> city (temp, until location confirmed)


def _get_pending_city(user_id):
    return _PENDING_CITY.get(user_id)


def save_confirmed_city(ctx):
    skill = ctx["text"].replace("city_use_", "")
    _PENDING_CITY[ctx["user_id"]] = skill
    _update(ctx, "city", skill)
    ctx["bot"].send_message(ctx["user_id"], f"📍 {skill} — got it.\n\nWhich LGA?")


def save_kept_city(ctx):
    uid = ctx["user_id"]
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT city FROM seller_sessions WHERE seller_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    city = row[0] if row else "your city"
    _PENDING_CITY[uid] = city
    ctx["bot"].send_message(uid, f"📍 {city} — got it.\n\nWhich LGA?")


def save_confirmed_lga(ctx):
    lga = ctx["text"].replace("lga_use_", "")
    _update(ctx, "lga", lga)
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_kept_lga(ctx):
    uid = ctx["user_id"]
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT lga FROM seller_sessions WHERE seller_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    lga = row[0] if row else "your LGA"
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_lga_and_confirm(ctx):
    _update(ctx, "lga", ctx["text"])
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, ctx["text"])


def reset_location(ctx):
    uid = ctx["user_id"]
    _PENDING_CITY.pop(uid, None)
    ctx["bot"].send_message(uid, "No problem — what city is your shop in?")
