"""Route registration for Vintage Vinyl Store."""

from __future__ import annotations

from flask import Flask

from vinyl_store.controllers import admin_bp, auth_bp, cart_bp, catalog_bp, orders_bp, reviews_bp, wishlist_bp

BLUEPRINTS = [auth_bp, catalog_bp, cart_bp, wishlist_bp, orders_bp, reviews_bp, admin_bp]


def register_routes(app: Flask) -> None:
    """Register REST API blueprints declared through decorators."""

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
