import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, ADMIN_ID, MAIN_DB
from storage.db import get_conn, init_all_dbs
from kernel.bootstrap import load_modules
from kernel.crash_log import safe_dispatch, init_crash_log
from kernel.registration_flows.rules.seller import resolve_event as seller_resolve_event
from kernel.registration_flows.rules.seller import resolve_callback_event as seller_resolve_callback
from kernel.registration_flows.rules.buyer import resolve_event as buyer_resolve_event
from kernel.registration_flows.rules.driver import resolve_event as driver_resolve_event
from kernel.registration_flows.rules.driver import resolve_callback_event as driver_resolve_callback
from kernel.registration_flows.rules.service import resolve_event as service_resolve_event
from kernel.registration_flows.rules.service import resolve_callback_event as service_resolve_callback

bot = telebot.TeleBot(TOKEN)

SELLER_STATES = {
    "TC_PENDING", "ASK_FULL_NAME", "ASK_SHOP_NAME", "ASK_PHONE", "ASK_EMAIL",
    "ASK_DOB", "ASK_NIN", "ASK_NIN_PHOTO", "ASK_FACE_PHOTO", "ASK_SHOP_PHOTO",
    "ASK_CITY", "CONFIRM_CITY", "ASK_LGA", "CONFIRM_LGA", "ASK_ADDRESS",
    "ASK_BANK", "ASK_ACCOUNT_NO", "ASK_ACCOUNT_NAME", "ASK_DELIVERY_HRS",
    "ASK_BIO", "CONFIRM_SUBMIT"
}

BUYER_STATES = {
    "REG_NAME", "REG_PHONE", "REG_EMAIL", "REG_DOB", "REG_NIN",
    "REG_CITY", "REG_LGA", "REG_ADDRESS"
}

DRIVER_STATES = {
    "TC_PENDING", "ASK_FULL_NAME", "ASK_PHONE", "ASK_EMAIL", "ASK_DOB",
    "ASK_NIN", "ASK_NIN_PHOTO", "ASK_FACE_PHOTO", "ASK_CITY", "ASK_LGA",
    "ASK_ADDRESS", "ASK_VEHICLE", "ASK_PLATE", "ASK_PLATE_PHOTO"
}

SERVICE_STATES = {
    "TC_PENDING", "ASK_FULL_NAME", "ASK_BUSINESS", "ASK_SKILL", "CONFIRM_SKILL",
    "ASK_PHONE", "ASK_EMAIL", "ASK_DOB", "ASK_NIN", "ASK_NIN_PHOTO", "ASK_FACE_PHOTO",
    "ASK_WORKPLACE_PHOTO", "ASK_CITY", "ASK_LGA", "ASK_ADDRESS", "ASK_BANK",
    "ASK_ACCOUNT_NO", "ASK_TURNAROUND", "ASK_BIO"
}


def _get_seller_state(user_id):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT state FROM seller_sessions WHERE seller_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def _set_seller_state(user_id, state):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("UPDATE seller_sessions SET state = ? WHERE seller_id = ?", (state, user_id))
    conn.commit()
    conn.close()


