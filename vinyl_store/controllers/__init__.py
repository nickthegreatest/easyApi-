"""Controller blueprints."""

from vinyl_store.controllers.admin import admin_bp
from vinyl_store.controllers.auth import auth_bp
from vinyl_store.controllers.cart import cart_bp
from vinyl_store.controllers.catalog import catalog_bp
from vinyl_store.controllers.orders import orders_bp
from vinyl_store.controllers.reviews import reviews_bp
from vinyl_store.controllers.wishlist import wishlist_bp

__all__ = ["admin_bp", "auth_bp", "cart_bp", "catalog_bp", "orders_bp", "reviews_bp", "wishlist_bp"]
