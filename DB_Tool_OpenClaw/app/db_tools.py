"""
Read-only database tool functions.

Each function accepts a SQLAlchemy ``Session`` and returns plain Python
objects (dicts / lists) that the API layer converts to Pydantic models.

All write-path SQL is blocked either by ``security.validate_query`` (for
ad-hoc queries) or by ``security.sanitize_identifier`` (for parameterised
introspection helpers).
"""

import logging
import time
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.security import validate_query, sanitize_identifier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. list_tables
# ---------------------------------------------------------------------------

def list_tables(db: Session) -> list[str]:
    """Return the names of every user table in the database."""
    start = time.perf_counter()
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    elapsed = time.perf_counter() - start
    logger.info("list_tables returned %d tables in %.3fs", len(tables), elapsed)
    return tables


# ---------------------------------------------------------------------------
# 2. describe_table
# ---------------------------------------------------------------------------

def describe_table(db: Session, table_name: str) -> list[dict[str, Any]]:
    """
    Return column metadata for *table_name*.

    Each dict contains: name, type, nullable, default, primary_key.
    """
    table_name = sanitize_identifier(table_name)
    _assert_table_exists(db, table_name)
    start = time.perf_counter()

    inspector = inspect(db.bind)
    columns = inspector.get_columns(table_name)
    pk_constraint = inspector.get_pk_constraint(table_name)
    pk_cols = set(pk_constraint.get("constrained_columns", []))

    result = [
        {
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "default": str(col["default"]) if col.get("default") is not None else None,
            "primary_key": col["name"] in pk_cols,
        }
        for col in columns
    ]

    elapsed = time.perf_counter() - start
    logger.info(
        "describe_table(%s) returned %d columns in %.3fs",
        table_name, len(result), elapsed,
    )
    return result


# ---------------------------------------------------------------------------
# 3. get_table_sample
# ---------------------------------------------------------------------------

def get_table_sample(
    db: Session,
    table_name: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Return up to *limit* sample rows from *table_name*."""
    table_name = sanitize_identifier(table_name)
    _assert_table_exists(db, table_name)
    limit = min(max(1, limit), 1000)  # clamp between 1 and 1000
    start = time.perf_counter()

    result = db.execute(
        text(f"SELECT * FROM {table_name} LIMIT :lim"),  # noqa: S608
        {"lim": limit},
    )
    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchall()]

    elapsed = time.perf_counter() - start
    logger.info(
        "get_table_sample(%s, limit=%d) returned %d rows in %.3fs",
        table_name, limit, len(rows), elapsed,
    )
    return {"columns": columns, "rows": rows}


# ---------------------------------------------------------------------------
# 4. get_table_count
# ---------------------------------------------------------------------------

def get_table_count(db: Session, table_name: str) -> int:
    """Return the total row count of *table_name*."""
    table_name = sanitize_identifier(table_name)
    _assert_table_exists(db, table_name)
    start = time.perf_counter()

    result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))  # noqa: S608
    count: int = result.scalar_one()

    elapsed = time.perf_counter() - start
    logger.info(
        "get_table_count(%s) = %d in %.3fs", table_name, count, elapsed,
    )
    return count


# ---------------------------------------------------------------------------
# 5. get_table_data
# ---------------------------------------------------------------------------

def get_table_data(
    db: Session,
    table_name: str,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """Return paginated rows from *table_name* along with the total count."""
    table_name = sanitize_identifier(table_name)
    _assert_table_exists(db, table_name)
    limit = min(max(1, limit), 1000)
    offset = max(0, offset)
    start = time.perf_counter()

    total = get_table_count(db, table_name)

    result = db.execute(
        text(f"SELECT * FROM {table_name} LIMIT :lim OFFSET :off"),  # noqa: S608
        {"lim": limit, "off": offset},
    )
    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchall()]

    elapsed = time.perf_counter() - start
    logger.info(
        "get_table_data(%s, limit=%d, offset=%d) returned %d/%d rows in %.3fs",
        table_name, limit, offset, len(rows), total, elapsed,
    )
    return {"columns": columns, "rows": rows, "total": total}


# ---------------------------------------------------------------------------
# 6. search_table
# ---------------------------------------------------------------------------

def search_table(
    db: Session,
    table_name: str,
    column: str,
    value: str,
) -> dict[str, Any]:
    """Search *table_name* for rows where *column* matches *value* (ILIKE)."""
    table_name = sanitize_identifier(table_name)
    column = sanitize_identifier(column)
    _assert_table_exists(db, table_name)
    start = time.perf_counter()

    query = text(
        f"SELECT * FROM {table_name} WHERE {column}::text ILIKE :val LIMIT 100"  # noqa: S608
    )
    result = db.execute(query, {"val": f"%{value}%"})
    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchall()]

    elapsed = time.perf_counter() - start
    logger.info(
        "search_table(%s, %s, %r) returned %d rows in %.3fs",
        table_name, column, value, len(rows), elapsed,
    )
    return {"columns": columns, "rows": rows}


# ---------------------------------------------------------------------------
# 7. execute_safe_query
# ---------------------------------------------------------------------------

def execute_safe_query(db: Session, query: str) -> dict[str, Any]:
    """
    Validate and execute a user-supplied SELECT query.

    The query is validated by ``security.validate_query`` before execution.
    """
    safe_query = validate_query(query)
    start = time.perf_counter()

    result = db.execute(text(safe_query))
    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchall()]

    elapsed = time.perf_counter() - start
    logger.info(
        "execute_safe_query returned %d rows in %.3fs", len(rows), elapsed,
    )
    return {"columns": columns, "rows": rows}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assert_table_exists(db: Session, table_name: str) -> None:
    """Raise ``ValueError`` if *table_name* does not exist in the database."""
    inspector = inspect(db.bind)
    if table_name not in inspector.get_table_names():
        raise ValueError(f"Table '{table_name}' not found.")
