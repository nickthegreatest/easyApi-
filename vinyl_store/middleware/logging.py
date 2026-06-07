"""Request logging middleware."""

from __future__ import annotations

import logging
import time

from flask import Flask, g, request

logger = logging.getLogger("vinyl_store.requests")


def register_request_logging(app: Flask) -> None:
    """Log method, path, status code, and request duration."""

    @app.before_request
    def before_request() -> None:
        g.request_started_at = time.perf_counter()

    @app.after_request
    def after_request(response):
        started = getattr(g, "request_started_at", time.perf_counter())
        duration_ms = (time.perf_counter() - started) * 1000
        logger.info("%s %s -> %s %.1fms", request.method, request.path, response.status_code, duration_ms)
        return response
