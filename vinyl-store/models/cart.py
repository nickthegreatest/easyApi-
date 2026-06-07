"""Модель корзины."""

from typing import Any

from easyApi import execute_query


class CartModel:
    """Работа с корзиной."""

    @staticmethod
    def get_items(user_id: int) -> list[dict[str, Any]]:
        """Получить все товары в корзине пользователя."""
        columns = """
            cart_items.*,
            products.title,
            products.artist,
            products.price,
            products.image_url,
            products.stock_quantity
        """
        join = "INNER JOIN products ON cart_items.product_id = products.id"
        return execute_query(
            "SELECT",
            "cart_items",
            columns=columns,
            join=join,
            where="cart_items.user_id = %s",
            where_params=(user_id,),
        )

    @staticmethod
    def get_item(user_id: int, product_id: int) -> dict[str, Any] | None:
        """Получить конкретный товар в корзине."""
        rows = execute_query(
            "SELECT",
            "cart_items",
            where="user_id = %s AND product_id = %s",
            where_params=(user_id, product_id),
        )
        return rows[0] if rows else None

    @staticmethod
    def add_item(user_id: int, product_id: int, quantity: int = 1) -> dict[str, Any]:
        """Добавить товар в корзину."""
        existing = CartModel.get_item(user_id, product_id)

        if existing:
            # Увеличиваем количество
            new_quantity = existing["quantity"] + quantity
            return execute_query(
                "UPDATE",
                "cart_items",
                {"quantity": new_quantity},
                where="user_id = %s AND product_id = %s",
                where_params=(user_id, product_id),
            )
        else:
            # Добавляем новый товар
            return execute_query(
                "INSERT",
                "cart_items",
                {
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity,
                },
            )

    @staticmethod
    def update_quantity(user_id: int, product_id: int, quantity: int) -> dict[str, Any]:
        """Обновить количество товара в корзине."""
        if quantity <= 0:
            return CartModel.remove_item(user_id, product_id)

        return execute_query(
            "UPDATE",
            "cart_items",
            {"quantity": quantity},
            where="user_id = %s AND product_id = %s",
            where_params=(user_id, product_id),
        )

    @staticmethod
    def remove_item(user_id: int, product_id: int) -> dict[str, Any]:
        """Удалить товар из корзины."""
        return execute_query(
            "DELETE",
            "cart_items",
            where="user_id = %s AND product_id = %s",
            where_params=(user_id, product_id),
        )

    @staticmethod
    def clear(user_id: int) -> dict[str, Any]:
        """Очистить корзину пользователя."""
        return execute_query("DELETE", "cart_items", where="user_id = %s", where_params=(user_id,))

    @staticmethod
    def get_total(user_id: int) -> dict[str, Any]:
        """Получить общую сумму корзины."""
        columns = """
            SUM(products.price * cart_items.quantity) as subtotal,
            SUM(cart_items.quantity) as total_items
        """
        join = "INNER JOIN products ON cart_items.product_id = products.id"
        rows = execute_query(
            "SELECT",
            "cart_items",
            columns=columns,
            join=join,
            where="cart_items.user_id = %s",
            where_params=(user_id,),
        )

        result = rows[0] if rows else {"subtotal": 0, "total_items": 0}
        return {
            "subtotal": float(result["subtotal"]) if result["subtotal"] else 0,
            "total_items": result["total_items"] or 0,
        }

    @staticmethod
    def get_full_cart(user_id: int) -> dict[str, Any]:
        """Получить полную информацию о корзине."""
        items = CartModel.get_items(user_id)
        total = CartModel.get_total(user_id)

        return {
            "items": items,
            "subtotal": total["subtotal"],
            "total_items": total["total_items"],
        }
