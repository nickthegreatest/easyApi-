"""Контроллер аутентификации: регистрация и вход."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from easyApi.models import user_model
from easyApi.services.jwt_service import generate_token
from easyApi.services.security import check_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register() -> tuple[Any, int]:
    """Регистрация нового пользователя."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email и password обязательны", "code": 400}), 400

    if user_model.get_user_by_username(username):
        return jsonify({"error": "Пользователь уже существует", "code": 409}), 409

    result = user_model.create_user(username, email, password)
    return jsonify(result), 201


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple[Any, int]:
    """Авторизация и выдача JWT-токена."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username и password обязательны", "code": 400}), 400

    user = user_model.get_user_by_username(username)
    if not user or not check_password(password, user["password"]):
        return jsonify({"error": "Неверные учётные данные", "code": 401}), 401

    token = generate_token(
        {"id": user["id"], "username": user["username"], "role": user["role"]}
    )
    return jsonify(
        {
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
            },
        }
    ), 200

