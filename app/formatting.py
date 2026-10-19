"""Presentation helpers shared by templates and JSON responses."""


def format_brl(cents):
    return f"R$ {cents / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
