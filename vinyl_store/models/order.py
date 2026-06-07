"""Модель заказа."""

import random
import string
from datetime import datetime
from typing import Any

from easyApi import execute_query, get_connection


class OrderModel:
    """Работа с заказами."""

    @staticmethod
    def generate_order_number() -> str:
        """Сгенерировать уникальный номер заказа."""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"VV-{date_part}-{random_part}"

    @staticmethod
    def create(
        user_id: int,
        total_amount: float,
        shipping_address: str,
        shipping_city: str,
        shipping_postal_code: str,
        shipping_country: str,
        customer_phone: str,
        customer_email: str,
        payment_method: str = "card",
        notes: str = "",
        discount_amount: float = 0,
        shipping_cost: float = 0,
    ) -> dict[str, Any]:
        """Создать новый заказ."""
        order_number = OrderModel.generate_order_number()

        result = execute_query(
            "INSERT",
            "orders",
            {
                "user_id": user_id,
                "order_number": order_number,
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "shipping_cost": shipping_cost,
                "payment_method": payment_method,
                "payment_status": "pending",
                "status": "pending",
                "shipping_address": shipping_address,
                "shipping_city": shipping_city,
                "shipping_postal_code": shipping_postal_code,
                "shipping_country": shipping_country,
                "customer_phone": customer_phone,
                "customer_email": customer_email,
                "notes": notes,
            },
        )

        return {"order_id": result["insert_id"], "order_number": order_number}

    @staticmethod
    def add_item(
        order_id: int,
        product_id: int,
        title: str,
        artist: str,
        quantity: int,
        price: float,
        image_url: str = "",
    ) -> dict[str, Any]:
        """Добавить позицию в заказ."""
        return execute_query(
            "INSERT",
            "order_items",
            {
                "order_id": order_id,
                "product_id": product_id,
                "title": title,
                "artist": artist,
                "quantity": quantity,
                "price": price,
                "subtotal": price * quantity,
                "image_url": image_url,
            },
        )

    @staticmethod
    def get_by_id(order_id: int) -> dict[str, Any] | None:
        """Получить заказ по ID."""
        rows = execute_query("SELECT", "orders", where="id = %s", where_params=(order_id,))
        return rows[0] if rows else None

    @staticmethod
    def get_by_number(order_number: str) -> dict[str, Any] | None:
        """Получить заказ по номеру."""
        rows = execute_query("SELECT", "orders", where="order_number = %s", where_params=(order_number,))
        return rows[0] if rows else None

    @staticmethod
    def get_items(order_id: int) -> list[dict[str, Any]]:
        """Получить позиции заказа."""
        return execute_query(
            "SELECT",
            "order_items",
            where="order_id = %s",
            where_params=(order_id,),
        )

    @staticmethod
    def get_full_order(order_id: int) -> dict[str, Any] | None:
        """Получить заказ с позициями."""
        order = OrderModel.get_by_id(order_id)
        if not order:
            return None

        order["items"] = OrderModel.get_items(order_id)
        return order

    @staticmethod
    def get_by_user(user_id: int, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Получить заказы пользователя."""
        return execute_query(
            "SELECT",
            "orders",
            order="created_at DESC",
            where="user_id = %s",
            where_params=(user_id,),
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get_all(
        status: str | None = None,
        payment_status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
    ) -> tuple[list[dict[str, Any]], int]:
        """Получить все заказы с фильтрами."""
        where_parts = ["1=1"]
        params: list[Any] = []

        if status:
            where_parts.append("status = %s")
            params.append(status)

        if payment_status:
            where_parts.append("payment_status = %s")
            params.append(payment_status)

        where = " AND ".join(where_parts) if len(where_parts) > 1 else None

        # Общее количество
        count_result = execute_query(
            "SELECT",
            "orders",
            columns="COUNT(*) as total",
            where=where,
            where_params=params if params else None,
        )
        total = count_result[0]["total"] if count_result else 0

        # Заказы
        valid_sort = ["created_at", "total_amount", "status"]
        if sort_by not in valid_sort:
            sort_by = "created_at"

        orders = execute_query(
            "SELECT",
            "orders",
            order=f"{sort_by} {sort_order.upper()}",
            where=where,
            where_params=params if params else None,
            limit=limit,
            offset=offset,
        )

        return orders, total

    @staticmethod
    def update_status(order_id: int, status: str) -> dict[str, Any]:
        """Обновить статус заказа."""
        valid_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"]
        if status not in valid_statuses:
            raise ValueError(f"Недопустимый статус: {status}")

        update_data = {"status": status}
        if status == "shipped":
            update_data["shipped_at"] = datetime.now()
        elif status == "delivered":
            update_data["delivered_at"] = datetime.now()

        return execute_query("UPDATE", "orders", update_data, where="id = %s", where_params=(order_id,))

    @staticmethod
    def update_payment_status(order_id: int, payment_status: str) -> dict[str, Any]:
        """Обновить статус оплаты."""
        valid_statuses = ["pending", "paid", "failed", "refunded"]
        if payment_status not in valid_statuses:
            raise ValueError(f"Недопустимый статус оплаты: {payment_status}")

        return execute_query(
            "UPDATE",
            "orders",
            {"payment_status": payment_status},
            where="id = %s",
            where_params=(order_id,),
        )

    @staticmethod
    def update(order_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Обновить данные заказа."""
        # Защита от изменения критических полей
        protected_fields = ["id", "user_id", "order_number", "created_at"]
        for field in protected_fields:
            data.pop(field, None)

        return execute_query("UPDATE", "orders", data, where="id = %s", where_params=(order_id,))

    @staticmethod
    def cancel(order_id: int) -> dict[str, Any]:
        """Отменить заказ."""
        return OrderModel.update_status(order_id, "cancelled")

    @staticmethod
    def get_statistics() -> dict[str, Any]:
        """Получить статистику по заказам."""
        stats = execute_query(
            "SELECT",
            "orders",
            columns="""
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_count,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_count,
                SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) as shipped_count,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_count,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count
            """,
        )

        return stats[0] if stats else {}

    @staticmethod
    def create_order_with_items(
        user_id: int,
        cart_items: list[dict[str, Any]],
        shipping_data: dict[str, Any],
        payment_method: str = "card",
        promo_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Создать заказ с позициями из корзины.
        Использует транзакцию для целостности данных.
        """
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Рассчитываем суммы
            subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
            discount_amount = 0
            shipping_cost = 300  # Стандартная доставка

            # Бесплатная доставка от 5000₽
            if subtotal >= 5000:
                shipping_cost = 0

            total_amount = subtotal - discount_amount + shipping_cost

            # Создаём заказ
            order_number = OrderModel.generate_order_number()
            cursor.execute(
                """
                INSERT INTO orders (
                    user_id, order_number, total_amount, discount_amount, shipping_cost,
                    payment_method, payment_status, status,
                    shipping_address, shipping_city, shipping_postal_code, shipping_country,
                    customer_phone, customer_email, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    order_number,
                    total_amount,
                    discount_amount,
                    shipping_cost,
                    payment_method,
                    "pending",
                    "pending",
                    shipping_data.get("address", ""),
                    shipping_data.get("city", ""),
                    shipping_data.get("postal_code", ""),
                    shipping_data.get("country", "Russia"),
                    shipping_data.get("phone", ""),
                    shipping_data.get("email", ""),
                    shipping_data.get("notes", ""),
                ),
            )
            order_id = cursor.lastrowid

            # Добавляем позиции
            for item in cart_items:
                cursor.execute(
                    """
                    INSERT INTO order_items (
                        order_id, product_id, title, artist, quantity, price, subtotal, image_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        item["product_id"],
                        item["title"],
                        item["artist"],
                        item["quantity"],
                        item["price"],
                        item["price"] * item["quantity"],
                        item.get("image_url", ""),
                    ),
                )

                # Уменьшаем склад
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s",
                    (item["quantity"], item["product_id"]),
                )

            conn.commit()

            return {"order_id": order_id, "order_number": order_number, "total_amount": total_amount}

        except Exception as e:
            if conn:
                conn.rollback()
            raise e

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
