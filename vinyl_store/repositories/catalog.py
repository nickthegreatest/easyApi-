"""SQL repository for catalog tables."""

from __future__ import annotations

from typing import Any

from vinyl_store.repositories.base import delete, insert, raw_query, select, update

PRODUCT_COLUMNS = """
p.id, p.title, p.artist, p.slug, p.description, p.price, p.old_price, p.stock_quantity,
p.category_id, c.name AS category_name, p.label_id, l.name AS label_name, p.release_year,
p.country, p.format, p.weight_grams, p.speed_rpm, p.color, p.is_limited, p.is_new,
p.image_url, p.rating, p.review_count, p.created_at, p.updated_at
""".strip()
PRODUCT_JOIN = "LEFT JOIN categories c ON p.category_id = c.id LEFT JOIN labels l ON p.label_id = l.id"


def list_products(filters: dict[str, Any]) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if filters.get("q"):
        clauses.append("(p.title LIKE %s OR p.artist LIKE %s OR p.description LIKE %s)")
        term = f"%{filters['q']}%"
        params.extend([term, term, term])
    if filters.get("category_id"):
        clauses.append("p.category_id = %s")
        params.append(filters["category_id"])
    if filters.get("genre"):
        clauses.append("c.slug = %s")
        params.append(filters["genre"])
    if filters.get("min_price"):
        clauses.append("p.price >= %s")
        params.append(filters["min_price"])
    if filters.get("max_price"):
        clauses.append("p.price <= %s")
        params.append(filters["max_price"])
    where = " AND ".join(clauses) if clauses else None
    order_map = {
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "rating": "p.rating DESC",
        "new": "p.created_at DESC",
        "year": "p.release_year DESC",
    }
    order = order_map.get(filters.get("sort"), "p.created_at DESC")
    return select(
        "products p",
        columns=PRODUCT_COLUMNS,
        join=PRODUCT_JOIN,
        where=where,
        where_params=params,
        order=order,
        limit=filters.get("limit", 48),
        offset=filters.get("offset", 0),
    )


def get_product(product_id: int) -> dict[str, Any] | None:
    rows = select("products p", columns=PRODUCT_COLUMNS, join=PRODUCT_JOIN, where="p.id = %s", where_params=[product_id], limit=1)
    return rows[0] if rows else None


def list_categories() -> list[dict[str, Any]]:
    return select("categories", order="name ASC")


def create_product(data: dict[str, Any]) -> int:
    return int(insert("products", data)["insert_id"])


def update_product(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update("products", data, "id = %s", [product_id])


def delete_product(product_id: int) -> dict[str, Any]:
    return delete("products", "id = %s", [product_id])


def create_category(data: dict[str, Any]) -> int:
    return int(insert("categories", data)["insert_id"])


def update_category(category_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update("categories", data, "id = %s", [category_id])


def delete_category(category_id: int) -> dict[str, Any]:
    return delete("categories", "id = %s", [category_id])


def record_view(user_id: int | None, product_id: int) -> None:
    insert("view_history", {"user_id": user_id, "product_id": product_id})


def sales_stats() -> dict[str, Any]:
    totals = raw_query(
        """
        SELECT COUNT(*) AS orders_count, COALESCE(SUM(total_amount), 0) AS revenue,
               COALESCE(AVG(total_amount), 0) AS average_order
        FROM orders
        WHERE status <> 'cancelled'
        """,
        fetch_one=True,
    )
    top_products = raw_query(
        """
        SELECT oi.product_id, oi.title, oi.artist, SUM(oi.quantity) AS sold, SUM(oi.subtotal) AS revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status <> 'cancelled'
        GROUP BY oi.product_id, oi.title, oi.artist
        ORDER BY sold DESC
        LIMIT 5
        """
    )
    return {"totals": totals, "top_products": top_products}
