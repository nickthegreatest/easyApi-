"""Input validation helpers."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from vinyl_store.middleware.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def json_object(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")
    return payload


def required_string(payload: dict[str, Any], key: str, *, min_len: int = 1, max_len: int = 255) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Field '{key}' is required")
    value = value.strip()
    if len(value) < min_len or len(value) > max_len:
        raise ValidationError(f"Field '{key}' length must be between {min_len} and {max_len}")
    return value


def optional_string(payload: dict[str, Any], key: str, *, max_len: int = 255) -> str | None:
    value = payload.get(key)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(f"Field '{key}' must be a string")
    value = value.strip()
    if len(value) > max_len:
        raise ValidationError(f"Field '{key}' length must be <= {max_len}")
    return value


def integer(payload: dict[str, Any], key: str, *, default: int | None = None, minimum: int | None = None) -> int:
    value = payload.get(key, default)
    if value is None:
        raise ValidationError(f"Field '{key}' is required")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Field '{key}' must be an integer") from exc
    if minimum is not None and result < minimum:
        raise ValidationError(f"Field '{key}' must be >= {minimum}")
    return result


def decimal_value(payload: dict[str, Any], key: str, *, minimum: Decimal | None = None) -> Decimal:
    value = payload.get(key)
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValidationError(f"Field '{key}' must be a decimal number") from exc
    if minimum is not None and result < minimum:
        raise ValidationError(f"Field '{key}' must be >= {minimum}")
    return result


def validate_email(value: str) -> str:
    if not EMAIL_RE.match(value):
        raise ValidationError("Email has invalid format")
    return value.lower()


def validate_slug(value: str) -> str:
    if not SLUG_RE.match(value):
        raise ValidationError("Slug must contain lowercase letters, numbers and hyphens")
    return value
