# app/models.py
from datetime import datetime, timezone
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


def utc_now():
    """Naive UTC preserves the original SQLite schema and date convention."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Contato(db.Model):
    __tablename__ = "contatos"
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(100), nullable=False)
    segundo_nome = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(150))
    email = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)
    objetivo = db.Column(db.String(200))
    mensagem = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=utc_now, nullable=False)

    def __repr__(self):
        return f"<Contato {self.primeiro_nome} {self.segundo_nome} - {self.email}>"


class Conta(db.Model):
    __tablename__ = "contas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=utc_now)
    atualizado_em = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Conta id={self.id} usuario={self.usuario}>"


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    price_cents = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(255), default="")

    def price_str(self):
        return f"R$ {self.price_cents / 100:.2f}"

    def __repr__(self):
        return f"<Product id={self.id} name={self.name} stock={self.stock}>"


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    total_cents = db.Column(db.Integer, nullable=False, default=0)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)

    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order id={self.id} total={self.total_cents}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_cents = db.Column(db.Integer, nullable=False)

    # relationships
    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def line_total(self):
        return self.price_cents * self.quantity

    def __repr__(self):
        return (
            f"<OrderItem order_id={self.order_id} product_id={self.product_id} qty={self.quantity}>"
        )