def _get_buyer_state(user_id):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT state FROM buyer_sessions WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def _get_driver_state(user_id):
    from config import DISPATCH_DB
    conn = get_conn(DISPATCH_DB)
    c = conn.cursor()
    c.execute("SELECT state FROM driver_sessions WHERE driver_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def _set_driver_state(user_id, state):
    from config import DISPATCH_DB
    conn = get_conn(DISPATCH_DB)
    c = conn.cursor()
    c.execute("UPDATE driver_sessions SET state = ? WHERE driver_id = ?", (state, user_id))
    conn.commit()
    conn.close()


def _get_service_state(user_id):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT state FROM service_seller_sessions WHERE seller_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def _set_service_state(user_id, state):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("UPDATE service_seller_sessions SET state = ? WHERE seller_id = ?", (state, user_id))
    conn.commit()
    conn.close()


def _set_buyer_state(user_id, state):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("UPDATE buyer_sessions SET state = ? WHERE user_id = ?", (state, user_id))
    conn.commit()
    conn.close()


def handle_buy_deep_link(bot, user_id, product_ref):
    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    c.execute("SELECT user_id FROM buyer_profiles WHERE user_id = ? AND is_approved = 1", (user_id,))
    registered = c.fetchone()
    conn.close()

    if registered:
        bot.send_message(user_id,
            f"Got it — pulling up that product for you. "
            f"(Product `{product_ref}` — order flow coming next)")
        return

    conn2 = get_conn(MAIN_DB)
    c2 = conn2.cursor()
    c2.execute("INSERT OR REPLACE INTO buyer_sessions (user_id, state, pending_product_id) VALUES (?, 'REG_NAME', ?)",
               (user_id, product_ref))
    conn2.commit()
    conn2.close()

    bot.send_message(user_id,
        "Good taste — let me lock that in for you.\n\n"
        "Quick thing first: I need to know who I'm dealing with. "
        "Takes two minutes, keeps everything safe for you.\n\n"
        "What's your name?"
    )


@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    try:
        if message.text and len(message.text.split()) > 1:
            param = message.text.split()[1]
            if param.startswith("buy_"):
                product_ref = param[4:]
                handle_buy_deep_link(bot, user_id, product_ref)
                return

        if user_id == ADMIN_ID:
            bot.reply_to(message, "👑 OnTabs Admin — kernel mode running.")
            return

        conn_check = get_conn(MAIN_DB)
        c_check = conn_check.cursor()
        c_check.execute("SELECT is_approved FROM sellers WHERE seller_id = ?", (user_id,))
        seller_row = c_check.fetchone()
        conn_check.close()
        is_approved_seller = seller_row and seller_row[0] == 1

        kb = InlineKeyboardMarkup()
        if is_approved_seller:
            kb.add(InlineKeyboardButton("🏪 My Shop", callback_data="open_my_shop"))
        else:
            kb.add(InlineKeyboardButton("🏪 Become a Seller", callback_data="start_seller_reg"))
        kb.add(InlineKeyboardButton("🛍️ Browse & Shop", callback_data="start_buyer_browse"))
        kb.add(InlineKeyboardButton("🚴 Become a Driver", callback_data="start_driver_reg"))
        kb.add(InlineKeyboardButton("🛠️ Offer a Service", callback_data="start_service_reg"))
        kb.add(InlineKeyboardButton("🗑️ Start Fresh", callback_data="reset_everything"))
        bot.reply_to(message, "⚡ Welcome to OnTabs.", reply_markup=kb)
    except Exception as e:
        from kernel.crash_log import log_crash
        log_crash(user_id, "START", "cmd_start", e)


@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def main_handler(message):
    user_id = message.chat.id
    text = message.text.strip() if message.text else ""
    content_type = message.content_type

    if text.startswith("/"):
        return  # let dedicated command handlers deal with this

    # ── Seller flow ──
    seller_state = _get_seller_state(user_id)
    print(f"DEBUG main_handler: seller_state={seller_state} text={text!r}")
    if seller_state and seller_state in SELLER_STATES:
        if seller_state in ("TC_PENDING", "CONFIRM_SUBMIT", "CONFIRM_CITY", "CONFIRM_LGA"):
            return  # button-only states, ignore stray text

        event = seller_resolve_event(seller_state, text, content_type)
        if not event:
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
            return

        ctx = {
            "bot": bot, "user_id": user_id, "text": text,
            "content_type": content_type, "message_id": message.message_id,
            "oil": False, "session": {}
        }
        new_state, result = safe_dispatch(seller_state, event, ctx)
        if result == "OK":
            if ctx.get("needs_confirm") and seller_state == "ASK_CITY":
                _set_seller_state(user_id, "CONFIRM_CITY")
            elif ctx.get("needs_confirm") and seller_state == "ASK_LGA":
                _set_seller_state(user_id, "CONFIRM_LGA")
            else:
                _set_seller_state(user_id, new_state)
        elif result == "GUARD_FAIL":
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
        return

    # ── Buyer flow ──
    buyer_state = _get_buyer_state(user_id)
    if buyer_state and buyer_state in BUYER_STATES:
        event = buyer_resolve_event(buyer_state, text, content_type)
        if not event:
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
            return

        ctx = {
            "bot": bot, "user_id": user_id, "text": text,
            "content_type": content_type, "message_id": message.message_id,
            "session": {}
        }
        new_state, result = safe_dispatch(buyer_state, event, ctx)
        if result == "OK":
            if new_state == "BROWSING":
                conn = get_conn(MAIN_DB)
                c = conn.cursor()
                c.execute("DELETE FROM buyer_sessions WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
            else:
                _set_buyer_state(user_id, new_state)
        elif result == "GUARD_FAIL":
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
        return

    # ── Driver flow ──
    driver_state = _get_driver_state(user_id)
    if driver_state and driver_state in DRIVER_STATES:
        if driver_state == "TC_PENDING":
            return  # button-only state, ignore stray text

        event = driver_resolve_event(driver_state, text, content_type)
        if not event:
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
            return

        ctx = {
            "bot": bot, "user_id": user_id, "text": text,
            "content_type": content_type, "message_id": message.message_id,
            "session": {}
        }
        new_state, result = safe_dispatch(driver_state, event, ctx)
        if result == "OK":
            _set_driver_state(user_id, new_state)
        elif result == "GUARD_FAIL":
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
        return


    # ── Service flow ──
    service_state = _get_service_state(user_id)
    if service_state and service_state in SERVICE_STATES:
        if service_state == "TC_PENDING":
            return  # button-only state, ignore stray text

        event = service_resolve_event(service_state, text, content_type)
        if not event:
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
            return

        ctx = {
            "bot": bot, "user_id": user_id, "text": text,
            "content_type": content_type, "message_id": message.message_id,
            "session": {}
        }
        new_state, result = safe_dispatch(service_state, event, ctx)
        if result == "OK":
            if ctx.get("needs_confirm"):
                _set_service_state(user_id, "CONFIRM_SKILL")
            else:
                _set_service_state(user_id, new_state)
        elif result == "GUARD_FAIL":
            bot.send_message(user_id, "Hmm, that doesn't look quite right — mind trying again?")
        return


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "reset_everything":
        conn = get_conn(MAIN_DB)
        c = conn.cursor()
        c.execute("DELETE FROM seller_sessions WHERE seller_id = ?", (user_id,))
        c.execute("DELETE FROM buyer_sessions WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM sellers WHERE seller_id = ?", (user_id,))
        c.execute("DELETE FROM buyer_profiles WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM service_seller_sessions WHERE seller_id = ?", (user_id,))
        c.execute("DELETE FROM service_sellers WHERE seller_id = ?", (user_id,))
        conn.commit()
        conn.close()

        from config import DISPATCH_DB
        conn2 = get_conn(DISPATCH_DB)
        c2 = conn2.cursor()
        c2.execute("DELETE FROM driver_sessions WHERE driver_id = ?", (user_id,))
        c2.execute("DELETE FROM drivers WHERE driver_id = ?", (user_id,))
        conn2.commit()
        conn2.close()

        from kernel.registration_flows.actions.buyer import _DRAFT
        _DRAFT.pop(user_id, None)
        bot.send_message(user_id, "🗑️ Wiped clean — all roles. Hit /start whenever you're ready to go again.")
        return

    if data == "start_seller_reg":
        conn = get_conn(MAIN_DB)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO seller_sessions (seller_id, state) VALUES (?, 'TC_PENDING')", (user_id,))
        conn.commit()
        conn.close()
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Agree", callback_data="seller_agree"),
            InlineKeyboardButton("❌ Decline", callback_data="seller_decline")
        )
        bot.send_message(user_id,
            "Before we get started — a quick word: be honest about what you're selling, "
            "price fairly, and deliver when you say you will. That's really all OnTabs asks. "
            "Sound fair?",
            reply_markup=kb
        )
        return

    if data == "start_driver_reg":
        from config import DISPATCH_DB
        conn = get_conn(DISPATCH_DB)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO driver_sessions (driver_id, state) VALUES (?, 'TC_PENDING')", (user_id,))
        conn.commit()
        conn.close()
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Agree", callback_data="driver_agree"),
            InlineKeyboardButton("❌ Decline", callback_data="driver_decline")
        )
        bot.send_message(user_id,
            "One quick thing before we start — once you accept a delivery job, "
            "the price is locked for that trip. No changing it mid-route, for "
            "you or the customer. Fair to everyone that way.\n\nSound good?",
            reply_markup=kb
        )
        return

    if data == "start_service_reg":
        conn = get_conn(MAIN_DB)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO service_seller_sessions (seller_id, state) VALUES (?, 'TC_PENDING')", (user_id,))
        conn.commit()
        conn.close()
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Agree", callback_data="service_agree"),
            InlineKeyboardButton("❌ Decline", callback_data="service_decline")
        )
        bot.send_message(user_id,
            "Quick word before we start — be upfront about pricing and timing "
            "with customers, and show up when you say you will. That's it.\n\n"
            "Sound fair?",
            reply_markup=kb
        )
        return

    if data == "start_buyer_browse":
        conn = get_conn(MAIN_DB)
        c = conn.cursor()
        c.execute("SELECT user_id FROM buyer_profiles WHERE user_id = ? AND is_approved = 1", (user_id,))
        registered = c.fetchone()
        conn.close()
        if registered:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("🛍️ Browse OnTabs Discovery", url="https://t.me/ontabsdiscovery"))
            bot.send_message(user_id, "Here's where the action is 👇", reply_markup=kb)
        else:
            conn2 = get_conn(MAIN_DB)
            c2 = conn2.cursor()
            c2.execute("INSERT OR REPLACE INTO buyer_sessions (user_id, state) VALUES (?, 'REG_NAME')", (user_id,))
            conn2.commit()
            conn2.close()
            bot.send_message(user_id,
                "Before you start browsing — quick setup so checkout is smooth later. "
                "What's your name?"
            )
        return

    # ── Seller button events ──
    state = _get_seller_state(user_id)
    if state:
        event = seller_resolve_callback(state, data)
        if event:
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "oil": False, "session": {}
            }
            new_state, result = safe_dispatch(state, event, ctx)
            if result == "OK":
                _set_seller_state(user_id, new_state)
                if new_state == "ASK_FULL_NAME":
                    bot.send_message(user_id, "What is your full legal name? 👇")
            return

    # ── Driver button events ──
    driver_state = _get_driver_state(user_id)
    if driver_state:
        event = driver_resolve_callback(driver_state, data)
        if event:
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "session": {}
            }
            new_state, result = safe_dispatch(driver_state, event, ctx)
            if result == "OK":
                _set_driver_state(user_id, new_state)
                if new_state == "ASK_FULL_NAME":
                    bot.send_message(user_id, "What's your full name? 👇")
            return


    # ── Seller city/LGA confirmation (dynamic callback data) ──
    seller_state = _get_seller_state(user_id)
    if seller_state == "CONFIRM_CITY":
        if data.startswith("city_use_"):
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "oil": False, "session": {}
            }
            new_state, result = safe_dispatch("CONFIRM_CITY", "CITY_CONFIRMED", ctx)
            if result == "OK":
                _set_seller_state(user_id, new_state)
            return
        if data == "city_keep":
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "oil": False, "session": {}
            }
            new_state, result = safe_dispatch("CONFIRM_CITY", "CITY_KEPT", ctx)
            if result == "OK":
                _set_seller_state(user_id, new_state)
            return

    if seller_state == "CONFIRM_LGA":
        if data.startswith("lga_use_"):
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "oil": False, "session": {}
            }
            new_state, result = safe_dispatch("CONFIRM_LGA", "LGA_CONFIRMED", ctx)
            if result == "OK":
                _set_seller_state(user_id, new_state)
            return
        if data == "lga_keep":
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "oil": False, "session": {}
            }
            new_state, result = safe_dispatch("CONFIRM_LGA", "LGA_KEPT", ctx)
            if result == "OK":
                _set_seller_state(user_id, new_state)
            return

    # ── Service skill confirmation (dynamic callback data) ──
    service_state = _get_service_state(user_id)
    if service_state == "CONFIRM_SKILL":
        if data.startswith("svc_skill_use_"):
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "session": {}
            }
            new_state, result = safe_dispatch("CONFIRM_SKILL", "SKILL_CONFIRMED", ctx)
            if result == "OK":
                _set_service_state(user_id, new_state)
            return
        if data == "svc_skill_keep":
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "session": {}
            }
            new_state, result = safe_dispatch("CONFIRM_SKILL", "SKILL_KEPT", ctx)
            if result == "OK":
                _set_service_state(user_id, new_state)
            return

    # ── Service button events ──
    if service_state:
        event = service_resolve_callback(service_state, data)
        if event:
            ctx = {
                "bot": bot, "user_id": user_id, "text": data,
                "content_type": "callback", "message_id": call.message.message_id,
                "session": {}
            }
            new_state, result = safe_dispatch(service_state, event, ctx)
            if result == "OK":
                _set_service_state(user_id, new_state)
                if new_state == "ASK_FULL_NAME":
                    bot.send_message(user_id, "What's your full name? 👇")
            return


if __name__ == "__main__":
    init_all_dbs()
    init_crash_log()
    load_modules()
    print("✅ OnTabs V10 (kernel mode) is LIVE.")
    bot.infinity_polling()

