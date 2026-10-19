from app import db
from app.models import Product

AJAX = {"X-Requested-With": "XMLHttpRequest"}


def test_cart_snapshot_and_line_totals(logged_in):
    response = logged_in.post("/add/1", data={"quantity": 2}, headers=AJAX)
    data = response.get_json()
    assert data["total"] == "R$ 21,56"
    assert data["cart_count"] == 2
    assert data["items"] == [
        {"id": 1, "quantity": 2, "limit": 3, "subtotal": "R$ 21,56", "unit_price": "R$ 10,78"}
    ]
    assert b"R$ 21,56" in logged_in.get("/checkout").data
    response = logged_in.post("/remove/1", headers=AJAX)
    assert response.get_json()["items"] == []
    assert response.get_json()["cart_count"] == 0
    assert b'href="/checkout"' not in logged_in.get("/cart_partial").data


def test_rejected_quantity_returns_current_stock_snapshot(logged_in, app):
    logged_in.post("/add/1", data={"quantity": 3})
    with app.app_context():
        db.session.get(Product, 1).stock = 1
        db.session.commit()
    response = logged_in.post("/update_cart", data={"product_id": 1, "qty": 2}, headers=AJAX)
    assert response.status_code == 400
    data = response.get_json()
    assert data["cart_count"] == 1
    assert data["total"] == "R$ 10,78"
    assert data["items"][0]["limit"] == 1


def test_invalid_price_cannot_be_added(logged_in, app):
    with app.app_context():
        db.session.get(Product, 1).price_cents = -100
        db.session.commit()
    assert logged_in.post("/add/1", data={"quantity": 1}, headers=AJAX).status_code == 400
    with logged_in.session_transaction() as state:
        assert not state.get("cart")


def test_payment_button_requires_sandbox(logged_in, app):
    logged_in.post("/add/1", data={"quantity": 1})
    app.config["PAYMENT_MODE"] = "disabled"
    page = logged_in.get("/checkout").get_data(as_text=True)
    assert 'id="pay-btn"' not in page
    assert "nenhuma cobrança será realizada" in page
    app.config["PAYMENT_MODE"] = "sandbox"
    assert 'id="pay-btn"' in logged_in.get("/checkout").get_data(as_text=True)


def test_unconfigured_campaign_has_no_payment_link(client):
    page = client.get("/projeto/3").get_data(as_text=True)
    assert "Em preparação" in page
    assert "pag.ae" not in page
    assert "vakinha.com.br" not in page
    listing = client.get("/projetos").get_data(as_text=True)
    assert "Em preparação" in listing


def test_static_assets_do_not_query_accounts(logged_in, monkeypatch):
    def unexpected_query(*args, **kwargs):
        raise AssertionError("Static assets must not require a database query")

    monkeypatch.setattr(db.session, "get", unexpected_query)
    assert logged_in.get("/static/js/api.js").status_code == 200
