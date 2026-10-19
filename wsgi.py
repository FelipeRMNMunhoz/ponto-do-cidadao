"""WSGI entry point for PythonAnywhere and other compatible servers."""

from app import create_app

application = create_app()
