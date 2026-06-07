"""HTTP controllers for cart endpoints."""

from __future__ import annotations

from flask import Blueprint, g, request

from vinyl_store.middleware import jwt_required, success
from vinyl_store.services import cart_service
from vinyl_store.validators.store import validate_cart_item, validate_quantity

cart_bp = Blueprint("cart", __name__)


@cart_bp.post("/cart")
@jwt_required
def add_to_cart():
    payload = validate_cart_item(request.get_json(silent=True))
    cart = cart_service.add_to_cart(g.current_user["id"], payload["product_id"], payload["quantity"])
    return success(cart, message="Product added to cart", status=201)


@cart_bp.get("/cart")
@jwt_required
def get_cart():
    return success(cart_service.get_cart(g.current_user["id"]))


@cart_bp.put("/cart/<int:product_id>")
@jwt_required
def update_cart(product_id: int):
    quantity = validate_quantity(request.get_json(silent=True))
    return success(cart_service.update_quantity(g.current_user["id"], product_id, quantity), message="Cart updated")


@cart_bp.delete("/cart/<int:item_id>")
@jwt_required
def delete_cart_item(item_id: int):
    return success(cart_service.remove_item(g.current_user["id"], item_id), message="Cart item removed")
