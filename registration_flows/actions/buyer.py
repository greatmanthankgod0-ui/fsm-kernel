from kernel.kernel import register_action
from config import MAIN_DB
from storage.db import get_conn

_DRAFT = {}


def _draft(uid):
    if uid not in _DRAFT:
        _DRAFT[uid] = {}
    return _DRAFT[uid]


def save_buyer_name(ctx):
    uid = ctx["user_id"]
    name = ctx["text"]
    _draft(uid)["full_name"] = name
    first = name.split()[0]
    ctx["bot"].send_message(uid,
        f"Nice to meet you, {first} 👋\n\nDrop your phone number — sellers might need it for delivery.")


def save_buyer_phone(ctx):
    uid = ctx["user_id"]
    _draft(uid)["phone"] = ctx["text"]
    ctx["bot"].send_message(uid, "Got it. What's your email?")


def save_buyer_email(ctx):
    uid = ctx["user_id"]
    _draft(uid)["email"] = ctx["text"]
    ctx["bot"].send_message(uid, "Thanks. When's your birthday? (DD/MM/YYYY)")


def save_buyer_dob(ctx):
    uid = ctx["user_id"]
    _draft(uid)["dob"] = ctx["text"]
    ctx["bot"].send_message(uid,
        "One more thing — your NIN.\n\n"
        "I know it feels like a lot for shopping, but it keeps fraud out and "
        "protects everyone on here, including you. 🔒\n\n11 digits:")


def save_buyer_nin(ctx):
    uid = ctx["user_id"]
    _draft(uid)["nin"] = ctx["text"]
    ctx["bot"].send_message(uid, "Noted. ✅\n\nWhat city are you in?")


def save_buyer_city(ctx):
    uid = ctx["user_id"]
    _draft(uid)["city"] = ctx["text"]
    ctx["bot"].send_message(uid, f"{ctx['text']}, got it.\n\nWhich LGA?")


def save_buyer_lga(ctx):
    uid = ctx["user_id"]
    _draft(uid)["lga"] = ctx["text"]
    ctx["bot"].send_message(uid,
        "Last one — your delivery address. Street, house number, "
        "and a landmark if you've got one.")


def save_buyer_address(ctx):
    from datetime import datetime, timezone
    uid = ctx["user_id"]
    bot = ctx["bot"]
    now = datetime.now(timezone.utc).isoformat()

    d = _draft(uid)
    d["address"] = ctx["text"]

    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO buyer_profiles
        (user_id, full_name, phone, email, dob, nin, city, lga, address, is_approved, joined_at)
        VALUES (?,?,?,?,?,?,?,?,?,1,?)""",
        (uid, d.get("full_name"), d.get("phone"), d.get("email"), d.get("dob"),
         d.get("nin"), d.get("city"), d.get("lga"), d.get("address"), now))
    c.execute("DELETE FROM buyer_sessions WHERE user_id = ?", (uid,))
    conn.commit()
    conn.close()

    first = d.get("full_name", "there").split()[0]
    _DRAFT.pop(uid, None)

    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛍️ Browse OnTabs Discovery", url="https://t.me/ontabsdiscovery"))
    bot.send_message(uid,
        f"You're all set, {first} 🎉\n\n"
        f"Your money's safe with us until your order actually arrives — that's the whole point.\n\n"
        f"Go take a look at what's on offer 👇",
        reply_markup=kb
    )


def register_buyer_actions():
    register_action("SAVE_BUYER_NAME", save_buyer_name)
    register_action("SAVE_BUYER_PHONE", save_buyer_phone)
    register_action("SAVE_BUYER_EMAIL", save_buyer_email)
    register_action("SAVE_BUYER_DOB", save_buyer_dob)
    register_action("SAVE_BUYER_NIN", save_buyer_nin)
    register_action("SAVE_BUYER_CITY", save_buyer_city)
    register_action("SAVE_BUYER_LGA", save_buyer_lga)
    register_action("SAVE_BUYER_ADDRESS", save_buyer_address)


# ── City / LGA fuzzy match helpers ──

_PENDING_CITY = {}


def _get_pending_city(user_id):
    return _PENDING_CITY.get(user_id)


def save_buyer_confirmed_city(ctx):
    city = ctx["text"].replace("city_use_", "")
    _PENDING_CITY[ctx["user_id"]] = city
    _update(ctx, "city", city)
    ctx["bot"].send_message(ctx["user_id"], f"📍 {city} — got it.\n\nWhich LGA?")


def save_buyer_kept_city(ctx):
    uid = ctx["user_id"]
    from config import MAIN_DB
    from storage.db import get_conn
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT city FROM buyer_sessions WHERE user_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    city = row[0] if row else "your city"
    _PENDING_CITY[uid] = city
    ctx["bot"].send_message(uid, f"📍 {city} — got it.\n\nWhich LGA?")


def save_buyer_confirmed_lga(ctx):
    lga = ctx["text"].replace("lga_use_", "")
    _update(ctx, "lga", lga)
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_buyer_kept_lga(ctx):
    uid = ctx["user_id"]
    from config import MAIN_DB
    from storage.db import get_conn
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT lga FROM buyer_sessions WHERE user_id = ?", (uid,))
    row = c.fetchone()
    conn.close()
    lga = row[0] if row else "your LGA"
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, lga)


def save_buyer_lga_and_confirm(ctx):
    _update(ctx, "lga", ctx["text"])
    uid = ctx["user_id"]
    city = _PENDING_CITY.get(uid, "")
    from kernel.text_helpers import send_location_confirm
    send_location_confirm(ctx["bot"], uid, city, ctx["text"])


def reset_buyer_location(ctx):
    uid = ctx["user_id"]
    _PENDING_CITY.pop(uid, None)
    ctx["bot"].send_message(uid, "No problem — what city are you in?")
