"""Контроллер каталога товаров."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify

from easyApi.models import product_model

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.route("/", methods=["GET"])
def index() -> tuple[Any, int]:
    """Главная — список всех товаров."""
    products = product_model.get_all_products()
    return jsonify({"products": products}), 200


@catalog_bp.route("/product/<int:product_id>", methods=["GET"])
def product_detail(product_id: int) -> tuple[Any, int]:
    """Карточка товара по ID."""
    product = product_model.get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Товар не найден", "code": 404}), 404
    return jsonify(product), 200

