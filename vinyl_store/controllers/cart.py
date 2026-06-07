"""Контроллер корзины."""

from flask import Blueprint, request, jsonify

from vinyl_store.models.cart import CartModel
from vinyl_store.models.product import ProductModel
from vinyl_store.services.security import token_required

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/")
@token_required
def get_cart(current_user):
    """Получить корзину текущего пользователя."""
    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify(cart)


@cart_bp.route("/add", methods=["POST"])
@token_required
def add_to_cart(current_user):
    """Добавить товар в корзину."""
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = max(1, int(data.get("quantity", 1)))

    if not product_id:
        return jsonify({"error": "product_id обязателен"}), 400

    # Проверяем товар
    product = ProductModel.get_by_id(product_id)
    if not product:
        return jsonify({"error": "Товар не найден"}), 404

    # Проверяем наличие
    if product["stock_quantity"] < quantity:
        return jsonify({"error": "Недостаточно товара на складе"}), 400

    # Добавляем в корзину
    result = CartModel.add_item(current_user["id"], product_id, quantity)

    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify({
        "message": "Товар добавлен в корзину",
        "cart": cart,
    })


@cart_bp.route("/update", methods=["POST"])
@token_required
def update_cart(current_user):
    """Обновить количество товара в корзине."""
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id:
        return jsonify({"error": "product_id обязателен"}), 400

    if quantity < 0:
        return jsonify({"error": "quantity должен быть >= 0"}), 400

    # Проверяем товар
    product = ProductModel.get_by_id(product_id)
    if not product:
        return jsonify({"error": "Товар не найден"}), 404

    # Проверяем наличие
    if quantity > 0 and product["stock_quantity"] < quantity:
        return jsonify({"error": "Недостаточно товара на складе"}), 400

    CartModel.update_quantity(current_user["id"], product_id, quantity)

    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify({
        "message": "Корзина обновлена",
        "cart": cart,
    })


@cart_bp.route("/remove", methods=["POST"])
@token_required
def remove_from_cart(current_user):
    """Удалить товар из корзины."""
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "product_id обязателен"}), 400

    CartModel.remove_item(current_user["id"], product_id)

    cart = CartModel.get_full_cart(current_user["id"])
    return jsonify({
        "message": "Товар удалён из корзины",
        "cart": cart,
    })


@cart_bp.route("/clear", methods=["POST"])
@token_required
def clear_cart(current_user):
    """Очистить корзину."""
    CartModel.clear(current_user["id"])
    return jsonify({"message": "Корзина очищена"})


@cart_bp.route("/count")
@token_required
def get_cart_count(current_user):
    """Получить количество товаров в корзине."""
    total = CartModel.get_total(current_user["id"])
    return jsonify({
        "total_items": total["total_items"],
        "subtotal": total["subtotal"],
    })
