def agree_guard(ctx):
    return ctx.get("text", "").strip().lower() == "agree"


def name_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def phone_guard(ctx):
    text = ctx.get("text", "")
    return text.replace("+", "").isdigit() and len(text) >= 10


def email_guard(ctx):
    text = ctx.get("text", "")
    return "@" in text and "." in text


def nin_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) == 11


def city_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def lga_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def bank_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def account_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) >= 10


def delivery_guard(ctx):
    return ctx.get("text", "").strip() in ["6", "12", "24", "48"]
