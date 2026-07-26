from kernel.kernel import register_guard
def name_guard(ctx):
    text = ctx.get("text", "")
    return len(text.strip()) >= 2


def phone_guard(ctx):
    text = ctx.get("text", "").replace("+", "")
    return text.isdigit() and len(text) >= 10


def email_guard(ctx):
    text = ctx.get("text", "")
    return "@" in text and "." in text


def dob_guard(ctx):
    text = ctx.get("text", "")
    return len(text.strip()) >= 8


def nin_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) == 11


def account_no_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) >= 10


def photo_guard(ctx):
    return ctx.get("content_type") == "photo"


def delivery_hrs_guard(ctx):
    valid = ["6 hours", "12 hours", "24 hours", "48 hours"]
    return ctx.get("text", "") in valid


def register_seller_guards():
    register_guard("name_guard", name_guard)
    register_guard("phone_guard", phone_guard)
    register_guard("email_guard", email_guard)
    register_guard("dob_guard", dob_guard)
    register_guard("nin_guard", nin_guard)
    register_guard("account_no_guard", account_no_guard)
    register_guard("photo_guard", photo_guard)
    register_guard("delivery_hrs_guard", delivery_hrs_guard)
