"""Демо-приложение интернет-магазина — использует библиотеку easyApi."""

from __future__ import annotations

import logging

from easyApi import create_app

from demo.config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    JWT_EXPIRATION_HOURS,
    SECRET_KEY,
)
from demo.controllers.account import account_bp
from demo.controllers.auth import auth_bp
from demo.controllers.cart import cart_bp
from demo.controllers.catalog import catalog_bp
from demo.controllers.orders import orders_bp
from demo.controllers.review import review_bp

logging.basicConfig(level=logging.INFO)

app = create_app(
    blueprints=[auth_bp, catalog_bp, cart_bp, orders_bp, review_bp, account_bp],
    config={
        "DB_HOST": DB_HOST,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_NAME": DB_NAME,
        "DB_PORT": DB_PORT,
        "SECRET_KEY": SECRET_KEY,
        "JWT_EXPIRATION_HOURS": JWT_EXPIRATION_HOURS,
    },
    name="shop_demo",
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

