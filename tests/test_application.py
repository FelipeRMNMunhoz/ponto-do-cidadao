import re

import pytest

from app import db
from app.catalog import seed_products
from app.models import Conta, Contato, Order, Product


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/doacoes",
        "/projetos",
        "/projeto/1",
        "/QuemSomos",
        "/login",
        "/criarconta",
    ],
)
def test_public_pages(client, url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize(
    "url, target",
    [("/project", "/doacoes"), ("/about", "/QuemSomos"), ("/quem-somos", "/QuemSomos")],
)
def test_legacy_urls(client, url, target):
    response = client.get(url)
    assert response.status_code == 301
    assert response.location.endswith(target)


def test_missing_campaign(client):
    assert client.get("/projeto/999").status_code == 404


def test_contact_validation_and_storage(client, app):
    assert client.post("/", data={"email": "invalid"}).status_code == 400
    data = {
        "firstName": "Teste",
        "lastName": "Local",
        "email": "local@example.test",
        "message": "Mensagem de teste",
        "phone": "00000000000",
    }
    assert client.post("/", data=data).status_code == 302
    with app.app_context():
        contacts = db.session.scalars(db.select(Contato)).all()
        assert len(contacts) == 1
        assert contacts[0].telefone == "00000000000"
    assert client.post("/", data={**data, "message": "x" * 3001}).status_code == 400


def test_registration_password_hash_and_duplicates(client, app):
    data = {
        "nome": "Nova Pessoa",
        "email": "NOVA@example.test",
        "senha": " senha longa com espaços ",
        "confirmacao": " senha longa com espaços ",
    }
    assert client.post("/criarconta", data=data).status_code == 302
    assert client.post("/criarconta", data=data).status_code == 400
    with app.app_context():
        user = db.session.scalar(db.select(Conta).where(Conta.email == "nova@example.test"))
        assert user.senha_hash != data["senha"]
        assert user.verificar_senha(data["senha"])
    assert (
        client.post(
            "/login", data={"usuario": "nova@example.test", "senha": data["senha"]}
        ).status_code
        == 302
    )


@pytest.mark.parametrize("change", [{"senha": "short"}, {"email": "invalid"}, {"nome": ""}])
def test_invalid_registration(client, change):
    data = {
        "nome": "Pessoa",
        "email": "new@example.test",
        "senha": "senha-longa-de-teste",
        "confirmacao": "senha-longa-de-teste",
    }
    assert client.post("/criarconta", data={**data, **change}).status_code == 400


def test_failed_login_and_post_only_logout(client):
    assert (
        client.post("/login", data={"usuario": "teste@example.test", "senha": "wrong"}).status_code
        == 400
    )
    assert client.get("/logout").status_code == 405


@pytest.mark.parametrize("path", ["/add/1", "/update_cart", "/remove/1"])
def test_cart_mutations_require_login(client, path):
    response = client.post(path, data={"quantity": 1, "product_id": 1, "qty": 1})
    assert response.status_code == 302
    assert response.location.endswith("/login")
    with client.session_transaction() as state:
        assert not state.get("cart")


def test_total_stock_bound_and_invalid_input(logged_in):
    logged_in.post("/add/1", data={"quantity": 2})
    logged_in.post("/add/1", data={"quantity": 2})
    with logged_in.session_transaction() as state:
        assert state["cart"] == {"1": 2}
    for quantity in ["abc", "-1", "9999999"]:
        assert logged_in.post("/add/1", data={"quantity": quantity}).status_code == 302
    assert b"R$ 21,56" in logged_in.get("/cart_partial").data
    assert logged_in.post("/update_cart", data={"product_id": "abc", "qty": "2"}).status_code == 302
    logged_in.post("/update_cart", data={"product_id": 1, "qty": 3})
    assert b"R$ 32,34" in logged_in.get("/checkout").data


def test_stale_cart_is_revalidated(logged_in, app):
    logged_in.post("/add/1", data={"quantity": 3})
    with app.app_context():
        db.session.get(Product, 1).stock = 1
        db.session.commit()
    assert b"R$ 10,78" in logged_in.get("/checkout").data
    with logged_in.session_transaction() as state:
        assert state["cart"] == {"1": 1}


def test_removal_empty_checkout_and_logout(logged_in):
    logged_in.post("/add/1", data={"quantity": 1})
    logged_in.post("/remove/1")
    assert logged_in.get("/checkout").location.endswith("/doacoes")
    logged_in.post("/logout")
    with logged_in.session_transaction() as state:
        assert "usuario_id" not in state and "cart" not in state


def test_invalid_session_user_cannot_access_cart(client):
    with client.session_transaction() as state:
        state["usuario_id"] = 999
    assert client.get("/cart_partial").location.endswith("/login")


def test_checkout_has_no_payment_side_effects(logged_in, app):
    logged_in.post("/add/1", data={"quantity": 1})
    for path in ["/checkout", "/compracerta?status=approved", "/compraerrada"]:
        assert logged_in.get(path).status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Order.id))) == 0
        assert db.session.get(Product, 1).stock == 3


def test_csrf_enforced_for_posts(client, app):
    app.config["WTF_CSRF_ENABLED"] = True
    assert client.post("/login", data={}).status_code == 400
    response = client.get("/login")
    token = re.search(rb'name="csrf_token" value="([^"]+)"', response.data).group(1).decode()
    assert (
        client.post(
            "/login",
            data={
                "csrf_token": token,
                "usuario": "teste@example.test",
                "senha": "uma-senha-de-teste",
            },
        ).status_code
        == 302
    )
    assert client.post("/add/1", data={"quantity": 1}).status_code == 400


def test_seed_is_idempotent(app):
    with app.app_context():
        assert seed_products() == 15
        assert seed_products() == 0


def test_untrusted_text_is_escaped(client):
    response = client.post("/", data={"firstName": "<script>alert(1)</script>"})
    assert b"<script>alert(1)</script>" not in response.data


def test_security_headers(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"
