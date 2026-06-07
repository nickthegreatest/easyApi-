"""Контроллер заказов."""

import random
from datetime import datetime

from flask import Blueprint, request, jsonify

from vinyl_store.models.cart import CartModel
from vinyl_store.models.order import OrderModel
from vinyl_store.models.product import ProductModel
from vinyl_store.services.security import token_required

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
@token_required
def get_orders(current_user):
    """Получить заказы текущего пользователя."""
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 20))))
    offset = (page - 1) * per_page

    orders = OrderModel.get_by_user(current_user["id"], limit=per_page, offset=offset)

    # Добавляем количество товаров в каждый заказ
    for order in orders:
        items = OrderModel.get_items(order["id"])
        order["items_count"] = sum(item["quantity"] for item in items)

    return jsonify({
        "orders": orders,
        "pagination": {
            "page": page,
            "per_page": per_page,
        },
    })


@orders_bp.route("/<int:order_id>")
@token_required
def get_order(current_user, order_id):
    """Получить详细信息 заказа."""
    order = OrderModel.get_full_order(order_id)
    if not order:
        return jsonify({"error": "Заказ не найден"}), 404

    # Проверка доступа
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Доступ запрещён"}), 403

    return jsonify(order)


@orders_bp.route("/create", methods=["POST"])
@token_required
def create_order(current_user):
    """Создать заказ из корзины."""
    data = request.get_json() or {}

    # Получаем корзину
    cart_items = CartModel.get_items(current_user["id"])
    if not cart_items:
        return jsonify({"error": "Корзина пуста"}), 400

    # Проверяем наличие всех товаров
    for item in cart_items:
        if item["stock_quantity"] < item["quantity"]:
            return jsonify({
                "error": f"Товар '{item['title']}' недоступен в нужном количестве",
            }), 400

    # Данные доставки
    shipping_data = {
        "address": data.get("address", "") or current_user.get("address", ""),
        "city": data.get("city", ""),
        "postal_code": data.get("postal_code", ""),
        "country": data.get("country", "Russia"),
        "phone": data.get("phone", "") or current_user.get("phone", ""),
        "email": data.get("email", "") or current_user.get("email", ""),
        "notes": data.get("notes", ""),
    }

    # Валидация обязательных полей
    if not shipping_data["address"]:
        return jsonify({"error": "Адрес доставки обязателен"}), 400
    if not shipping_data["city"]:
        return jsonify({"error": "Город обязателен"}), 400
    if not shipping_data["phone"]:
        return jsonify({"error": "Телефон обязателен"}), 400

    payment_method = data.get("payment_method", "card")
    if payment_method not in ["card", "cash", "online"]:
        payment_method = "card"

    try:
        # Создаём заказ с транзакцией
        result = OrderModel.create_order_with_items(
            user_id=current_user["id"],
            cart_items=cart_items,
            shipping_data=shipping_data,
            payment_method=payment_method,
        )

        # Очищаем корзину
        CartModel.clear(current_user["id"])

        return jsonify({
            "message": "Заказ успешно создан",
            "order": result,
        }), 201

    except Exception as e:
        return jsonify({"error": f"Ошибка создания заказа: {str(e)}"}), 500


@orders_bp.route("/<int:order_id>/pay", methods=["POST"])
@token_required
def pay_order(current_user, order_id):
    """
    Оплатить заказ (фейковая оплата).
    Симулирует процесс оплаты с вероятностью успеха 95%.
    """
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Заказ не найден"}), 404

    # Проверка доступа
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Доступ запрещён"}), 403

    # Проверка статуса
    if order["payment_status"] == "paid":
        return jsonify({"error": "Заказ уже оплачен"}), 400
    if order["status"] in ["cancelled", "delivered"]:
        return jsonify({"error": "Нельзя оплатить этот заказ"}), 400

    # Фейковая оплата
    payment_success = random.random() < 0.95  # 95% успеха

    if payment_success:
        OrderModel.update_payment_status(order_id, "paid")
        OrderModel.update_status(order_id, "confirmed")

        return jsonify({
            "message": "Оплата успешна",
            "payment_status": "paid",
            "order_status": "confirmed",
        })
    else:
        OrderModel.update_payment_status(order_id, "failed")
        return jsonify({
            "error": "Платёж не прошёл. Попробуйте ещё раз.",
            "payment_status": "failed",
        }), 400


@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@token_required
def cancel_order(current_user, order_id):
    """Отменить заказ."""
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({"error": "Заказ не найден"}), 404

    # Проверка доступа
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Доступ запрещён"}), 403

    # Можно отменить только pending/confirmed
    if order["status"] not in ["pending", "confirmed"]:
        return jsonify({"error": "Нельзя отменить этот заказ"}), 400

    OrderModel.cancel(order_id)

    return jsonify({"message": "Заказ отменён"})


@orders_bp.route("/<int:order_id>/invoice")
@token_required
def get_invoice(current_user, order_id):
    """Получить счёт/чек заказа."""
    order = OrderModel.get_full_order(order_id)
    if not order:
        return jsonify({"error": "Заказ не найден"}), 404

    # Проверка доступа
    if order["user_id"] != current_user["id"] and current_user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Доступ запрещён"}), 403

    return jsonify({
        "invoice": {
            "order_number": order["order_number"],
            "created_at": str(order["created_at"]),
            "customer": {
                "name": f"{order.get('customer_email', '')}",
                "email": order.get("customer_email", ""),
                "phone": order.get("customer_phone", ""),
            },
            "shipping": {
                "address": order["shipping_address"],
                "city": order["shipping_city"],
                "postal_code": order["shipping_postal_code"],
                "country": order["shipping_country"],
            },
            "items": order["items"],
            "totals": {
                "subtotal": sum(item["subtotal"] for item in order["items"]),
                "discount": order.get("discount_amount", 0),
                "shipping": order.get("shipping_cost", 0),
                "total": order["total_amount"],
            },
            "payment": {
                "method": order["payment_method"],
                "status": order["payment_status"],
            },
        },
    })
