"""Illustrative catalog values inherited from the 2025 prototype."""

from app import db
from app.models import Product


def seed_products():
    products_data = [
        {
            "name": "Arroz Camil 1kg",
            "description": "1kg de Arroz Camil para doação.",
            "price_cents": 1078,
            "stock": 100,
            "image_url": "picture-movie/img/help/arroz.png",
        },
        {
            "name": "Feijão Kicaldo 1kg",
            "description": "1kg de Feijão Kicaldo para doação.",
            "price_cents": 599,
            "stock": 100,
            "image_url": "picture-movie/img/help/feijao.png",
        },
        {
            "name": "Açúcar 1kg",
            "description": "1kg de Açúcar para doação.",
            "price_cents": 899,
            "stock": 100,
            "image_url": "picture-movie/img/help/Acucar.png",
        },
        {
            "name": "Café 500g",
            "description": "500g de Café para doação.",
            "price_cents": 2000,
            "stock": 100,
            "image_url": "picture-movie/img/help/cafe.png",
        },
        {
            "name": "Sal Lebre 1kg",
            "description": "1kg de Sal Lebre para doação.",
            "price_cents": 300,
            "stock": 100,
            "image_url": "picture-movie/img/help/Sal.png",
        },
        {
            "name": "Macarrão Renata 1kg",
            "description": "1kg de Macarrão para doação.",
            "price_cents": 622,
            "stock": 100,
            "image_url": "picture-movie/img/help/Macarrao-de-Semola.png",
        },
        {
            "name": "Óleo Soya 900 ml",
            "description": "900ml de Óleo Soya para doação.",
            "price_cents": 719,
            "stock": 100,
            "image_url": "picture-movie/img/help/oleo-soya.png",
        },
        {
            "name": "Molho de tomate Sofruta 1,7 kg",
            "description": "1,7 kg de molho de tomate para doação.",
            "price_cents": 2517,
            "stock": 100,
            "image_url": "picture-movie/img/help/molho-de-tomate.png",
        },
        {
            "name": "Papel Higiênico Mellior",
            "description": "Papel Higiênico para doação.",
            "price_cents": 3499,
            "stock": 100,
            "image_url": "picture-movie/img/help/papel-higienico.png",
        },
        {
            "name": "Leite Leco Personal",
            "description": "Leite Leco para doação.",
            "price_cents": 718,
            "stock": 100,
            "image_url": "picture-movie/img/help/Leco-leite.png",
        },
        {
            "name": "Sardinha Pescador",
            "description": "Sardinha Pescador para doação.",
            "price_cents": 609,
            "stock": 100,
            "image_url": "picture-movie/img/help/Sardinha-vermelha.png",
        },
        {
            "name": "Fubá de Milho",
            "description": "Fubá de Milho para doação.",
            "price_cents": 421,
            "stock": 100,
            "image_url": "picture-movie/img/help/fuba_de_milho.png",
        },
        {
            "name": "Cesta Completa",
            "description": "Cesta Completa para doação.",
            "price_cents": 44999,
            "stock": 100,
            "image_url": "picture-movie/img/help/cesta-completa.png",
        },
        {
            "name": "Cesta Básica+",
            "description": "Cesta Básica+ para doação.",
            "price_cents": 32000,
            "stock": 100,
            "image_url": "picture-movie/img/help/cesta-basica-plus.png",
        },
        {
            "name": "Cesta Básica",
            "description": "Cesta Básica para doação.",
            "price_cents": 14999,
            "stock": 100,
            "image_url": "picture-movie/img/help/cesta-basica.png",
        },
    ]

    count = 0
    for data in products_data:
        if db.session.scalar(db.select(Product).where(Product.name == data["name"])) is None:
            db.session.add(Product(**data))
            count += 1
    db.session.commit()
    return count
