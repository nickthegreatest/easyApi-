"""EasyApi — библиотека для ускорения разработки RESTful API на Flask и PyMySQL."""

from easyApi.app import EasyApi, RestKit, SimpleModel, create_app


from easyApi.config import Config, configure, configure_from_env, get_config

from easyApi.db.connection import execute_query, get_connection
from easyApi.db.exceptions import (
    DatabaseConnectionError,
    DatabaseError,
    DatabaseQueryError,
    TokenExpiredError,
    TokenInvalidError,
)
from easyApi.services.jwt_service import generate_token, verify_token
from easyApi.services.security import admin_required, check_password, hash_password, manager_required, token_required

__version__ = "0.1.0"

__all__ = [
    "Config",
    "EasyApi",
    "RestKit",
    "SimpleModel",
    "admin_required",
    "manager_required",
    "check_password",
    "configure",
    "configure_from_env",
    "create_app",

    "execute_query",
    "generate_token",
    "get_config",
    "get_connection",
    "hash_password",
    "token_required",
    "verify_token",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "TokenExpiredError",
    "TokenInvalidError",
]

