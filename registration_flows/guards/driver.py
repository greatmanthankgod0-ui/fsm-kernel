from kernel.kernel import register_guard


def driver_name_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 2


def driver_phone_guard(ctx):
    text = ctx.get("text", "").replace("+", "")
    return text.isdigit() and len(text) >= 10


def driver_nin_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) == 11


def driver_photo_guard(ctx):
    return ctx.get("content_type") == "photo"


def driver_account_guard(ctx):
    text = ctx.get("text", "")
    return text.isdigit() and len(text) >= 10


def driver_vehicle_guard(ctx):
    valid = ["🏍️ bike", "🚗 car", "🚐 van", "🚛 truck", "🏎️ tricycle (keke)"]
    return ctx.get("text", "").lower() in valid


def register_driver_guards():
    register_guard("driver_name_guard", driver_name_guard)
    register_guard("driver_phone_guard", driver_phone_guard)
    register_guard("driver_nin_guard", driver_nin_guard)
    register_guard("driver_photo_guard", driver_photo_guard)
    register_guard("driver_account_guard", driver_account_guard)
    register_guard("driver_vehicle_guard", driver_vehicle_guard)
