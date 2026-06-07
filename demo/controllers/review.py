"""Контроллер отзывов."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from easyApi.models import product_model, review_model
from easyApi.services.security import token_required

review_bp = Blueprint("review", __name__)


@review_bp.route("/product/<int:product_id>/review", methods=["POST"])
@token_required
def add_review(current_user: dict[str, Any], product_id: int) -> tuple[Any, int]:
    """Добавление отзыва на товар."""
    if not product_model.get_product_by_id(product_id):
        return jsonify({"error": "Товар не найден", "code": 404}), 404

    data = request.get_json(silent=True) or {}
    text = data.get("text")
    rating = data.get("rating")

    if not text or rating is None:
        return jsonify({"error": "text и rating обязательны", "code": 400}), 400

    rating_int = int(rating)
    if rating_int < 1 or rating_int > 5:
        return jsonify({"error": "rating должен быть от 1 до 5", "code": 400}), 400

    result = review_model.add_review(current_user["id"], product_id, text, rating_int)
    return jsonify(result), 201


@review_bp.route("/product/<int:product_id>/reviews", methods=["GET"])
def get_reviews(product_id: int) -> tuple[Any, int]:
    """Список отзывов на товар."""
    if not product_model.get_product_by_id(product_id):
        return jsonify({"error": "Товар не найден", "code": 404}), 404

    reviews = review_model.get_reviews_by_product(product_id)
    return jsonify({"reviews": reviews}), 200

