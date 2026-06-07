"""SQL repository for orders and order_items."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from easyApi import get_connection
from vinyl_store.repositories.base import raw_query, select, update


def list_user_orders(user_id: int) -> list[dict[str, Any]]:
    return select("orders", where="user_id = %s", where_params=[user_id], order="created_at DESC")


def list_all_orders() -> list[dict[str, Any]]:
    return select(
        "orders o",
        columns="o.*, u.username, u.email",
        join="JOIN users u ON o.user_id = u.id",
        order="o.created_at DESC",
    )


def get_order_items(order_id: int) -> list[dict[str, Any]]:
    return select("order_items", where="order_id = %s", where_params=[order_id], order="id ASC")


def get_active_promo(code: str) -> dict[str, Any] | None:
    rows = raw_query(
        """
        SELECT * FROM promo_codes
        WHERE code = %s
          AND is_active = TRUE
          AND (valid_from IS NULL OR valid_from <= CURRENT_DATE())
          AND (valid_until IS NULL OR valid_until >= CURRENT_DATE())
          AND (max_uses IS NULL OR used_count < max_uses)
        LIMIT 1
        """,
        [code],
    )
    return rows[0] if rows else None


def create_from_cart(user_id: int, payload: dict[str, Any], promo: dict[str, Any] | None, discount: Decimal) -> dict[str, Any]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ci.product_id, ci.quantity, p.title, p.artist, p.price, p.stock_quantity, p.image_url
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.user_id = %s
                FOR UPDATE
                """,
                [user_id],
            )
            items = list(cursor.fetchall())
            if not items:
                raise ValueError("Cart is empty")
            subtotal = sum(Decimal(str(item["price"])) * item["quantity"] for item in items)
            shipping = Decimal("0.00") if subtotal >= Decimal("5000.00") else Decimal("300.00")
            total = subtotal + shipping - discount
            cursor.execute("SELECT CONCAT('VV-', DATE_FORMAT(NOW(), '%y%m%d'), '-', LPAD(COUNT(*) + 1, 4, '0')) AS number FROM orders")
            order_number = cursor.fetchone()["number"]
            cursor.execute(
                """
                INSERT INTO orders (user_id, order_number, status, total_amount, discount_amount, shipping_cost,
                                    payment_method, shipping_address, shipping_city, shipping_postal_code,
                                    shipping_country, customer_phone, customer_email, notes)
                VALUES (%s, %s, 'pending', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    user_id,
                    order_number,
                    total,
                    discount,
                    shipping,
                    payload["payment_method"],
                    payload["shipping_address"],
                    payload["shipping_city"],
                    payload["shipping_postal_code"],
                    payload["shipping_country"],
                    payload["customer_phone"],
                    payload["customer_email"],
                    payload["notes"],
                ],
            )
            order_id = cursor.lastrowid
            for item in items:
                if item["quantity"] > item["stock_quantity"]:
                    raise ValueError(f"Not enough stock for {item['title']}")
                line_subtotal = Decimal(str(item["price"])) * item["quantity"]
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, title, artist, quantity, price, subtotal, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [order_id, item["product_id"], item["title"], item["artist"], item["quantity"], item["price"], line_subtotal, item["image_url"]],
                )
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s", [item["quantity"], item["product_id"]])
            cursor.execute("DELETE FROM cart_items WHERE user_id = %s", [user_id])
            if promo:
                cursor.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE id = %s", [promo["id"]])
        connection.commit()
        return {"id": order_id, "order_number": order_number, "subtotal": subtotal, "shipping_cost": shipping, "discount_amount": discount, "total_amount": total}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_status(order_id: int, status: str) -> dict[str, Any]:
    return update("orders", {"status": status}, "id = %s", [order_id])
