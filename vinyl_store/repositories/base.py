"""Low-level SQL helpers powered by the EasyApi PyMySQL wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from easyApi import execute_query, get_connection


def _table_sql(table: str) -> str:
    """Quote simple table names while allowing constant table aliases used by repositories."""

    return f"`{table}`" if table.replace("_", "").isalnum() else table


def select(
    table: str,
    *,
    columns: str = "*",
    where: str | None = None,
    where_params: Iterable[Any] | None = None,
    join: str | None = None,
    order: str | None = None,
    group_by: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """Run a parameterized SELECT through EasyApi's PyMySQL connection helper."""

    sql = f"SELECT {columns} FROM {_table_sql(table)}"
    params = list(where_params or [])
    if join:
        sql += f" {join}"
    if where:
        sql += f" WHERE {where}"
    if group_by:
        sql += f" GROUP BY {group_by}"
    if order:
        sql += f" ORDER BY {order}"
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        sql += " OFFSET %s"
        params.append(offset)
    return raw_query(sql, params)

def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    """Insert a row through EasyApi's CRUD helper."""

    return execute_query("INSERT", table, params=data)


def update(table: str, data: dict[str, Any], where: str, params: Iterable[Any]) -> dict[str, Any]:
    """Update rows through EasyApi's CRUD helper."""

    return execute_query("UPDATE", table, params=data, where=where, where_params=list(params))


def delete(table: str, where: str, params: Iterable[Any]) -> dict[str, Any]:
    """Delete rows through EasyApi's CRUD helper."""

    return execute_query("DELETE", table, where=where, where_params=list(params))


def raw_query(sql: str, params: Iterable[Any] | None = None, *, fetch_one: bool = False) -> Any:
    """Execute parameterized SQL for reports and transactional reads without ORM."""

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, list(params or []))
            result = cursor.fetchone() if fetch_one else list(cursor.fetchall())
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
