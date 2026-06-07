"""Модель корзины: операции для таблицы cart_items."""

from __future__ import annotations

from typing import Any

from easyApi.db.connection import execute_query


def add_to_cart(user_id: int, product_id: int, quantity: int, price: float) -> dict[str, Any]:
    """Добавляет товар в корзину или увеличивает количество."""
    existing = execute_query(
        "SELECT",
        "cart_items",
        where="user_id = %s AND product_id = %s",
        where_params=(user_id, product_id),
    )
    if existing:
        new_quantity = existing[0]["quantity"] + quantity
        return execute_query(
            "UPDATE",
            "cart_items",
            {"quantity": new_quantity, "price": price},
            where="user_id = %s AND product_id = %s",
            where_params=(user_id, product_id),
        )
    return execute_query(
        "INSERT",
        "cart_items",
        {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
        },
    )


def get_cart(user_id: int) -> list[dict[str, Any]]:
    """Возвращает корзину с JOIN к products."""
    return execute_query(
        "SELECT",
        "cart_items",
        columns="cart_items.*, products.name AS product_name, products.url AS product_url",
        join="INNER JOIN products ON cart_items.product_id = products.id",
        where="cart_items.user_id = %s",
        where_params=(user_id,),
    )


def remove_from_cart(user_id: int, product_id: int) -> dict[str, Any]:
    """Удаляет товар из корзины."""
    return execute_query(
        "DELETE",
        "cart_items",
        where="user_id = %s AND product_id = %s",
        where_params=(user_id, product_id),
    )


def clear_cart(user_id: int) -> dict[str, Any]:
    """Очищает корзину пользователя."""
    return execute_query(
        "DELETE",
        "cart_items",
        where="user_id = %s",
        where_params=(user_id,),
    )

