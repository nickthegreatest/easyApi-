"""Модель отзывов: операции для таблицы reviews."""

from __future__ import annotations

from typing import Any

from easyApi.db.connection import execute_query


def add_review(user_id: int, product_id: int, text: str, rating: int) -> dict[str, Any]:
    """Добавляет отзыв на товар."""
    return execute_query(
        "INSERT",
        "reviews",
        {
            "user_id": user_id,
            "product_id": product_id,
            "text": text,
            "rating": rating,
        },
    )


def get_reviews_by_product(product_id: int) -> list[dict[str, Any]]:
    """Возвращает отзывы на товар с именем автора."""
    return execute_query(
        "SELECT",
        "reviews",
        columns="reviews.*, users.username",
        join="INNER JOIN users ON reviews.user_id = users.id",
        where="reviews.product_id = %s",
        where_params=(product_id,),
    )


def delete_review(review_id: int, user_id: int) -> dict[str, Any]:
    """Удаляет отзыв, если он принадлежит пользователю."""
    return execute_query(
        "DELETE",
        "reviews",
        where="id = %s AND user_id = %s",
        where_params=(review_id, user_id),
    )

