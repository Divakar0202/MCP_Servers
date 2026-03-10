"""Data retrieval tools with strict read-only enforcement."""

from __future__ import annotations

from db_connection import ConnectionManager
from query_validator import validate_read_only_query
from utils import MCPToolError, ensure_identifier, rows_to_dicts, success_response


def get_table_sample_data(
    conn_mgr: ConnectionManager,
    database_name: str,
    schema_name: str,
    table_name: str,
    limit: int = 20,
) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    schema_name = ensure_identifier(schema_name, "schema_name")
    table_name = ensure_identifier(table_name, "table_name")

    if limit <= 0:
        raise MCPToolError(code="invalid_limit", message="Limit must be a positive integer.")

    safe_limit = min(limit, conn_mgr.settings.max_returned_rows)
    sql = f'SELECT * FROM "{schema_name}"."{table_name}" LIMIT :limit_value'
    result = conn_mgr.execute_query(
        sql,
        database_name=database_name,
        params={"limit_value": safe_limit},
    )
    rows = rows_to_dicts(result.columns, result.rows)
    return success_response(
        {
            "database": database_name,
            "schema": schema_name,
            "table": table_name,
            "limit": safe_limit,
            "rows": rows,
        }
    )


def get_table_row_count(conn_mgr: ConnectionManager, database_name: str, schema_name: str, table_name: str) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    schema_name = ensure_identifier(schema_name, "schema_name")
    table_name = ensure_identifier(table_name, "table_name")

    sql = f'SELECT COUNT(*) AS row_count FROM "{schema_name}"."{table_name}"'
    result = conn_mgr.execute_query(sql, database_name=database_name)
    count = int(result.rows[0][0]) if result.rows else 0
    return success_response(
        {
            "database": database_name,
            "schema": schema_name,
            "table": table_name,
            "row_count": count,
        }
    )


def execute_readonly_query(
    conn_mgr: ConnectionManager,
    database_name: str,
    query: str,
    limit: int | None = None,
) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    safe_query = validate_read_only_query(query)

    effective_limit = conn_mgr.settings.max_returned_rows
    if limit is not None:
        if limit <= 0:
            raise MCPToolError(code="invalid_limit", message="Limit must be a positive integer.")
        effective_limit = min(limit, conn_mgr.settings.max_returned_rows)

    result = conn_mgr.execute_query(
        safe_query,
        database_name=database_name,
        fetch_limit=effective_limit,
    )
    rows = rows_to_dicts(result.columns, result.rows)
    return success_response(
        {
            "database": database_name,
            "max_rows": effective_limit,
            "columns": result.columns,
            "row_count": len(rows),
            "rows": rows,
        }
    )
