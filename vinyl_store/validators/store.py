"""Store operation validators."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from vinyl_store.middleware.errors import ValidationError
from vinyl_store.validators.common import (
    decimal_value,
    integer,
    json_object,
    optional_string,
    required_string,
    validate_slug,
)


def validate_cart_item(payload: Any) -> dict[str, int]:
    data = json_object(payload)
    return {"product_id": integer(data, "product_id", minimum=1), "quantity": integer(data, "quantity", default=1, minimum=1)}


def validate_quantity(payload: Any) -> int:
    data = json_object(payload)
    return integer(data, "quantity", minimum=1)


def validate_wishlist(payload: Any) -> dict[str, int]:
    data = json_object(payload)
    return {"product_id": integer(data, "product_id", minimum=1)}


def validate_review(payload: Any) -> dict[str, Any]:
    data = json_object(payload)
    rating = integer(data, "rating", minimum=1)
    if rating > 5:
        raise ValidationError("Field 'rating' must be <= 5")
    return {
        "product_id": integer(data, "product_id", minimum=1),
        "rating": rating,
        "title": optional_string(data, "title", max_len=200),
        "content": required_string(data, "content", min_len=3, max_len=4000),
    }


def validate_order(payload: Any) -> dict[str, Any]:
    data = json_object(payload)
    return {
        "shipping_address": required_string(data, "shipping_address", min_len=5, max_len=1000),
        "shipping_city": optional_string(data, "shipping_city", max_len=100),
        "shipping_postal_code": optional_string(data, "shipping_postal_code", max_len=20),
        "shipping_country": optional_string(data, "shipping_country", max_len=50) or "Russia",
        "customer_phone": optional_string(data, "customer_phone", max_len=20),
        "customer_email": optional_string(data, "customer_email", max_len=100),
        "payment_method": data.get("payment_method", "card"),
        "promo_code": optional_string(data, "promo_code", max_len=50),
        "notes": optional_string(data, "notes", max_len=1000),
    }


def validate_product(payload: Any, *, partial: bool = False) -> dict[str, Any]:
    data = json_object(payload)
    result: dict[str, Any] = {}
    required = [] if partial else ["title", "artist", "slug", "price"]
    for field in required:
        if field not in data:
            raise ValidationError(f"Field '{field}' is required")
    if "title" in data:
        result["title"] = required_string(data, "title", max_len=200)
    if "artist" in data:
        result["artist"] = required_string(data, "artist", max_len=100)
    if "slug" in data:
        result["slug"] = validate_slug(required_string(data, "slug", max_len=200))
    if "description" in data:
        result["description"] = optional_string(data, "description", max_len=4000)
    if "price" in data:
        result["price"] = decimal_value(data, "price", minimum=Decimal("0.01"))
    if "old_price" in data:
        result["old_price"] = decimal_value(data, "old_price", minimum=Decimal("0.01")) if data.get("old_price") else None
    for field in ["stock_quantity", "category_id", "label_id", "release_year", "weight_grams"]:
        if field in data:
            result[field] = integer(data, field, minimum=0 if field != "release_year" else 1900)
    for field in ["country", "format", "speed_rpm", "color", "image_url"]:
        if field in data:
            result[field] = optional_string(data, field, max_len=255)
    for field in ["is_limited", "is_new"]:
        if field in data:
            result[field] = bool(data[field])
    return result


def validate_category(payload: Any, *, partial: bool = False) -> dict[str, Any]:
    data = json_object(payload)
    if not partial and ("name" not in data or "slug" not in data):
        raise ValidationError("Fields 'name' and 'slug' are required")
    result: dict[str, Any] = {}
    if "name" in data:
        result["name"] = required_string(data, "name", max_len=100)
    if "slug" in data:
        result["slug"] = validate_slug(required_string(data, "slug", max_len=100))
    if "description" in data:
        result["description"] = optional_string(data, "description", max_len=1000)
    if "image_url" in data:
        result["image_url"] = optional_string(data, "image_url", max_len=255)
    return result
