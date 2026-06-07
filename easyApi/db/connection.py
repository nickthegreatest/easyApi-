"""Ядро библиотеки: подключение к БД и универсальное выполнение CRUD-запросов."""

from __future__ import annotations

import logging
from typing import Any

import pymysql
from pymysql.cursors import DictCursor

from easyApi.config import get_config
from easyApi.db.exceptions import DatabaseConnectionError, DatabaseQueryError

logger = logging.getLogger(__name__)

OperationResult = dict[str, Any] | list[dict[str, Any]]


def get_connection() -> pymysql.connections.Connection:
    """Создаёт и возвращает соединение PyMySQL из текущей конфигурации EasyApi.

    Returns:
        Активное соединение PyMySQL.

    Raises:
        DatabaseConnectionError: При ошибке подключения.
    """
    cfg = get_config()
    try:
        return pymysql.connect(
            host=cfg.DB_HOST,
            user=cfg.DB_USER,
            password=cfg.DB_PASSWORD,
            database=cfg.DB_NAME,
            port=cfg.DB_PORT,
            cursorclass=DictCursor,
            autocommit=False,
        )
    except pymysql.Error as exc:
        logger.error("Ошибка подключения к БД: %s", exc)
        raise DatabaseConnectionError(str(exc)) from exc


def execute_query(
    operation: str,
    table: str,
    params: dict[str, Any] | None = None,
    where: str | None = None,
    where_params: tuple[Any, ...] | list[Any] | None = None,
    columns: str = "*",
    join: str | None = None,
    order: str | None = None,
    group_by: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> OperationResult:
    """Универсальный метод для выполнения CRUD-запросов.

    Формирует параметризованный SQL-запрос с %s-подстановками PyMySQL.

    Args:
        operation: 'SELECT', 'INSERT', 'UPDATE' или 'DELETE'.
        table: Название таблицы.
        params: Данные для INSERT/UPDATE.
        where: Условие WHERE.
        where_params: Параметры для WHERE.
        columns: Столбцы для SELECT.
        join: JOIN-выражение для SELECT.

    Returns:
        SELECT — список словарей; INSERT — insert_id; UPDATE/DELETE — affected_rows.

    Raises:
        DatabaseQueryError: При ошибке выполнения запроса.
    """
    operation = operation.upper()
    connection: pymysql.connections.Connection | None = None
    cursor: pymysql.cursors.Cursor | None = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        if operation == "SELECT":
            sql = f"SELECT {columns} FROM `{table}`"
            if join:
                sql += f" {join}"
            query_params: list[Any] = []
            if where:
                sql += f" WHERE {where}"
                query_params = list(where_params or [])
            if group_by:
                sql += f" GROUP BY {group_by}"
            if order:
                sql += f" ORDER BY {order}"
            if limit:
                sql += f" LIMIT {limit}"
            if offset:
                sql += f" OFFSET {offset}"
            cursor.execute(sql, query_params)
            return list(cursor.fetchall())

        if operation == "INSERT":
            if not params:
                raise DatabaseQueryError("Для INSERT необходимо передать params")
            columns_list = ", ".join(f"`{key}`" for key in params)
            placeholders = ", ".join(["%s"] * len(params))
            sql = f"INSERT INTO `{table}` ({columns_list}) VALUES ({placeholders})"
            cursor.execute(sql, list(params.values()))
            connection.commit()
            return {
                "insert_id": cursor.lastrowid,
                "message": "Запись успешно добавлена",
            }

        if operation == "UPDATE":
            if not params:
                raise DatabaseQueryError("Для UPDATE необходимо передать params")
            set_clause = ", ".join(f"`{key}` = %s" for key in params)
            sql = f"UPDATE `{table}` SET {set_clause}"
            query_params = list(params.values())
            if where:
                sql += f" WHERE {where}"
                query_params.extend(where_params or [])
            cursor.execute(sql, query_params)
            connection.commit()
            return {
                "affected_rows": cursor.rowcount,
                "message": "Запись успешно обновлена",
            }

        if operation == "DELETE":
            sql = f"DELETE FROM `{table}`"
            query_params = list(where_params or [])
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, query_params)
            connection.commit()
            return {
                "affected_rows": cursor.rowcount,
                "message": "Запись успешно удалена",
            }

        raise DatabaseQueryError(f"Неподдерживаемая операция: {operation}")

    except DatabaseQueryError:
        if connection:
            connection.rollback()
        raise
    except pymysql.Error as exc:
        if connection:
            connection.rollback()
        logger.error("Ошибка SQL [%s %s]: %s", operation, table, exc)
        raise DatabaseQueryError(str(exc)) from exc
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

