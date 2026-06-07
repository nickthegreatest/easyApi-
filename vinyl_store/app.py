"""VinylVault — интернет-магазин виниловых пластинок."""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта vinyl_store
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from easyApi import EasyApi

# Загружаем переменные окружения
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Конфигурация из ENV
app_config = {
    "DB_HOST": os.getenv("DB_HOST", "localhost"),
    "DB_USER": os.getenv("DB_USER", "root"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
    "DB_NAME": os.getenv("DB_NAME", "vinyl_store"),
    "DB_PORT": int(os.getenv("DB_PORT", "3306")),
    "SECRET_KEY": os.getenv("SECRET_KEY", "vinyl-vault-secret-key-change-in-production"),
    "JWT_EXPIRATION_HOURS": int(os.getenv("JWT_EXPIRATION_HOURS", "72")),
}

# Создаём приложение
kit = EasyApi(config=app_config, name="vinyl_store")

# Регистрируем контроллеры
from vinyl_store.controllers import auth_bp, catalog_bp, cart_bp, orders_bp, admin_bp

kit.register_blueprint(auth_bp, url_prefix="/api/auth")
kit.register_blueprint(catalog_bp, url_prefix="/api")
kit.register_blueprint(cart_bp, url_prefix="/api/cart")
kit.register_blueprint(orders_bp, url_prefix="/api/orders")
kit.register_blueprint(admin_bp, url_prefix="/api/admin")


# Раздача статики и SPA
@kit.flask.route("/")
def index():
    """Главная страница."""
    return send_from_directory("vinyl_store/templates", "index.html")


@kit.flask.route("/<path:path>")
def static_files(path):
    """Раздача статики."""
    if path.startswith("static/"):
        return send_from_directory(".", path)
    return send_from_directory("vinyl_store/templates", "index.html")


if __name__ == "__main__":
    print("🎵 VinylVault — интернет-магазин виниловых пластинок")
    print("📍 http://localhost:5000")
    print("🔧 API: http://localhost:5000/api/*")
    kit.run(debug=True, host="0.0.0.0", port=5000)
