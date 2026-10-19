"""Stable endpoint namespace shared by the route modules."""

from flask import Blueprint

main = Blueprint("main", __name__)
