from kernel.kernel import register_guard


def buyer_name_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def buyer_phone_guard(ctx):
    text = ctx.get("text", "").replace("+", "")
    return text.isdigit() and len(text) >= 10


def buyer_email_guard(ctx):
    text = ctx.get("text", "")
    return "@" in text and "." in text


def buyer_dob_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 8


def buyer_nin_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) == 11


def register_buyer_guards():
    register_guard("buyer_name_guard", buyer_name_guard)
    register_guard("buyer_phone_guard", buyer_phone_guard)
    register_guard("buyer_email_guard", buyer_email_guard)
    register_guard("buyer_dob_guard", buyer_dob_guard)
    register_guard("buyer_nin_guard", buyer_nin_guard)
