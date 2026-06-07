"""Контроллер личного кабинета."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify

from easyApi.models import user_model
from easyApi.services import order_service
from easyApi.services.security import token_required

account_bp = Blueprint("account", __name__)


@account_bp.route("/account", methods=["GET"])
@token_required
def account(current_user: dict[str, Any]) -> tuple[Any, int]:
    """Профиль текущего пользователя."""
    user = user_model.get_user_by_id(current_user["id"])
    if not user:
        return jsonify({"error": "Пользователь не найден", "code": 404}), 404

    return jsonify(
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }
    ), 200


@account_bp.route("/account/orders", methods=["GET"])
@token_required
def account_orders(current_user: dict[str, Any]) -> tuple[Any, int]:
    """стория заказов пользователя."""
    orders = order_service.get_user_orders(current_user["id"])
    return jsonify({"orders": orders}), 200

