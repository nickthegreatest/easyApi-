"""Auth request validators."""

from __future__ import annotations

from typing import Any

from vinyl_store.validators.common import json_object, optional_string, required_string, validate_email


def validate_register(payload: Any) -> dict[str, Any]:
    data = json_object(payload)
    password = required_string(data, "password", min_len=6, max_len=128)
    return {
        "username": required_string(data, "username", min_len=3, max_len=50),
        "email": validate_email(required_string(data, "email", max_len=100)),
        "password": password,
        "first_name": optional_string(data, "first_name", max_len=50),
        "last_name": optional_string(data, "last_name", max_len=50),
        "phone": optional_string(data, "phone", max_len=20),
        "address": optional_string(data, "address", max_len=1000),
    }


def validate_login(payload: Any) -> dict[str, str]:
    data = json_object(payload)
    return {
        "identity": required_string(data, "identity", min_len=3, max_len=100),
        "password": required_string(data, "password", min_len=1, max_len=128),
    }
