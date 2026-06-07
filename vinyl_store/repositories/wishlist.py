"""SQL repository for wishlist."""

from __future__ import annotations

from vinyl_store.repositories.base import delete, raw_query, select


def add(user_id: int, product_id: int) -> None:
    raw_query("INSERT IGNORE INTO wishlist (user_id, product_id) VALUES (%s, %s)", [user_id, product_id])


def list_items(user_id: int):
    return select(
        "wishlist w",
        columns="w.id, w.product_id, w.created_at, p.title, p.artist, p.price, p.image_url, p.rating",
        join="JOIN products p ON w.product_id = p.id",
        where="w.user_id = %s",
        where_params=[user_id],
        order="w.created_at DESC",
    )


def remove(user_id: int, product_id: int):
    return delete("wishlist", "user_id = %s AND product_id = %s", [user_id, product_id])
