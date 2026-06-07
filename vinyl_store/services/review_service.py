"""Business logic for product reviews."""

from __future__ import annotations

from typing import Any

from vinyl_store.middleware.errors import ValidationError
from vinyl_store.repositories import catalog as catalog_repo
from vinyl_store.repositories import reviews as reviews_repo


def add_review(user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    if not catalog_repo.get_product(payload["product_id"]):
        raise ValidationError("Product not found")
    review_id = reviews_repo.add_review({"user_id": user_id, "is_approved": False, **payload})
    return {"id": review_id, "moderation": "Review is awaiting admin approval"}


def list_reviews(product_id: int):
    return reviews_repo.list_for_product(product_id)


def list_all_reviews():
    return reviews_repo.list_all()


def moderate_review(review_id: int, approved: bool):
    result = reviews_repo.approve(review_id, approved)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Review not found")
    return result


def delete_review(review_id: int):
    result = reviews_repo.delete_review(review_id)
    if result.get("affected_rows", 0) == 0:
        raise ValidationError("Review not found")
    return result
