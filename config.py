"""Configuration loaded at application creation, never at import time."""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


def get_config():
    load_dotenv(BASE_DIR / ".env")
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", "sqlite:///ponto_do_cidadao.db"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": os.getenv("COOKIE_SECURE", "false").lower() == "true",
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=2),
        "MAX_CONTENT_LENGTH": 64 * 1024,
        "WTF_CSRF_TIME_LIMIT": 3600,
        "PAYMENT_MODE": os.getenv("PAYMENT_MODE", "disabled"),
        "MERCADOPAGO_ACCESS_TOKEN": os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""),
        "PUBLIC_BASE_URL": os.getenv("PUBLIC_BASE_URL", ""),
    }
