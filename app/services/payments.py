"""Mercado Pago test checkout. Never trust browser return URLs as proof of payment."""

import json
import secrets
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from flask import current_app


class PaymentError(Exception):
    pass


def criar_preferencia(items, total_cents):
    config = current_app.config
    if config.get("PAYMENT_MODE") != "sandbox":
        raise PaymentError("Pagamento não configurado. Nenhuma cobrança foi criada.")
    token = config.get("MERCADOPAGO_ACCESS_TOKEN")
    base = config.get("PUBLIC_BASE_URL", "").rstrip("/")
    parsed = urlparse(base)
    if (
        not token
        or parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        raise PaymentError("Configure as credenciais de teste e a URL pública HTTPS.")
    if total_cents <= 0:
        raise PaymentError("O valor do carrinho é inválido.")
    payload = {
        "items": [
            {
                "id": str(row["product"].id),
                "title": row["product"].name,
                "quantity": row["quantity"],
                "currency_id": "BRL",
                "unit_price": row["product"].price_cents / 100,
            }
            for row in items
        ],
        "back_urls": {
            "success": base + "/compracerta",
            "failure": base + "/compraerrada",
            "pending": base + "/compraerrada",
        },
        "external_reference": secrets.token_hex(16),
        "statement_descriptor": "PONTO DO CIDADAO",
    }
    req = Request(
        "https://api.mercadopago.com/checkout/preferences",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=15) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
        raise PaymentError("Serviço de pagamento de teste indisponível. Tente novamente.") from None
    link = data.get("sandbox_init_point", "") if isinstance(data, dict) else ""
    url = urlparse(link)
    if url.scheme != "https" or url.hostname not in {
        "sandbox.mercadopago.com.br",
        "sandbox.mercadopago.com",
    }:
        raise PaymentError("O serviço não retornou um endereço válido de teste.")
    return link
