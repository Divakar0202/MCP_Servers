"""Read-only SQL validation logic."""

from __future__ import annotations

import re

from utils import MCPToolError


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "GRANT",
    "REVOKE",
    "MERGE",
    "CALL",
    "DO",
    "COPY",
}

ALLOWED_STARTS = ("SELECT", "WITH", "EXPLAIN")


def _normalize_sql(query: str) -> str:
    query = query.strip()
    if not query:
        raise MCPToolError(code="invalid_query", message="Query cannot be empty.")

    # Remove SQL comments before inspection.
    query = re.sub(r"--.*?$", "", query, flags=re.MULTILINE)
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
    return query.strip()


def validate_read_only_query(query: str) -> str:
    """Validate that a SQL statement is read-only and single-statement."""
    normalized = _normalize_sql(query)
    upper = normalized.upper()

    if not upper.startswith(ALLOWED_STARTS):
        raise MCPToolError(
            code="read_only_violation",
            message="Only SELECT, WITH, or EXPLAIN queries are allowed.",
        )

    # Reject multi-statement queries.
    semicolons = [m.start() for m in re.finditer(r";", upper)]
    if semicolons:
        if len(semicolons) > 1 or semicolons[0] != len(upper) - 1:
            raise MCPToolError(
                code="read_only_violation",
                message="Multiple SQL statements are not allowed.",
            )
        upper = upper[:-1].rstrip()
        normalized = normalized[:-1].rstrip()

    # Detect forbidden DDL/DML keywords as standalone words.
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper):
            raise MCPToolError(
                code="read_only_violation",
                message=f"Query contains forbidden operation: {keyword}.",
            )

    return normalized
