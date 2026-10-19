"""Cart handlers used by the existing sidebar and checkout."""

from flask import current_app, flash, jsonify, redirect, render_template, request, session, url_for
from app import db
from app.auth import login_required
from app.blueprints import main
from app.models import Product
from app.formatting import format_brl
from app.services.cart import cart_items
from app.services.payments import PaymentError, criar_preferencia


def ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def result(message, error=False, **extra):
    if ajax():
        return jsonify(
            status="error" if error else "success", message=message, **extra
        ), 400 if error else 200
    flash(message, "error" if error else "success")
    return redirect(url_for("main.doacoes"))


def totals():
    items, total = cart_items()
    return {
        "total": format_brl(total),
        "cart_count": sum(row["quantity"] for row in items),
        "items": [
            {
                "id": row["product"].id,
                "quantity": row["quantity"],
                "limit": min(row["product"].stock, 99),
                "subtotal": format_brl(row["subtotal"]),
                "unit_price": format_brl(row["product"].price_cents),
            }
            for row in items
        ],
    }


@main.post("/add/<int:product_id>")
@login_required
def add_to_cart(product_id):
    product = db.get_or_404(Product, product_id)
    cart_items()
    cart = dict(session.get("cart", {}))
    try:
        qty = int(request.form.get("quantity", "1"))
    except ValueError:
        qty = 0
    combined = cart.get(str(product_id), 0) + qty
    if product.price_cents < 0 or qty < 1 or combined > min(product.stock, 99):
        return result("Quantidade inválida ou acima do estoque disponível.", True)
    if str(product_id) not in cart and len(cart) >= 50:
        return result("O carrinho atingiu o limite de itens distintos.", True)
    cart[str(product_id)] = combined
    session["cart"] = cart
    return result(f"{product.name} foi adicionado ao carrinho.", **totals())


@main.post("/update_cart")
@login_required
def update_cart():
    try:
        pid = int(request.form.get("product_id", ""))
        qty = int(request.form.get("qty", ""))
    except ValueError:
        return result("Quantidade ou item inválido.", True)
    product = db.session.get(Product, pid)
    if product is None:
        return result("Produto não encontrado.", True)
    cart_items()
    cart = dict(session.get("cart", {}))
    if str(pid) not in cart or not 0 <= qty <= min(product.stock, 99):
        return result("Quantidade inválida para este item.", True, **totals())
    if qty == 0:
        cart.pop(str(pid), None)
    else:
        cart[str(pid)] = qty
    session["cart"] = cart
    return result("Carrinho atualizado.", qty=qty, **totals())


@main.post("/remove/<int:product_id>")
@login_required
def remove_item(product_id):
    cart_items()
    cart = dict(session.get("cart", {}))
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return result("Item removido.", **totals())


@main.get("/cart_partial")
@login_required
def cart_partial():
    items, total = cart_items()
    return render_template(
        "cart.html",
        items=items,
        total_cents=total,
        cart_count=sum(row["quantity"] for row in items),
    )


@main.get("/checkout")
@login_required
def checkout():
    items, total = cart_items()
    if not items:
        flash("Seu carrinho está vazio. Adicione itens antes de continuar.", "info")
        return redirect(url_for("main.doacoes"))
    return render_template(
        "checkout.html",
        items=items,
        total_cents=total,
        payment_enabled=current_app.config.get("PAYMENT_MODE") == "sandbox",
        pagina_ativa="doacoes",
    )


@main.post("/pagamento")
@login_required
def pagamento():
    items, total = cart_items()
    if not items:
        return result("Seu carrinho está vazio.", True)
    try:
        link = criar_preferencia(items, total)
    except PaymentError as error:
        current_app.logger.warning("Não foi possível criar preferência de teste: %s", error)
        return result(str(error), True)
    return jsonify(status="success", url=link)
