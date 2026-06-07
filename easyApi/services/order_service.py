"""Сервис заказов: создание заказа из корзины и история заказов."""

from __future__ import annotations

from typing import Any

import pymysql

from easyApi.db.connection import get_connection
from easyApi.db.exceptions import DatabaseQueryError
from easyApi.models import cart_model, order_model


def create_order(user_id: int) -> dict[str, Any]:
    """Создаёт заказ из корзины пользователя в одной транзакции.

    Args:
        user_id: дентификатор пользователя.

    Returns:
        Словарь с order_id и total_price.

    Raises:
        DatabaseQueryError: Если корзина пуста или произошла ошибка БД.
    """
    cart_items = cart_model.get_cart(user_id)
    if not cart_items:
        raise DatabaseQueryError("Корзина пуста", code=400)

    total_price = sum(float(item["price"]) * int(item["quantity"]) for item in cart_items)

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO `orders` (`user_id`, `total_price`, `status`) VALUES (%s, %s, %s)",
            (user_id, total_price, "pending"),
        )
        order_id = cursor.lastrowid

        for item in cart_items:
            cursor.execute(
                "INSERT INTO `order_items` (`order_id`, `product_id`, `quantity`, `price`) "
                "VALUES (%s, %s, %s, %s)",
                (order_id, item["product_id"], item["quantity"], item["price"]),
            )

        cursor.execute("DELETE FROM `cart_items` WHERE `user_id` = %s", (user_id,))
        connection.commit()

        return {"order_id": order_id, "total_price": total_price}
    except pymysql.Error as exc:
        if connection:
            connection.rollback()
        raise DatabaseQueryError(str(exc)) from exc
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_user_orders(user_id: int) -> list[dict[str, Any]]:
    """Возвращает заказы пользователя с позициями.

    Args:
        user_id: дентификатор пользователя.

    Returns:
        Список заказов с вложенными items.
    """
    rows = order_model.get_orders_by_user(user_id)
    orders_map: dict[int, dict[str, Any]] = {}

    for row in rows:
        order_id = row["order_id"]
        if order_id not in orders_map:
            orders_map[order_id] = {
                "order_id": order_id,
                "user_id": row["user_id"],
                "total_price": float(row["total_price"]),
                "status": row["status"],
                "created_at": row["created_at"],
                "items": [],
            }
        if row.get("product_id"):
            orders_map[order_id]["items"].append(
                {
                    "product_id": row["product_id"],
                    "product_name": row.get("product_name"),
                    "quantity": row["quantity"],
                    "price": float(row["item_price"]),
                }
            )

    return list(orders_map.values())

