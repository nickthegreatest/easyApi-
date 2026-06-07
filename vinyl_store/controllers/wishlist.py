"""HTTP controllers for wishlist endpoints."""

from __future__ import annotations

from flask import Blueprint, g, request

from vinyl_store.middleware import jwt_required, success
from vinyl_store.services import wishlist_service
from vinyl_store.validators.store import validate_wishlist

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.post("/wishlist")
@jwt_required
def add_wishlist():
    payload = validate_wishlist(request.get_json(silent=True))
    return success(wishlist_service.add_to_wishlist(g.current_user["id"], payload["product_id"]), message="Product added to wishlist", status=201)


@wishlist_bp.get("/wishlist")
@jwt_required
def list_wishlist():
    return success(wishlist_service.list_wishlist(g.current_user["id"]))


@wishlist_bp.delete("/wishlist/<int:product_id>")
@jwt_required
def remove_wishlist(product_id: int):
    return success(wishlist_service.remove_from_wishlist(g.current_user["id"], product_id), message="Product removed from wishlist")
