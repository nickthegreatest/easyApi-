"""Модель заказов: операции для orders и order_items."""

from __future__ import annotations

from typing import Any

from easyApi.db.connection import execute_query


def create_order_record(user_id: int, total_price: float) -> dict[str, Any]:
    """Создаёт запись заказа."""
    return execute_query(
        "INSERT",
        "orders",
        {"user_id": user_id, "total_price": total_price, "status": "pending"},
    )


def add_order_item(order_id: int, product_id: int, quantity: int, price: float) -> dict[str, Any]:
    """Добавляет позицию в заказ."""
    return execute_query(
        "INSERT",
        "order_items",
        {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
        },
    )


def get_orders_by_user(user_id: int) -> list[dict[str, Any]]:
    """Возвращает заказы пользователя с JOIN к order_items и products."""
    return execute_query(
        "SELECT",
        "orders",
        columns=(
            "orders.id AS order_id, orders.user_id, orders.total_price, "
            "orders.status, orders.created_at, "
            "order_items.product_id, order_items.quantity, "
            "order_items.price AS item_price, products.name AS product_name"
        ),
        join=(
            "LEFT JOIN order_items ON orders.id = order_items.order_id "
            "LEFT JOIN products ON order_items.product_id = products.id"
        ),
        where="orders.user_id = %s",
        where_params=(user_id,),
    )


def update_order_status(order_id: int, status: str) -> dict[str, Any]:
    """Обновляет статус заказа."""
    return execute_query(
        "UPDATE",
        "orders",
        {"status": status},
        where="id = %s",
        where_params=(order_id,),
    )

