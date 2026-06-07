"""Контроллер корзины."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from easyApi.models import cart_model, product_model
from easyApi.services.security import token_required

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart", methods=["GET"])
@token_required
def view_cart(current_user: dict[str, Any]) -> tuple[Any, int]:
    """Содержимое корзины текущего пользователя."""
    items = cart_model.get_cart(current_user["id"])
    return jsonify({"cart": items}), 200


@cart_bp.route("/add-to-cart", methods=["POST"])
@token_required
def add_to_cart(current_user: dict[str, Any]) -> tuple[Any, int]:
    """Добавление товара в корзину."""
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "product_id обязателен", "code": 400}), 400

    product = product_model.get_product_by_id(int(product_id))
    if not product:
        return jsonify({"error": "Товар не найден", "code": 404}), 404

    result = cart_model.add_to_cart(
        current_user["id"],
        int(product_id),
        int(quantity),
        float(product["price"]),
    )
    return jsonify(result), 200


@cart_bp.route("/cart/<int:product_id>", methods=["DELETE"])
@token_required
def remove_from_cart(current_user: dict[str, Any], product_id: int) -> tuple[Any, int]:
    """Удаление товара из корзины."""
    result = cart_model.remove_from_cart(current_user["id"], product_id)
    return jsonify(result), 200

