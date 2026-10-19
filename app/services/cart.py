from flask import session
from app import db
from app.models import Product

MAX_ITEMS = 50


def cart_items():
    raw = session.get("cart", {})
    valid = {}
    rows, total = [], 0
    if not isinstance(raw, dict):
        raw = {}
    for pid, qty in list(raw.items())[:MAX_ITEMS]:
        if not str(pid).isdigit() or type(qty) is not int or qty < 1:
            continue
        product = db.session.get(Product, int(pid))
        if not product or product.stock < 1 or product.price_cents < 0:
            continue
        qty = min(qty, product.stock, 99)
        valid[str(product.id)] = qty
        subtotal = qty * product.price_cents
        rows.append({"product": product, "quantity": qty, "subtotal": subtotal})
        total += subtotal
    if valid != raw:
        session["cart"] = valid
    return rows, total
