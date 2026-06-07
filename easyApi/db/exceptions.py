"""Кастомные исключения EasyApi для БД и JWT."""

from __future__ import annotations


class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных."""

    def __init__(self, message: str, code: int = 500) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class DatabaseConnectionError(DatabaseError):
    """Ошибка подключения к базе данных."""

    def __init__(self, message: str = "Не удалось подключиться к базе данных") -> None:
        super().__init__(message, code=500)


class DatabaseQueryError(DatabaseError):
    """Ошибка выполнения SQL-запроса."""

    def __init__(
        self,
        message: str = "Ошибка выполнения запроса к базе данных",
        code: int = 500,
    ) -> None:
        super().__init__(message, code=code)


class TokenExpiredError(Exception):
    """стёк срок действия JWT-токена."""

    def __init__(self, message: str = "Срок действия токена истёк") -> None:
        self.message = message
        super().__init__(message)


class TokenInvalidError(Exception):
    """Невалидный JWT-токен."""

    def __init__(self, message: str = "Недействительный токен") -> None:
        self.message = message
        super().__init__(message)

