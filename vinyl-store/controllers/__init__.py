"""Пакет контроллеров VinylVault."""

from vinyl_store.controllers.auth import auth_bp
from vinyl_store.controllers.catalog import catalog_bp
from vinyl_store.controllers.cart import cart_bp
from vinyl_store.controllers.orders import orders_bp
from vinyl_store.controllers.admin import admin_bp

__all__ = [
    "auth_bp",
    "catalog_bp",
    "cart_bp",
    "orders_bp",
    "admin_bp",
]
