"""Модель продукта (виниловой пластинки)."""

from typing import Any

from easyApi import execute_query


class ProductModel:
    """Работа с товарами."""

    @staticmethod
    def get_all(
        limit: int = 12,
        offset: int = 0,
        category_id: int | None = None,
        label_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        in_stock: bool = False,
        is_new: bool = False,
        is_limited: bool = False,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Получить список товаров с фильтрами, сортировкой и пагинацией.
        Возвращает (товары, общее количество).
        """
        # Базовый запрос для подсчёта общего количества
        count_where_parts = ["1=1"]
        count_params: list[Any] = []

        # Базовый запрос для товаров
        columns = """
            products.*,
            categories.name as category_name,
            categories.slug as category_slug,
            labels.name as label_name
        """
        join = "LEFT JOIN categories ON products.category_id = categories.id LEFT JOIN labels ON products.label_id = labels.id"
        where_parts = ["1=1"]
        params: list[Any] = []

        # Фильтры
        if category_id:
            where_parts.append("products.category_id = %s")
            count_where_parts.append("category_id = %s")
            params.append(category_id)
            count_params.append(category_id)

        if label_id:
            where_parts.append("products.label_id = %s")
            count_where_parts.append("label_id = %s")
            params.append(label_id)
            count_params.append(label_id)

        if min_price is not None:
            where_parts.append("products.price >= %s")
            count_where_parts.append("price >= %s")
            params.append(min_price)
            count_params.append(min_price)

        if max_price is not None:
            where_parts.append("products.price <= %s")
            count_where_parts.append("price <= %s")
            params.append(max_price)
            count_params.append(max_price)

        if min_rating is not None:
            where_parts.append("products.rating >= %s")
            count_where_parts.append("rating >= %s")
            params.append(min_rating)
            count_params.append(min_rating)

        if in_stock:
            where_parts.append("products.stock_quantity > 0")
            count_where_parts.append("stock_quantity > 0")

        if is_new:
            where_parts.append("products.is_new = TRUE")
            count_where_parts.append("is_new = TRUE")

        if is_limited:
            where_parts.append("products.is_limited = TRUE")
            count_where_parts.append("is_limited = TRUE")

        if search:
            search_term = f"%{search}%"
            where_parts.append("(products.title LIKE %s OR products.artist LIKE %s)")
            count_where_parts.append("(title LIKE %s OR artist LIKE %s)")
            params.extend([search_term, search_term])
            count_params.extend([search_term, search_term])

        where = " AND ".join(where_parts)
        count_where = " AND ".join(count_where_parts)

        # Сортировка
        valid_sort_fields = ["price", "rating", "title", "artist", "release_year", "created_at"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        if sort_order.upper() not in ["ASC", "DESC"]:
            sort_order = "DESC"

        order = f"products.{sort_by} {sort_order.upper()}"

        # Получаем общее количество
        count_result = execute_query(
            "SELECT",
            "products",
            columns="COUNT(*) as total",
            where=count_where,
            where_params=count_params if count_params else None,
        )
        total = count_result[0]["total"] if count_result else 0

        # Получаем товары
        products = execute_query(
            "SELECT",
            "products",
            columns=columns,
            join=join,
            where=where,
            where_params=params if params else None,
            order=order,
            limit=limit,
            offset=offset,
        )

        return products, total

    @staticmethod
    def get_by_id(product_id: int) -> dict[str, Any] | None:
        """Получить товар по ID."""
        columns = """
            products.*,
            categories.name as category_name,
            categories.slug as category_slug,
            labels.name as label_name
        """
        join = "LEFT JOIN categories ON products.category_id = categories.id LEFT JOIN labels ON products.label_id = labels.id"
        rows = execute_query(
            "SELECT",
            "products",
            columns=columns,
            join=join,
            where="products.id = %s",
            where_params=(product_id,),
        )
        return rows[0] if rows else None

    @staticmethod
    def get_by_slug(slug: str) -> dict[str, Any] | None:
        """Получить товар по slug."""
        rows = execute_query("SELECT", "products", where="slug = %s", where_params=(slug,))
        return rows[0] if rows else None

    @staticmethod
    def create(data: dict[str, Any]) -> dict[str, Any]:
        """Создать товар."""
        return execute_query("INSERT", "products", data)

    @staticmethod
    def update(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Обновить товар."""
        return execute_query("UPDATE", "products", data, where="id = %s", where_params=(product_id,))

    @staticmethod
    def delete(product_id: int) -> dict[str, Any]:
        """Удалить товар."""
        return execute_query("DELETE", "products", where="id = %s", where_params=(product_id,))

    @staticmethod
    def get_new(limit: int = 8) -> list[dict[str, Any]]:
        """Получить новые поступления."""
        return execute_query(
            "SELECT",
            "products",
            where="is_new = TRUE",
            order="created_at DESC",
            limit=limit,
        )

    @staticmethod
    def get_bestsellers(limit: int = 8) -> list[dict[str, Any]]:
        """Получить популярные товары (по рейтингу)."""
        return execute_query(
            "SELECT",
            "products",
            where="rating > 0",
            order="rating DESC, review_count DESC",
            limit=limit,
        )

    @staticmethod
    def get_on_sale(limit: int = 8) -> list[dict[str, Any]]:
        """Получить товары со скидкой."""
        return execute_query(
            "SELECT",
            "products",
            where="old_price IS NOT NULL AND old_price > price",
            order="(old_price - price) / old_price DESC",
            limit=limit,
        )

    @staticmethod
    def update_stock(product_id: int, quantity: int) -> dict[str, Any]:
        """Обновить количество товара на складе."""
        return execute_query(
            "UPDATE",
            "products",
            {"stock_quantity": quantity},
            where="id = %s",
            where_params=(product_id,),
        )

    @staticmethod
    def decrease_stock(product_id: int, quantity: int) -> dict[str, Any]:
        """Уменьшить количество товара на складе."""
        return execute_query(
            "UPDATE",
            "products",
            {"stock_quantity": "stock_quantity - %s"},
            where="id = %s AND stock_quantity >= %s",
            where_params=(product_id, quantity, quantity),
        )

    @staticmethod
    def get_filters() -> dict[str, Any]:
        """Получить доступные фильтры."""
        categories = execute_query("SELECT", "categories", order="name ASC")
        labels = execute_query("SELECT", "labels", order="name ASC")

        price_range = execute_query(
            "SELECT",
            "products",
            columns="MIN(price) as min_price, MAX(price) as max_price",
        )

        return {
            "categories": categories,
            "labels": labels,
            "price_range": price_range[0] if price_range else {"min_price": 0, "max_price": 10000},
        }
