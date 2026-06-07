"""Фабрика Flask-приложения и high-level API EasyApi."""

from __future__ import annotations

import logging
from typing import Any, Callable

from flask import Blueprint, Flask, jsonify, request


from easyApi.config import Config, configure, configure_from_env, get_config
from easyApi.db.connection import execute_query
from easyApi.db.exceptions import DatabaseError, TokenExpiredError, TokenInvalidError
from easyApi.services.jwt_service import generate_token, verify_token
from easyApi.services.security import admin_required, check_password, hash_password, token_required

logger = logging.getLogger(__name__)


class SimpleModel:
    """Минимальная модель таблицы для CRUD-операций."""

    def __init__(self, table: str) -> None:
        self.table = table

    def all(
        self,
        where: str | None = None,
        where_params: tuple[Any, ...] | list[Any] | None = None,
        columns: str = "*",
        join: str | None = None,
    ) -> list[dict[str, Any]]:
        """Возвращает список записей."""
        return execute_query(
            "SELECT",
            self.table,
            where=where,
            where_params=where_params,
            columns=columns,
            join=join,
        )

    def get(self, entity_id: int, id_column: str = "id") -> dict[str, Any] | None:
        """Возвращает запись по идентификатору."""
        rows = execute_query(
            "SELECT",
            self.table,
            where=f"`{id_column}` = %s",
            where_params=(entity_id,),
        )
        return rows[0] if rows else None

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Создаёт запись."""
        return execute_query("INSERT", self.table, params=data)

    def update(
        self,
        entity_id: int,
        data: dict[str, Any],
        id_column: str = "id",
    ) -> dict[str, Any]:
        """Обновляет запись по идентификатору."""
        return execute_query(
            "UPDATE",
            self.table,
            params=data,
            where=f"`{id_column}` = %s",
            where_params=(entity_id,),
        )

    def delete(self, entity_id: int, id_column: str = "id") -> dict[str, Any]:
        """Удаляет запись по идентификатору."""
        return execute_query(
            "DELETE",
            self.table,
            where=f"`{id_column}` = %s",
            where_params=(entity_id,),
        )


class EasyApi:

    """Единая точка входа в библиотеку для минимального количества кода.

    Пример:
        kit = EasyApi()

        @kit.route("/health")
        def health() -> dict[str, str]:
            return {"status": "ok"}

        if __name__ == "__main__":
            kit.run(debug=True)
    """

    def __init__(
        self,
        config: dict[str, Any] | Config | None = None,
        blueprints: list[Blueprint] | None = None,
        name: str | None = None,
        use_env: bool = True,
        env_prefix: str = "EASYAPI_",
    ) -> None:
        if config is not None:
            configure(config)
        elif use_env:
            configure_from_env(prefix=env_prefix)

        self.app = create_app(blueprints=blueprints, config=None, name=name)

    @property
    def flask(self) -> Flask:
        """Возвращает внутренний Flask app, если нужен низкоуровневый доступ."""
        return self.app

    def route(self, rule: str, **options: Any) -> Callable[..., Any]:
        """Прокси к app.route для объявления маршрутов без прямого импорта Flask."""
        return self.app.route(rule, **options)

    def register_blueprint(self, blueprint: Blueprint, **options: Any) -> None:
        """Регистрирует Blueprint в приложении."""
        self.app.register_blueprint(blueprint, **options)

    def model(self, table: str) -> SimpleModel:
        """Возвращает простую CRUD-модель по имени таблицы."""
        return SimpleModel(table)

    def register_crud(
        self,
        table: str,
        url_prefix: str | None = None,
        id_column: str = "id",
        methods: tuple[str, ...] = ("GET", "POST", "PUT", "DELETE"),
    ) -> Blueprint:
        """Автоматически регистрирует CRUD-роуты для таблицы.

        Роуты:
            GET    {prefix}/         -> список
            GET    {prefix}/<id>     -> одна запись
            POST   {prefix}/         -> создать
            PUT    {prefix}/<id>     -> обновить
            DELETE {prefix}/<id>     -> удалить
        """
        model = self.model(table)
        prefix = (url_prefix or f"/{table}").rstrip("/")
        if not prefix.startswith("/"):
            prefix = f"/{prefix}"

        allowed = set(method.upper() for method in methods)
        blueprint_name = f"rk_{table}_{prefix.strip('/').replace('/', '_') or 'root'}"
        bp = Blueprint(blueprint_name, __name__)

        if "GET" in allowed:

            @bp.get("/")
            def list_entities() -> tuple[Any, int] | Any:
                return jsonify(model.all()), 200

            @bp.get("/<int:entity_id>")
            def get_entity(entity_id: int) -> tuple[Any, int] | Any:
                entity = model.get(entity_id, id_column=id_column)
                if entity is None:
                    return jsonify({"error": "Запись не найдена", "code": 404}), 404
                return jsonify(entity), 200

        if "POST" in allowed:

            @bp.post("/")
            def create_entity() -> tuple[Any, int] | Any:
                payload = request.get_json(silent=True)
                if not isinstance(payload, dict) or not payload:
                    return jsonify({"error": "Тело запроса должно быть непустым JSON-объектом", "code": 400}), 400
                result = model.create(payload)
                return jsonify(result), 201

        if "PUT" in allowed:

            @bp.put("/<int:entity_id>")
            def update_entity(entity_id: int) -> tuple[Any, int] | Any:
                payload = request.get_json(silent=True)
                if not isinstance(payload, dict) or not payload:
                    return jsonify({"error": "Тело запроса должно быть непустым JSON-объектом", "code": 400}), 400
                result = model.update(entity_id, payload, id_column=id_column)
                if result.get("affected_rows", 0) == 0:
                    return jsonify({"error": "Запись не найдена", "code": 404}), 404
                return jsonify(result), 200

        if "DELETE" in allowed:

            @bp.delete("/<int:entity_id>")
            def delete_entity(entity_id: int) -> tuple[Any, int] | Any:
                result = model.delete(entity_id, id_column=id_column)
                if result.get("affected_rows", 0) == 0:
                    return jsonify({"error": "Запись не найдена", "code": 404}), 404
                return jsonify(result), 200

        self.app.register_blueprint(bp, url_prefix=prefix)
        return bp

    def run(self, *args: Any, **kwargs: Any) -> None:

        """Запускает встроенный Flask-сервер."""
        self.app.run(*args, **kwargs)

    def query(
        self,
        operation: str,
        table: str,
        params: dict[str, Any] | None = None,
        where: str | None = None,
        where_params: tuple[Any, ...] | list[Any] | None = None,
        columns: str = "*",
        join: str | None = None,
    ) -> Any:
        """Универсальный SQL CRUD-запрос."""
        return execute_query(operation, table, params, where, where_params, columns, join)

    def select(
        self,
        table: str,
        where: str | None = None,
        where_params: tuple[Any, ...] | list[Any] | None = None,
        columns: str = "*",
        join: str | None = None,
    ) -> list[dict[str, Any]]:
        """Короткий хелпер SELECT."""
        return execute_query(
            "SELECT",
            table,
            where=where,
            where_params=where_params,
            columns=columns,
            join=join,
        )

    def insert(self, table: str, params: dict[str, Any]) -> dict[str, Any]:
        """Короткий хелпер INSERT."""
        return execute_query("INSERT", table, params=params)

    def update(
        self,
        table: str,
        params: dict[str, Any],
        where: str | None = None,
        where_params: tuple[Any, ...] | list[Any] | None = None,
    ) -> dict[str, Any]:
        """Короткий хелпер UPDATE."""
        return execute_query("UPDATE", table, params=params, where=where, where_params=where_params)

    def delete(
        self,
        table: str,
        where: str | None = None,
        where_params: tuple[Any, ...] | list[Any] | None = None,
    ) -> dict[str, Any]:
        """Короткий хелпер DELETE."""
        return execute_query("DELETE", table, where=where, where_params=where_params)

    def generate_token(self, user_data: dict[str, Any]) -> str:
        """Прокси к JWT-сервису."""
        return generate_token(user_data)

    def verify_token(self, token: str) -> dict[str, Any]:
        """Прокси к JWT-сервису."""
        return verify_token(token)

    def hash_password(self, password: str) -> str:
        """Прокси к сервису безопасности."""
        return hash_password(password)

    def check_password(self, password: str, hashed: str) -> bool:
        """Прокси к сервису безопасности."""
        return check_password(password, hashed)

    @property
    def token_required(self) -> Callable[..., Any]:
        """Декоратор проверки JWT для маршрутов."""
        return token_required

    @property
    def admin_required(self) -> Callable[..., Any]:
        """Декоратор проверки роли admin для маршрутов."""
        return admin_required


# Совместимость со старым именем класса
RestKit = EasyApi



def create_app(

    blueprints: list[Blueprint] | None = None,
    config: dict[str, Any] | Config | None = None,
    name: str | None = None,
) -> Flask:
    """Создаёт и настраивает Flask-приложение с обработчиками ошибок EasyApi."""
    if config is not None:
        configure(config)

    cfg = get_config()
    app = Flask(name or __name__)
    app.config["SECRET_KEY"] = cfg.SECRET_KEY

    if blueprints:
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

    _register_error_handlers(app)
    return app


def _register_error_handlers(app: Flask) -> None:
    """Регистрирует централизованный обработчик исключений EasyApi."""

    @app.errorhandler(Exception)
    def handle_exception(error: Exception) -> tuple[Any, int]:
        if isinstance(error, TokenExpiredError):
            return jsonify({"error": error.message, "code": 401}), 401
        if isinstance(error, TokenInvalidError):
            return jsonify({"error": error.message, "code": 403}), 403
        if isinstance(error, DatabaseError):
            return jsonify({"error": error.message, "code": error.code}), error.code

        logger.exception("Необработанная ошибка: %s", error)
        return jsonify({"error": str(error), "code": 500}), 500


