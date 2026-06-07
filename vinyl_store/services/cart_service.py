"""Business logic for cart operations."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from vinyl_store.middleware.errors import ValidationError
from vinyl_store.repositories import cart as cart_repo
from vinyl_store.repositories import catalog as catalog_repo


def get_cart(user_id: int) -> dict[str, Any]:
    items = cart_repo.get_cart_items(user_id)
    subtotal = sum(Decimal(str(item["subtotal"])) for item in items)
    return {"items": items, "total_items": sum(item["quantity"] for item in items), "subtotal": subtotal}


def add_to_cart(user_id: int, product_id: int, quantity: int) -> dict[str, Any]:
    product = catalog_repo.get_product(product_id)
    if not product:
        raise ValidationError("Product not found")
    if product["stock_quantity"] < quantity:
        raise ValidationError("Not enough product stock")
    cart_repo.upsert_item(user_id, product_id, quantity)
    return get_cart(user_id)


def update_quantity(user_id: int, product_id: int, quantity: int) -> dict[str, Any]:
    product = catalog_repo.get_product(product_id)
    if not product:
        raise ValidationError("Product not found")
    if product["stock_quantity"] < quantity:
        raise ValidationError("Not enough product stock")
    result = cart_repo.update_item(user_id, product_id, quantity)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Cart item not found")
    return get_cart(user_id)


def remove_item(user_id: int, item_id: int) -> dict[str, Any]:
    result = cart_repo.delete_item(user_id, item_id)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Cart item not found")
    return get_cart(user_id)
