"""SQL repository for cart_items."""

from __future__ import annotations

from typing import Any

from vinyl_store.repositories.base import delete, raw_query, select, update


def get_cart_items(user_id: int) -> list[dict[str, Any]]:
    return select(
        "cart_items ci",
        columns="ci.id, ci.product_id, ci.quantity, p.title, p.artist, p.price, p.stock_quantity, p.image_url, (ci.quantity * p.price) AS subtotal",
        join="JOIN products p ON ci.product_id = p.id",
        where="ci.user_id = %s",
        where_params=[user_id],
        order="ci.added_at DESC",
    )


def upsert_item(user_id: int, product_id: int, quantity: int) -> None:
    raw_query(
        """
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
        """,
        [user_id, product_id, quantity],
    )


def update_item(user_id: int, product_id: int, quantity: int) -> dict[str, Any]:
    return update("cart_items", {"quantity": quantity}, "user_id = %s AND product_id = %s", [user_id, product_id])


def delete_item(user_id: int, item_id: int) -> dict[str, Any]:
    return delete("cart_items", "user_id = %s AND id = %s", [user_id, item_id])


def clear_cart(user_id: int) -> dict[str, Any]:
    return delete("cart_items", "user_id = %s", [user_id])
