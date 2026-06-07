"""SQL repository for the users table."""

from __future__ import annotations

from typing import Any

from vinyl_store.repositories.base import insert, select, update

SAFE_USER_COLUMNS = "id, username, email, role, first_name, last_name, phone, address, created_at, updated_at"


def find_by_identity(identity: str) -> dict[str, Any] | None:
    rows = select("users", where="username = %s OR email = %s", where_params=[identity, identity], limit=1)
    return rows[0] if rows else None


def find_by_id(user_id: int) -> dict[str, Any] | None:
    rows = select("users", columns=SAFE_USER_COLUMNS, where="id = %s", where_params=[user_id], limit=1)
    return rows[0] if rows else None


def create_user(data: dict[str, Any]) -> int:
    result = insert("users", data)
    return int(result["insert_id"])


def update_user(user_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update("users", data, "id = %s", [user_id])


def list_users() -> list[dict[str, Any]]:
    return select("users", columns=SAFE_USER_COLUMNS, order="created_at DESC")
