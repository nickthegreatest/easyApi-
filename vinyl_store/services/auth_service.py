"""Business logic for registration, login, and profile operations."""

from __future__ import annotations

from typing import Any

from easyApi import check_password, generate_token, hash_password
from vinyl_store.middleware.errors import ValidationError
from vinyl_store.repositories import users as users_repo


def register_user(payload: dict[str, Any]) -> dict[str, Any]:
    if users_repo.find_by_identity(payload["username"]) or users_repo.find_by_identity(payload["email"]):
        raise ValidationError("Username or email is already registered")
    user_id = users_repo.create_user(
        {
            "username": payload["username"],
            "email": payload["email"],
            "password": hash_password(payload["password"]),
            "role": "user",
            "first_name": payload.get("first_name"),
            "last_name": payload.get("last_name"),
            "phone": payload.get("phone"),
            "address": payload.get("address"),
        }
    )
    user = users_repo.find_by_id(user_id)
    token = generate_token({"id": user["id"], "username": user["username"], "role": user["role"]})
    return {"user": user, "token": token}


def login_user(payload: dict[str, str]) -> dict[str, Any]:
    user = users_repo.find_by_identity(payload["identity"])
    if not user or not check_password(payload["password"], user["password"]):
        raise ValidationError("Invalid username/email or password")
    safe_user = users_repo.find_by_id(user["id"])
    token = generate_token({"id": user["id"], "username": user["username"], "role": user["role"]})
    return {"user": safe_user, "token": token}


def get_profile(user_id: int) -> dict[str, Any]:
    user = users_repo.find_by_id(user_id)
    if not user:
        raise ValidationError("User not found")
    return user
