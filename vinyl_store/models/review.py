"""Модель отзывов."""

from typing import Any

from easyApi import execute_query


class ReviewModel:
    """Работа с отзывами."""

    @staticmethod
    def create(
        product_id: int,
        user_id: int,
        rating: int,
        content: str,
        title: str = "",
    ) -> dict[str, Any]:
        """Создать отзыв."""
        return execute_query(
            "INSERT",
            "reviews",
            {
                "product_id": product_id,
                "user_id": user_id,
                "rating": rating,
                "content": content,
                "title": title,
                "is_verified": True,  # Покупатель — проверенный отзыв
            },
        )

    @staticmethod
    def get_by_product(product_id: int, approved_only: bool = True, limit: int = 50) -> list[dict[str, Any]]:
        """Получить отзывы к товару."""
        columns = """
            reviews.*,
            users.username,
            users.first_name,
            users.last_name
        """
        join = "INNER JOIN users ON reviews.user_id = users.id"
        where = "reviews.product_id = %s"
        params: list[Any] = [product_id]

        if approved_only:
            where += " AND reviews.is_approved = TRUE"

        return execute_query(
            "SELECT",
            "reviews",
            columns=columns,
            join=join,
            where=where,
            where_params=params,
            order="reviews.created_at DESC",
            limit=limit,
        )

    @staticmethod
    def get_by_user(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Получить отзывы пользователя."""
        columns = """
            reviews.*,
            products.title,
            products.artist,
            products.image_url
        """
        join = "INNER JOIN products ON reviews.product_id = products.id"
        return execute_query(
            "SELECT",
            "reviews",
            columns=columns,
            join=join,
            where="reviews.user_id = %s",
            where_params=(user_id,),
            order="reviews.created_at DESC",
            limit=limit,
        )

    @staticmethod
    def get_by_id(review_id: int) -> dict[str, Any] | None:
        """Получить отзыв по ID."""
        rows = execute_query("SELECT", "reviews", where="id = %s", where_params=(review_id,))
        return rows[0] if rows else None

    @staticmethod
    def approve(review_id: int) -> dict[str, Any]:
        """Одобрить отзыв."""
        return execute_query(
            "UPDATE",
            "reviews",
            {"is_approved": True},
            where="id = %s",
            where_params=(review_id,),
        )

    @staticmethod
    def reject(review_id: int) -> dict[str, Any]:
        """Отклонить отзыв."""
        return execute_query(
            "UPDATE",
            "reviews",
            {"is_approved": False},
            where="id = %s",
            where_params=(review_id,),
        )

    @staticmethod
    def delete(review_id: int, user_id: int | None = None) -> dict[str, Any]:
        """Удалить отзыв."""
        if user_id:
            return execute_query(
                "DELETE",
                "reviews",
                where="id = %s AND user_id = %s",
                where_params=(review_id, user_id),
            )
        return execute_query("DELETE", "reviews", where="id = %s", where_params=(review_id,))

    @staticmethod
    def get_pending(limit: int = 50) -> list[dict[str, Any]]:
        """Получить отзывы на модерацию."""
        columns = """
            reviews.*,
            users.username,
            products.title,
            products.artist
        """
        join = """
            INNER JOIN users ON reviews.user_id = users.id
            INNER JOIN products ON reviews.product_id = products.id
        """
        return execute_query(
            "SELECT",
            "reviews",
            columns=columns,
            join=join,
            where="reviews.is_approved = FALSE",
            order="reviews.created_at DESC",
            limit=limit,
        )

    @staticmethod
    def get_statistics(product_id: int) -> dict[str, Any]:
        """Получить статистику отзывов для товара."""
        stats = execute_query(
            "SELECT",
            "reviews",
            columns="""
                COUNT(*) as total,
                AVG(rating) as avg_rating,
                SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as rating_5,
                SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as rating_4,
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as rating_3,
                SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as rating_2,
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as rating_1
            """,
            where="product_id = %s AND is_approved = TRUE",
            where_params=(product_id,),
        )

        return stats[0] if stats and stats[0]["total"] > 0 else {
            "total": 0,
            "avg_rating": 0,
            "rating_5": 0,
            "rating_4": 0,
            "rating_3": 0,
            "rating_2": 0,
            "rating_1": 0,
        }
