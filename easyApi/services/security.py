"""Модуль безопасности: хеширование паролей и декораторы авторизации."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from easyApi.db.exceptions import TokenExpiredError, TokenInvalidError
from easyApi.services.jwt_service import verify_token


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием werkzeug.

    Args:
        password: сходный пароль.

    Returns:
        Хеш пароля.
    """
    return generate_password_hash(password)


def check_password(password: str, hashed: str) -> bool:
    """Проверяет соответствие пароля его хешу.

    Args:
        password: Пароль для проверки.
        hashed: Сохранённый хеш.

    Returns:
        True, если пароль верный.
    """
    return check_password_hash(hashed, password)


def token_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор Flask-маршрута: требует JWT в заголовке x-access-token."""

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = request.headers.get("x-access-token")
        if not token:
            return jsonify({"error": "Токен отсутствует", "code": 401}), 401

        try:
            current_user = verify_token(token)
        except TokenExpiredError as exc:
            return jsonify({"error": exc.message, "code": 401}), 401
        except TokenInvalidError as exc:
            return jsonify({"error": exc.message, "code": 403}), 403

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор Flask-маршрута: требует роль admin."""

    @wraps(f)
    @token_required
    def decorated(current_user: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if current_user.get("role") != "admin":
            return jsonify({"error": "Доступ запрещён: требуется роль admin", "code": 403}), 403
        return f(current_user, *args, **kwargs)

    return decorated


def manager_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор Flask-маршрута: требует роль admin или manager."""

    @wraps(f)
    @token_required
    def decorated(current_user: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        if current_user.get("role") not in ["admin", "manager"]:
            return jsonify({"error": "Доступ запрещён: требуется роль admin или manager", "code": 403}), 403
        return f(current_user, *args, **kwargs)

    return decorated

