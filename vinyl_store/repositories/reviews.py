"""SQL repository for reviews."""

from __future__ import annotations

from typing import Any

from vinyl_store.repositories.base import delete, insert, raw_query, select, update


def add_review(data: dict[str, Any]) -> int:
    return int(insert("reviews", data)["insert_id"])


def list_for_product(product_id: int) -> list[dict[str, Any]]:
    return select(
        "reviews r",
        columns="r.id, r.product_id, r.user_id, u.username, r.rating, r.title, r.content, r.is_verified, r.is_approved, r.created_at",
        join="JOIN users u ON r.user_id = u.id",
        where="r.product_id = %s AND r.is_approved = TRUE",
        where_params=[product_id],
        order="r.created_at DESC",
    )


def list_all() -> list[dict[str, Any]]:
    return select(
        "reviews r",
        columns="r.id, r.product_id, p.title AS product_title, r.user_id, u.username, r.rating, r.title, r.content, r.is_approved, r.created_at",
        join="JOIN users u ON r.user_id = u.id JOIN products p ON r.product_id = p.id",
        order="r.created_at DESC",
    )


def approve(review_id: int, approved: bool) -> dict[str, Any]:
    return update("reviews", {"is_approved": approved}, "id = %s", [review_id])


def delete_review(review_id: int) -> dict[str, Any]:
    return delete("reviews", "id = %s", [review_id])


def refresh_product_rating(product_id: int) -> None:
    raw_query(
        """
        UPDATE products p
        SET rating = COALESCE((SELECT AVG(r.rating) FROM reviews r WHERE r.product_id = %s AND r.is_approved = TRUE), 0),
            review_count = (SELECT COUNT(*) FROM reviews r WHERE r.product_id = %s AND r.is_approved = TRUE)
        WHERE p.id = %s
        """,
        [product_id, product_id, product_id],
    )
