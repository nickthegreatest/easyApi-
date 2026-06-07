"""Business logic for the vinyl catalog."""

from __future__ import annotations

from typing import Any

from vinyl_store.middleware.errors import ValidationError
from vinyl_store.repositories import catalog as catalog_repo


def list_products(args: dict[str, Any]) -> list[dict[str, Any]]:
    filters = {
        "q": args.get("q") or args.get("search"),
        "genre": args.get("genre"),
        "sort": args.get("sort"),
        "limit": min(int(args.get("limit", 48)), 100),
        "offset": max(int(args.get("offset", 0)), 0),
    }
    for key in ["category_id", "min_price", "max_price"]:
        if args.get(key):
            filters[key] = args.get(key)
    return catalog_repo.list_products(filters)


def get_product(product_id: int, user_id: int | None = None) -> dict[str, Any]:
    product = catalog_repo.get_product(product_id)
    if not product:
        raise ValidationError("Product not found")
    catalog_repo.record_view(user_id, product_id)
    return product


def list_categories() -> list[dict[str, Any]]:
    return catalog_repo.list_categories()


def create_product(data: dict[str, Any]) -> dict[str, Any]:
    product_id = catalog_repo.create_product(data)
    return catalog_repo.get_product(product_id)


def update_product(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        raise ValidationError("No product fields to update")
    result = catalog_repo.update_product(product_id, data)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Product not found")
    return catalog_repo.get_product(product_id)


def delete_product(product_id: int) -> dict[str, Any]:
    result = catalog_repo.delete_product(product_id)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Product not found")
    return result


def create_category(data: dict[str, Any]) -> dict[str, Any]:
    category_id = catalog_repo.create_category(data)
    return {"id": category_id, **data}


def update_category(category_id: int, data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        raise ValidationError("No category fields to update")
    result = catalog_repo.update_category(category_id, data)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Category not found")
    return result


def delete_category(category_id: int) -> dict[str, Any]:
    result = catalog_repo.delete_category(category_id)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Category not found")
    return result
