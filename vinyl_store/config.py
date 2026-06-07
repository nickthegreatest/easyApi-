"""Configuration for the Vintage Vinyl Store diploma project."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Application settings mapped to EasyApi configuration keys."""

    db_host: str = os.getenv("DB_HOST", os.getenv("EASYAPI_DB_HOST", "localhost"))
    db_user: str = os.getenv("DB_USER", os.getenv("EASYAPI_DB_USER", "root"))
    db_password: str = os.getenv("DB_PASSWORD", os.getenv("EASYAPI_DB_PASSWORD", ""))
    db_name: str = os.getenv("DB_NAME", os.getenv("EASYAPI_DB_NAME", "vinyl_store"))
    db_port: int = int(os.getenv("DB_PORT", os.getenv("EASYAPI_DB_PORT", "3306")))
    secret_key: str = os.getenv("SECRET_KEY", os.getenv("EASYAPI_SECRET_KEY", "change-vintage-vinyl-secret"))
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", os.getenv("EASYAPI_JWT_EXPIRATION_HOURS", "72")))
    upload_folder: str = os.getenv("UPLOAD_FOLDER", "uploads")


def easyapi_settings(config: AppConfig | None = None) -> dict[str, object]:
    """Return settings in the format expected by the custom EasyApi library."""

    cfg = config or AppConfig()
    return {
        "DB_HOST": cfg.db_host,
        "DB_USER": cfg.db_user,
        "DB_PASSWORD": cfg.db_password,
        "DB_NAME": cfg.db_name,
        "DB_PORT": cfg.db_port,
        "SECRET_KEY": cfg.secret_key,
        "JWT_EXPIRATION_HOURS": cfg.jwt_expiration_hours,
    }
