import pytest

from app import create_app, db
from app.models import Conta, Product


@pytest.fixture
def app():
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret-never-use-in-production-123456789",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with application.app_context():
        db.create_all()
        user = Conta(nome="Pessoa Teste", usuario="teste@example.test", email="teste@example.test")
        user.set_senha("uma-senha-de-teste")
        db.session.add_all([user, Product(name="Arroz", price_cents=1078, stock=3)])
        db.session.commit()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in(client):
    client.post("/login", data={"usuario": "teste@example.test", "senha": "uma-senha-de-teste"})
    return client
