"""JWT authentication middleware for the store."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import g, request

from easyApi import verify_token
from easyApi.db.exceptions import TokenExpiredError, TokenInvalidError
from vinyl_store.middleware.responses import error


def _extract_token() -> str | None:
    bearer = request.headers.get("Authorization", "")
    if bearer.startswith("Bearer "):
        return bearer.removeprefix("Bearer ").strip()
    return request.headers.get("x-access-token")


def jwt_required(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Require a valid JWT and expose the decoded user in flask.g.current_user."""

    @wraps(handler)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        token = _extract_token()
        if not token:
            return error("JWT token is missing", status=401)
        try:
            g.current_user = verify_token(token)
        except TokenExpiredError:
            return error("JWT token has expired", status=401)
        except TokenInvalidError:
            return error("JWT token is invalid", status=403)
        return handler(*args, **kwargs)

    return wrapper


def admin_required(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Require an authenticated user with admin role."""

    @wraps(handler)
    @jwt_required
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if g.current_user.get("role") != "admin":
            return error("Admin role is required", status=403)
        return handler(*args, **kwargs)

    return wrapper
