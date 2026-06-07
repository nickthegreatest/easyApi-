"""Модель категории."""

from typing import Any

from easyApi import execute_query


class CategoryModel:
    """Работа с категориями."""

    @staticmethod
    def get_all() -> list[dict[str, Any]]:
        """Получить все категории."""
        return execute_query("SELECT", "categories", order="name ASC")

    @staticmethod
    def get_by_slug(slug: str) -> dict[str, Any] | None:
        """Получить категорию по slug."""
        rows = execute_query("SELECT", "categories", where="slug = %s", where_params=(slug,))
        return rows[0] if rows else None

    @staticmethod
    def get_by_id(category_id: int) -> dict[str, Any] | None:
        """Получить категорию по ID."""
        rows = execute_query("SELECT", "categories", where="id = %s", where_params=(category_id,))
        return rows[0] if rows else None

    @staticmethod
    def create(name: str, slug: str, description: str = "") -> dict[str, Any]:
        """Создать категорию."""
        return execute_query("INSERT", "categories", {"name": name, "slug": slug, "description": description})

    @staticmethod
    def update(category_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Обновить категорию."""
        return execute_query("UPDATE", "categories", data, where="id = %s", where_params=(category_id,))

    @staticmethod
    def delete(category_id: int) -> dict[str, Any]:
        """Удалить категорию."""
        return execute_query("DELETE", "categories", where="id = %s", where_params=(category_id,))

    @staticmethod
    def get_with_counts() -> list[dict[str, Any]]:
        """Получить категории с количеством товаров."""
        return execute_query(
            "SELECT",
            "categories",
            columns="categories.*, COUNT(products.id) as product_count",
            join="LEFT JOIN products ON categories.id = products.category_id",
            group_by="categories.id",
        )
