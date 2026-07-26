from kernel.kernel import register_guard


def svc_name_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def svc_phone_guard(ctx):
    text = ctx.get("text", "").replace("+", "")
    return text.isdigit() and len(text) >= 10


def svc_email_guard(ctx):
    text = ctx.get("text", "")
    return "@" in text and "." in text


def svc_nin_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) == 11


def svc_photo_guard(ctx):
    return ctx.get("content_type") == "photo"


def svc_account_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) >= 10


def register_service_guards():
    register_guard("svc_name_guard", svc_name_guard)
    register_guard("svc_phone_guard", svc_phone_guard)
    register_guard("svc_email_guard", svc_email_guard)
    register_guard("svc_nin_guard", svc_nin_guard)
    register_guard("svc_photo_guard", svc_photo_guard)
    register_guard("svc_account_guard", svc_account_guard)
