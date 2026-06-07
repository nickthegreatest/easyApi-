"""Модель пользователя: CRUD для таблицы users."""

from __future__ import annotations

from typing import Any

from easyApi.db.connection import execute_query
from easyApi.services.security import hash_password


def create_user(username: str, email: str, password: str) -> dict[str, Any]:
    """Создаёт нового пользователя с хешированным паролем."""
    return execute_query(
        "INSERT",
        "users",
        {
            "username": username,
            "email": email,
            "password": hash_password(password),
            "role": "user",
        },
    )


def get_user_by_username(username: str) -> dict[str, Any] | None:
    """Возвращает пользователя по имени."""
    rows = execute_query(
        "SELECT",
        "users",
        where="username = %s",
        where_params=(username,),
    )
    return rows[0] if rows else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Возвращает пользователя по ID."""
    rows = execute_query(
        "SELECT",
        "users",
        where="id = %s",
        where_params=(user_id,),
    )
    return rows[0] if rows else None

