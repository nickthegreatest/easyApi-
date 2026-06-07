"""HTTP controllers for product reviews."""

from __future__ import annotations

from flask import Blueprint, g, request

from vinyl_store.middleware import jwt_required, success
from vinyl_store.services import review_service
from vinyl_store.validators.store import validate_review

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.post("/reviews")
@jwt_required
def add_review():
    payload = validate_review(request.get_json(silent=True))
    return success(review_service.add_review(g.current_user["id"], payload), message="Review submitted", status=201)


@reviews_bp.get("/reviews/<int:product_id>")
def list_reviews(product_id: int):
    return success(review_service.list_reviews(product_id))
