from kernel.kernel import register_guard


def product_name_guard(ctx):
    return len(ctx.get("text", "").strip()) >= 1


def product_price_guard(ctx):
    text = ctx.get("text", "").strip()
    try:
        float(text)
        return True
    except ValueError:
        return False


def product_stock_guard(ctx):
    text = ctx.get("text", "").strip()
    return text.isdigit()


def register_product_guards():
    register_guard("product_name_guard", product_name_guard)
    register_guard("product_price_guard", product_price_guard)
    register_guard("product_stock_guard", product_stock_guard)
