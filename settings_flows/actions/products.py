from kernel.kernel import register_action
from config import MAIN_DB
from storage.db import get_conn

_DRAFT = {}


def _draft(uid):
    if uid not in _DRAFT:
        _DRAFT[uid] = {"name": None, "price": None, "stock": None, "unit": None, "list": []}
    return _DRAFT[uid]


def start_add_product(ctx):
    uid = ctx["user_id"]
    _draft(uid)
    ctx["bot"].send_message(uid, "What's the product called?")


def save_product_name(ctx):
    uid = ctx["user_id"]
    _draft(uid)["name"] = ctx["text"]
    ctx["bot"].send_message(uid, f"*{ctx['text']}*\n\nHow much per unit? (just the number)", parse_mode="Markdown")


def save_product_price(ctx):
    uid = ctx["user_id"]
    _draft(uid)["price"] = float(ctx["text"])
    ctx["bot"].send_message(uid, "How many do you have in stock?")


def save_product_stock(ctx):
    uid = ctx["user_id"]
    _draft(uid)["stock"] = int(ctx["text"])

    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(row_width=2)
    units = ["Yards", "Litres", "Pieces", "Kg", "Bags", "Plates", "Packs", "Bottles"]
    for u in units:
        kb.add(InlineKeyboardButton(u, callback_data=f"unit_{u}"))
    kb.add(InlineKeyboardButton("✏️ Something else", callback_data="unit_custom"))
    ctx["bot"].send_message(uid, "What's it sold by?", reply_markup=kb)


def save_product_unit_custom_prompt(ctx):
    ctx["bot"].send_message(ctx["user_id"], "Type the unit (e.g. \"crates\", \"sets\"):")


def save_product_unit(ctx):
    uid = ctx["user_id"]
    d = _draft(uid)
    d["unit"] = ctx["text"]

    d["list"].append({
        "name": d["name"], "price": d["price"],
        "stock": d["stock"], "unit": d["unit"]
    })

    summary = "\n".join(
        f"• {p['name']} — ₦{p['price']:,.0f}/{p['unit']} ({p['stock']} in stock)"
        for p in d["list"]
    )

    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Add Another", callback_data="add_another_product"))
    kb.add(InlineKeyboardButton("✅ Done", callback_data="finish_product_list"))

    d["name"] = d["price"] = d["stock"] = d["unit"] = None

    ctx["bot"].send_message(uid,
        f"Added! Here's your list so far:\n\n{summary}",
        reply_markup=kb
    )


def finish_product_list(ctx):
    uid = ctx["user_id"]
    bot = ctx["bot"]
    d = _draft(uid)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    conn = get_conn(MAIN_DB)
    c = conn.cursor()
    for p in d["list"]:
        c.execute("""INSERT INTO products (seller_id, name, price, stock, unit, created_at)
                     VALUES (?,?,?,?,?,?)""",
                  (uid, p["name"], p["price"], p["stock"], p["unit"], now))
    conn.commit()
    conn.close()

    count = len(d["list"])
    _DRAFT.pop(uid, None)

    bot.send_message(uid, f"🎉 {count} product{'s' if count != 1 else ''} added to your shop.")


def register_product_actions():
    register_action("START_ADD_PRODUCT", start_add_product)
    register_action("SAVE_PRODUCT_NAME", save_product_name)
    register_action("SAVE_PRODUCT_PRICE", save_product_price)
    register_action("SAVE_PRODUCT_STOCK", save_product_stock)
    register_action("SAVE_PRODUCT_UNIT_CUSTOM_PROMPT", save_product_unit_custom_prompt)
    register_action("SAVE_PRODUCT_UNIT", save_product_unit)
    register_action("FINISH_PRODUCT_LIST", finish_product_list)
