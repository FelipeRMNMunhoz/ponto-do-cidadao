"""Account registration and session authentication."""

from functools import wraps
import re
from flask import flash, g, redirect, render_template, request, session, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Conta

from app.blueprints import main

EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@main.before_app_request
def load_user():
    if request.endpoint == "static":
        g.user = None
        return
    user_id = session.get("usuario_id")
    g.user = db.session.get(Conta, user_id) if isinstance(user_id, int) else None
    if user_id is not None and g.user is None:
        session.clear()


@main.app_context_processor
def user_context():
    from app.services.cart import cart_items

    items, _ = cart_items() if g.get("user") else ([], 0)
    return {"conta": g.get("user"), "cart_quantity": sum(row["quantity"] for row in items)}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.get("user"):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return {
                    "status": "redirect",
                    "url": url_for("main.login"),
                    "message": "Entre na sua conta para continuar.",
                }, 401
            flash("Entre na sua conta para continuar.", "info")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped


@main.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        if not (2 <= len(nome) <= 120 and len(email) <= 80 and EMAIL.fullmatch(email)):
            flash("Informe um nome e um e-mail válidos.", "error")
        elif not 8 <= len(senha) <= 128:
            flash("A senha deve ter entre 8 e 128 caracteres.", "error")
        else:
            conta = Conta(nome=nome, usuario=email, email=email)
            conta.set_senha(senha)
            db.session.add(conta)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Não foi possível criar a conta com este e-mail.", "error")
            else:
                flash("Conta criada. Entre para continuar.", "success")
                return redirect(url_for("main.login"))
        return render_template("criarconta.html", nome=nome, email=email), 400
    return render_template("criarconta.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("usuario", "").strip().lower()
        password = request.form.get("senha", "")
        conta = None
        if len(identifier) <= 120 and 0 < len(password) <= 128:
            conta = db.session.scalar(
                db.select(Conta).where(or_(Conta.usuario == identifier, Conta.email == identifier))
            )
        if conta and conta.verificar_senha(password):
            session.clear()
            session["usuario_id"] = conta.id
            session.permanent = True
            flash("Acesso realizado com sucesso.", "success")
            return redirect(url_for("main.doacoes"))
        flash("E-mail ou senha inválidos.", "error")
        return render_template("login.html", pagina_ativa="login"), 400
    return render_template("login.html", pagina_ativa="login")


@main.post("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "info")
    return redirect(url_for("main.home"))
