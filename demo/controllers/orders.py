"""Контроллер заказов."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify

from easyApi.db.exceptions import DatabaseQueryError
from easyApi.services import order_service
from easyApi.services.security import token_required

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/orders", methods=["GET"])
@token_required
def list_orders(current_user: dict[str, Any]) -> tuple[Any, int]:
    """Список заказов текущего пользователя."""
    orders = order_service.get_user_orders(current_user["id"])
    return jsonify({"orders": orders}), 200


@orders_bp.route("/create-order", methods=["POST"])
@token_required
def create_order_route(current_user: dict[str, Any]) -> tuple[Any, int]:
    """Создание заказа из корзины."""
    try:
        result = order_service.create_order(current_user["id"])
        return jsonify(result), 201
    except DatabaseQueryError as exc:
        return jsonify({"error": exc.message, "code": exc.code}), exc.code

