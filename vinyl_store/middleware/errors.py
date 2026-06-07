"""Centralized exception handling for Flask/EasyApi responses."""

from __future__ import annotations

import logging

from flask import Flask
from werkzeug.exceptions import HTTPException

from easyApi.db.exceptions import DatabaseError
from vinyl_store.middleware.responses import error

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Raised when request payload validation fails."""


def register_error_handlers(app: Flask) -> None:
    """Install centralized JSON error handlers."""

    @app.errorhandler(ValidationError)
    def handle_validation(exc: ValidationError):
        return error(str(exc), status=400)

    @app.errorhandler(DatabaseError)
    def handle_database(exc: DatabaseError):
        logger.exception("Database error: %s", exc)
        return error("Database operation failed", status=500, details=str(exc))

    @app.errorhandler(HTTPException)
    def handle_http(exc: HTTPException):
        return error(exc.description or exc.name, status=exc.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        logger.exception("Unhandled application error: %s", exc)
        return error("Internal server error", status=500)
