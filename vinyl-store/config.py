"""Конфигурация приложения VinylVault."""

import os

# Настройки базы данных
DB_HOST = os.getenv("VINYL_DB_HOST", "localhost")
DB_USER = os.getenv("VINYL_DB_USER", "root")
DB_PASSWORD = os.getenv("VINYL_DB_PASSWORD", "")
DB_NAME = os.getenv("VINYL_DB_NAME", "vinyl_store")
DB_PORT = int(os.getenv("VINYL_DB_PORT", "3306"))

# Секретный ключ для сессий и JWT
SECRET_KEY = os.getenv("VINYL_SECRET_KEY", "vinyl-vault-secret-key-change-in-production")

# JWT настройки
JWT_EXPIRATION_HOURS = int(os.getenv("VINYL_JWT_EXPIRATION_HOURS", "72"))

# Настройки приложения
APP_NAME = "VinylVault"
APP_VERSION = "1.0.0"

# Пагинация
PRODUCTS_PER_PAGE = 12
ORDERS_PER_PAGE = 20

# Загрузка файлов
UPLOAD_FOLDER = "static/images/products"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Доставка
SHIPPING_COST_FREE_THRESHOLD = 5000  # Бесплатная доставка от 5000₽
SHIPPING_COST_STANDARD = 300  # Стандартная доставка

# Фейковая оплата
PAYMENT_SUCCESS_RATE = 0.95  # 95% успешных платежей
