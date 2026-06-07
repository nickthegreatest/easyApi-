"""Модель товаров: CRUD для таблицы products."""

from __future__ import annotations

from typing import Any

from easyApi.db.connection import execute_query


def get_all_products() -> list[dict[str, Any]]:
    """Возвращает список всех товаров."""
    return execute_query("SELECT", "products")


def get_product_by_id(product_id: int) -> dict[str, Any] | None:
    """Возвращает товар по ID."""
    rows = execute_query(
        "SELECT",
        "products",
        where="id = %s",
        where_params=(product_id,),
    )
    return rows[0] if rows else None


def add_product(name: str, price: float, url: str, description: str) -> dict[str, Any]:
    """Добавляет новый товар."""
    return execute_query(
        "INSERT",
        "products",
        {"name": name, "price": price, "url": url, "description": description},
    )


def update_product(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """Обновляет данные товара."""
    return execute_query(
        "UPDATE",
        "products",
        data,
        where="id = %s",
        where_params=(product_id,),
    )


def delete_product(product_id: int) -> dict[str, Any]:
    """Удаляет товар по ID."""
    return execute_query(
        "DELETE",
        "products",
        where="id = %s",
        where_params=(product_id,),
    )

