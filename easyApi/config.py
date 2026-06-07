"""Конфигурация библиотеки EasyApi."""

from __future__ import annotations

import os
from typing import Any


class Config:

    """Настройки подключения к БД и JWT."""

    DB_HOST: str = "localhost"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "shop_db"
    DB_PORT: int = 3306
    SECRET_KEY: str = "change-me-in-production"
    JWT_EXPIRATION_HOURS: int = 1


_config: Config | None = None


def configure(settings: dict[str, Any] | Config | None = None) -> Config:
    """Инициализирует конфигурацию библиотеки.


    Вызывается один раз перед использованием easyApi (или передаётся в create_app).

    Args:
        settings: Словарь настроек или экземпляр Config.

    Returns:
        Активный объект конфигурации.
    """
    global _config

    if settings is None:
        _config = Config()
    elif isinstance(settings, Config):
        _config = settings
    else:
        _config = Config()
        for key, value in settings.items():
            if hasattr(_config, key):
                setattr(_config, key, value)

    return _config


def configure_from_env(prefix: str = "EASYAPI_") -> Config:
    """Инициализирует конфигурацию из переменных окружения.


    Поддерживаемые переменные:
        - {prefix}DB_HOST
        - {prefix}DB_USER
        - {prefix}DB_PASSWORD
        - {prefix}DB_NAME
        - {prefix}DB_PORT
        - {prefix}SECRET_KEY
        - {prefix}JWT_EXPIRATION_HOURS

    Args:
        prefix: Префикс переменных окружения.

    Returns:
        Активный объект конфигурации.
    """
    settings: dict[str, Any] = {}

    str_fields = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME", "SECRET_KEY"]
    int_fields = ["DB_PORT", "JWT_EXPIRATION_HOURS"]

    for field in str_fields:
        value = os.getenv(f"{prefix}{field}")
        if value is not None:
            settings[field] = value

    for field in int_fields:
        value = os.getenv(f"{prefix}{field}")
        if value is not None:
            try:
                settings[field] = int(value)
            except ValueError:
                continue

    return configure(settings)


def get_config() -> Config:
    """Возвращает текущую конфигурацию, создавая дефолтную при первом вызове.

    Returns:
        Активный объект конфигурации.
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


