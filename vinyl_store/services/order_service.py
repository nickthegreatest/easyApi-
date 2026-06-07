"""Business logic for checkout and order history."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from vinyl_store.middleware.errors import ValidationError
from vinyl_store.repositories import orders as orders_repo

ALLOWED_STATUSES = {"pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"}


def _calculate_discount(subtotal: Decimal, promo: dict[str, Any] | None) -> Decimal:
    if not promo:
        return Decimal("0.00")
    if subtotal < Decimal(str(promo.get("min_order_amount") or 0)):
        raise ValidationError("Promo code minimum order amount is not reached")
    if promo["discount_type"] == "percent":
        return (subtotal * Decimal(str(promo["discount_value"])) / Decimal("100")).quantize(Decimal("0.01"))
    return min(Decimal(str(promo["discount_value"])), subtotal)


def create_order(user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    promo = orders_repo.get_active_promo(payload["promo_code"].upper()) if payload.get("promo_code") else None
    # Discount is recalculated in the transaction after cart subtotal is known.
    # We pass a provisional zero first, then repository creates order atomically.
    if promo:
        from vinyl_store.services.cart_service import get_cart

        subtotal = Decimal(str(get_cart(user_id)["subtotal"]))
        discount = _calculate_discount(subtotal, promo)
    else:
        discount = Decimal("0.00")
    try:
        return orders_repo.create_from_cart(user_id, payload, promo, discount)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


def list_orders(user_id: int) -> list[dict[str, Any]]:
    orders = orders_repo.list_user_orders(user_id)
    for order in orders:
        order["items"] = orders_repo.get_order_items(order["id"])
    return orders


def list_all_orders() -> list[dict[str, Any]]:
    orders = orders_repo.list_all_orders()
    for order in orders:
        order["items"] = orders_repo.get_order_items(order["id"])
    return orders


def update_order_status(order_id: int, status: str) -> dict[str, Any]:
    if status not in ALLOWED_STATUSES:
        raise ValidationError("Unsupported order status")
    result = orders_repo.update_status(order_id, status)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Order not found")
    return result
