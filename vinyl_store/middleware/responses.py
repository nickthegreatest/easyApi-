"""Standard JSON response helpers."""

from __future__ import annotations

from typing import Any

from flask import jsonify


def success(data: Any = None, *, message: str = "OK", status: int = 200):
    """Return a standardized successful JSON response."""

    return jsonify({"success": True, "message": message, "data": data}), status


def error(message: str, *, status: int = 400, details: Any = None):
    """Return a standardized error JSON response."""

    payload: dict[str, Any] = {"success": False, "message": message, "code": status}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status
