"""Schema discovery tools for PostgreSQL metadata."""

from __future__ import annotations

from db_connection import ConnectionManager
from utils import ensure_identifier, rows_to_dicts, success_response


def list_databases(conn_mgr: ConnectionManager) -> dict:
    sql = """
    SELECT datname
    FROM pg_database
    WHERE datistemplate = false
    ORDER BY datname;
    """
    result = conn_mgr.execute_query(sql, database_name=conn_mgr.settings.default_database)
    databases = [row[0] for row in result.rows]
    return success_response({"databases": databases})


def list_schemas(conn_mgr: ConnectionManager, database_name: str) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    sql = """
    SELECT schema_name
    FROM information_schema.schemata
    ORDER BY schema_name;
    """
    result = conn_mgr.execute_query(sql, database_name=database_name)
    schemas = [row[0] for row in result.rows]
    return success_response({"database": database_name, "schemas": schemas})


def list_tables(conn_mgr: ConnectionManager, database_name: str, schema_name: str) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    schema_name = ensure_identifier(schema_name, "schema_name")
    sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = :schema_name
      AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """
    result = conn_mgr.execute_query(sql, database_name=database_name, params={"schema_name": schema_name})
    tables = [row[0] for row in result.rows]
    return success_response({"database": database_name, "schema": schema_name, "tables": tables})


def describe_table(conn_mgr: ConnectionManager, database_name: str, schema_name: str, table_name: str) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    schema_name = ensure_identifier(schema_name, "schema_name")
    table_name = ensure_identifier(table_name, "table_name")

    sql = """
    SELECT
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_schema = :schema_name
      AND table_name = :table_name
    ORDER BY ordinal_position;
    """
    result = conn_mgr.execute_query(
        sql,
        database_name=database_name,
        params={"schema_name": schema_name, "table_name": table_name},
    )
    columns = rows_to_dicts(result.columns, result.rows)
    return success_response(
        {
            "database": database_name,
            "schema": schema_name,
            "table": table_name,
            "columns": columns,
        }
    )


def get_foreign_keys(conn_mgr: ConnectionManager, database_name: str, schema_name: str, table_name: str) -> dict:
    database_name = ensure_identifier(database_name, "database_name")
    schema_name = ensure_identifier(schema_name, "schema_name")
    table_name = ensure_identifier(table_name, "table_name")

    sql = """
    SELECT
        tc.constraint_name,
        kcu.column_name,
        ccu.table_schema AS referenced_schema,
        ccu.table_name AS referenced_table,
        ccu.column_name AS referenced_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
      ON ccu.constraint_name = tc.constraint_name
     AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
      AND tc.table_schema = :schema_name
      AND tc.table_name = :table_name
    ORDER BY tc.constraint_name, kcu.ordinal_position;
    """
    result = conn_mgr.execute_query(
        sql,
        database_name=database_name,
        params={"schema_name": schema_name, "table_name": table_name},
    )
    foreign_keys = rows_to_dicts(result.columns, result.rows)
    return success_response(
        {
            "database": database_name,
            "schema": schema_name,
            "table": table_name,
            "foreign_keys": foreign_keys,
        }
    )
