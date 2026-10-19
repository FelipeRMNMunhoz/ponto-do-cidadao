"""Application factory and shared extensions."""

from pathlib import Path
import click
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import get_config
from app.formatting import format_brl

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(get_config())
    if test_config:
        app.config.update(test_config)
    secret = app.config.get("SECRET_KEY")
    if not secret or len(secret) < 32 or secret.startswith("troque-"):
        raise RuntimeError(
            "Defina SECRET_KEY com pelo menos 32 caracteres aleatórios no arquivo .env."
        )
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    from app.blueprints import main
    from app import routes, auth, cart  # noqa: F401 - register routes before blueprint

    app.register_blueprint(main)

    app.jinja_env.filters["brl"] = format_brl

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(status="error", message="Atualize a página e tente novamente."), 400
        return render_template(
            "error.html",
            title="Formulário expirado",
            message="Atualize a página e tente enviar novamente.",
        ), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template(
            "error.html",
            title="Página não encontrada",
            message="O endereço solicitado não está disponível.",
        ), 404

    @app.errorhandler(413)
    def too_large(error):
        return render_template(
            "error.html",
            title="Conteúdo muito extenso",
            message="Reduza o tamanho dos campos e tente novamente.",
        ), 413

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template(
            "error.html", title="Não foi possível concluir", message="Tente novamente mais tarde."
        ), 500

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.cli.command("init-db")
    def init_db():
        """Create missing tables on a new installation; never delete records."""
        db.create_all()
        click.echo("Tabelas criadas. Dados existentes preservados.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Insert the demonstration catalog without duplicating products."""
        from app.catalog import seed_products

        click.echo(f"{seed_products()} itens demonstrativos adicionados.")

    return app
