"""HTTP controllers for orders."""

from __future__ import annotations

from flask import Blueprint, g, request

from vinyl_store.middleware import jwt_required, success
from vinyl_store.services import order_service
from vinyl_store.validators.store import validate_order

orders_bp = Blueprint("orders", __name__)


@orders_bp.post("/orders")
@jwt_required
def create_order():
    payload = validate_order(request.get_json(silent=True))
    return success(order_service.create_order(g.current_user["id"], payload), message="Order created", status=201)


@orders_bp.get("/orders")
@jwt_required
def list_orders():
    return success(order_service.list_orders(g.current_user["id"]))
