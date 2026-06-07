"""Модель пользователя."""

from typing import Any

from easyApi import execute_query, hash_password, check_password


class UserModel:
    """Работа с пользователями."""

    @staticmethod
    def create(username: str, email: str, password: str, first_name: str = "", last_name: str = "") -> dict[str, Any]:
        """Создать нового пользователя."""
        return execute_query(
            "INSERT",
            "users",
            {
                "username": username,
                "email": email,
                "password": hash_password(password),
                "first_name": first_name,
                "last_name": last_name,
                "role": "user",
            },
        )

    @staticmethod
    def get_by_username(username: str) -> dict[str, Any] | None:
        """Найти пользователя по username."""
        rows = execute_query("SELECT", "users", where="username = %s", where_params=(username,))
        return rows[0] if rows else None

    @staticmethod
    def get_by_email(email: str) -> dict[str, Any] | None:
        """Найти пользователя по email."""
        rows = execute_query("SELECT", "users", where="email = %s", where_params=(email,))
        return rows[0] if rows else None

    @staticmethod
    def get_by_id(user_id: int) -> dict[str, Any] | None:
        """Найти пользователя по ID."""
        rows = execute_query("SELECT", "users", where="id = %s", where_params=(user_id,))
        return rows[0] if rows else None

    @staticmethod
    def check_password(user_id: int, password: str) -> bool:
        """Проверить пароль пользователя."""
        user = UserModel.get_by_id(user_id)
        if not user:
            return False
        return check_password(password, user["password"])

    @staticmethod
    def update(user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Обновить данные пользователя."""
        data.pop("password", None)  # Не обновляем пароль здесь
        return execute_query("UPDATE", "users", data, where="id = %s", where_params=(user_id,))

    @staticmethod
    def change_password(user_id: int, new_password: str) -> dict[str, Any]:
        """Сменить пароль."""
        return execute_query(
            "UPDATE",
            "users",
            {"password": hash_password(new_password)},
            where="id = %s",
            where_params=(user_id,),
        )

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Получить список пользователей."""
        return execute_query(
            "SELECT",
            "users",
            columns="id, username, email, role, first_name, last_name, created_at",
            order="created_at DESC",
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get_by_role(role: str) -> list[dict[str, Any]]:
        """Получить пользователей по роли."""
        return execute_query(
            "SELECT",
            "users",
            columns="id, username, email, role, first_name, last_name, created_at",
            where="role = %s",
            where_params=(role,),
        )
