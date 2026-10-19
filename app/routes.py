"""Public routes. Original templates and visual design are preserved."""

from flask import abort, flash, redirect, render_template, request, url_for
from app import db
from app.auth import EMAIL
from app.blueprints import main
from app.content import PROJETOS
from app.models import Contato, Product


@main.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        keys = ("firstName", "lastName", "address", "email", "phone", "subject", "message")
        data = {key: request.form.get(key, "").strip() for key in keys}
        limits = dict(zip(keys, (100, 100, 150, 150, 50, 200, 3000)))
        invalid = any(len(data[key]) > limit for key, limit in limits.items())
        invalid |= not all(data[key] for key in ("firstName", "lastName", "email", "phone"))
        invalid |= not bool(EMAIL.fullmatch(data["email"]))
        if invalid:
            flash("Confira os campos obrigatórios e o formato do e-mail.", "error")
            return render_template("home.html", pagina_ativa="home"), 400
        db.session.add(
            Contato(
                primeiro_nome=data["firstName"],
                segundo_nome=data["lastName"],
                empresa=data["address"],
                email=data["email"].lower(),
                telefone=data["phone"],
                objetivo=data["subject"],
                mensagem=data["message"],
            )
        )
        db.session.commit()
        flash("Sua mensagem foi registrada com sucesso.", "success")
        return redirect(url_for("main.home"))
    return render_template("home.html", pagina_ativa="home")


@main.get("/doacoes")
def doacoes():
    products = db.session.scalars(db.select(Product).order_by(Product.name)).all()
    return render_template("doacoes.html", products=products, pagina_ativa="doacoes")


@main.get("/project")
def project():
    return redirect(url_for("main.doacoes"), code=301)


@main.get("/QuemSomos")
def about():
    return render_template("quemsomos.html", pagina_ativa="quemsomos")


@main.get("/about")
@main.get("/quem-somos")
def legacy_about():
    return redirect(url_for("main.about"), code=301)


@main.get("/projetos")
def projetos():
    return render_template("projetos.html", projetos=PROJETOS, pagina_ativa="projetos")


@main.get("/projeto/<int:projeto_id>")
def projeto_detalhe(projeto_id):
    projeto = PROJETOS.get(projeto_id)
    if projeto is None:
        abort(404)
    return render_template("projeto_detalhe.html", projeto=projeto, pagina_ativa="projetos")


@main.get("/compracerta")
def compra_certa():
    return render_template("compracerta.html")


@main.get("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")
