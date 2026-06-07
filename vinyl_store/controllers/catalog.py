"""HTTP controllers for catalog browsing."""

from __future__ import annotations

from flask import Blueprint, g, request

from easyApi import verify_token
from vinyl_store.middleware import success
from vinyl_store.services import catalog_service

catalog_bp = Blueprint("catalog", __name__)


def _optional_user_id() -> int | None:
    token = request.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        try:
            return verify_token(token.removeprefix("Bearer ").strip())["id"]
        except Exception:
            return None
    return None


@catalog_bp.get("/products")
def products():
    return success(catalog_service.list_products(request.args.to_dict()))


@catalog_bp.get("/products/<int:product_id>")
def product_detail(product_id: int):
    return success(catalog_service.get_product(product_id, _optional_user_id()))


@catalog_bp.get("/categories")
def categories():
    return success(catalog_service.list_categories())
