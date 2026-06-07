"""HTTP controllers for the admin panel and admin REST API."""

from __future__ import annotations

from flask import Blueprint, request

from vinyl_store.middleware import admin_required, success
from vinyl_store.services import admin_service, catalog_service, order_service, review_service
from vinyl_store.validators.common import json_object, required_string
from vinyl_store.validators.store import validate_category, validate_product

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/admin/stats")
@admin_required
def stats():
    return success(admin_service.dashboard())


@admin_bp.get("/admin/users")
@admin_required
def users():
    return success(admin_service.users())


@admin_bp.get("/admin/orders")
@admin_required
def orders():
    return success(order_service.list_all_orders())


@admin_bp.put("/admin/orders/<int:order_id>")
@admin_required
def order_status(order_id: int):
    payload = json_object(request.get_json(silent=True))
    status = required_string(payload, "status", max_len=20)
    return success(order_service.update_order_status(order_id, status), message="Order status updated")


@admin_bp.post("/admin/products")
@admin_required
def create_product():
    payload = validate_product(request.get_json(silent=True))
    return success(catalog_service.create_product(payload), message="Product created", status=201)


@admin_bp.put("/admin/products/<int:product_id>")
@admin_required
def update_product(product_id: int):
    payload = validate_product(request.get_json(silent=True), partial=True)
    return success(catalog_service.update_product(product_id, payload), message="Product updated")


@admin_bp.delete("/admin/products/<int:product_id>")
@admin_required
def delete_product(product_id: int):
    return success(catalog_service.delete_product(product_id), message="Product deleted")


@admin_bp.post("/admin/categories")
@admin_required
def create_category():
    payload = validate_category(request.get_json(silent=True))
    return success(catalog_service.create_category(payload), message="Category created", status=201)


@admin_bp.put("/admin/categories/<int:category_id>")
@admin_required
def update_category(category_id: int):
    payload = validate_category(request.get_json(silent=True), partial=True)
    return success(catalog_service.update_category(category_id, payload), message="Category updated")


@admin_bp.delete("/admin/categories/<int:category_id>")
@admin_required
def delete_category(category_id: int):
    return success(catalog_service.delete_category(category_id), message="Category deleted")


@admin_bp.get("/admin/reviews")
@admin_required
def all_reviews():
    return success(review_service.list_all_reviews())


@admin_bp.put("/admin/reviews/<int:review_id>")
@admin_required
def moderate_review(review_id: int):
    payload = json_object(request.get_json(silent=True))
    return success(review_service.moderate_review(review_id, bool(payload.get("is_approved"))), message="Review moderated")


@admin_bp.delete("/admin/reviews/<int:review_id>")
@admin_required
def delete_review(review_id: int):
    return success(review_service.delete_review(review_id), message="Review deleted")
