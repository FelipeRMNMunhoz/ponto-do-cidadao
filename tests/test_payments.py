import io
import json
from urllib.error import URLError

from app import db
from app.models import Product
from app.services import payments

AJAX = {"X-Requested-With": "XMLHttpRequest"}


def test_payment_disabled_and_get_has_no_network(logged_in, monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("A disabled payment must not reach the provider")

    monkeypatch.setattr(payments, "urlopen", unexpected)
    logged_in.post("/add/1", data={"quantity": 1})
    assert logged_in.get("/checkout").status_code == 200
    response = logged_in.post("/pagamento", headers=AJAX)
    assert response.status_code == 400
    assert "Nenhuma cobrança" in response.json["message"]
    assert logged_in.get("/pagamento").status_code == 405


def test_sandbox_uses_current_server_price(logged_in, app, monkeypatch):
    app.config.update(
        PAYMENT_MODE="sandbox",
        MERCADOPAGO_ACCESS_TOKEN="fake-test-token",
        PUBLIC_BASE_URL="https://example.test",
    )
    logged_in.post("/add/1", data={"quantity": 2})
    with app.app_context():
        db.session.get(Product, 1).price_cents = 1234
        db.session.commit()
    sent = []

    def provider(request, timeout):
        sent.append(json.loads(request.data))
        assert timeout == 15
        return io.BytesIO(
            json.dumps(
                {
                    "sandbox_init_point": "https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=test"
                }
            ).encode()
        )

    monkeypatch.setattr(payments, "urlopen", provider)
    response = logged_in.post("/pagamento", data={"total": "0.01"}, headers=AJAX)
    assert response.status_code == 200
    assert sent[0]["items"][0]["unit_price"] == 12.34
    assert sent[0]["items"][0]["quantity"] == 2
    assert sent[0]["back_urls"]["success"] == "https://example.test/compracerta"
    assert len(sent[0]["external_reference"]) == 32


def test_provider_failure_does_not_expose_credentials(logged_in, app, monkeypatch):
    app.config.update(
        PAYMENT_MODE="sandbox",
        MERCADOPAGO_ACCESS_TOKEN="private-test-token",
        PUBLIC_BASE_URL="https://example.test",
    )
    logged_in.post("/add/1", data={"quantity": 1})

    def failed(*args, **kwargs):
        raise URLError("private-test-token")

    monkeypatch.setattr(payments, "urlopen", failed)
    response = logged_in.post("/pagamento", headers=AJAX)
    assert response.status_code == 400
    assert b"private-test-token" not in response.data


def test_provider_external_link_rejected(logged_in, app, monkeypatch):
    app.config.update(
        PAYMENT_MODE="sandbox",
        MERCADOPAGO_ACCESS_TOKEN="fake-test-token",
        PUBLIC_BASE_URL="https://example.test",
    )
    logged_in.post("/add/1", data={"quantity": 1})
    monkeypatch.setattr(
        payments,
        "urlopen",
        lambda *args, **kwargs: io.BytesIO(
            b'{"sandbox_init_point":"https://untrusted.example/pay"}'
        ),
    )
    assert logged_in.post("/pagamento", headers=AJAX).status_code == 400


def test_ajax_auth_and_csrf_contract(client, app):
    assert client.post("/pagamento", headers=AJAX).json["status"] == "redirect"
    app.config["WTF_CSRF_ENABLED"] = True
    response = client.post("/update_cart", data={"qty": 1}, headers=AJAX)
    assert response.status_code == 400
    assert response.json["status"] == "error"
