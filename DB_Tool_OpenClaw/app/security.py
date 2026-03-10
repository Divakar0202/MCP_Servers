"""
Query-level security enforcement.

Every raw SQL string passes through `validate_query` before it reaches the
database.  The function rejects anything that is not a pure SELECT statement.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Tokens that must never appear at the start of a statement (or as a
# secondary statement after a semicolon).
_FORBIDDEN_KEYWORDS: set[str] = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "CALL",
    "MERGE",
    "REPLACE",
    "LOCK",
    "UNLOCK",
    "RENAME",
    "COMMENT",
    "SET",
    "COPY",
}

# Precompiled pattern: matches any forbidden keyword that appears as a
# standalone word (case-insensitive).
_FORBIDDEN_PATTERN = re.compile(
    r"\b(" + "|".join(_FORBIDDEN_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


class UnsafeQueryError(Exception):
    """Raised when a query violates the read-only policy."""


def validate_query(query: str) -> str:
    """
    Validate that *query* is a safe, read-only SELECT statement.

    Returns the stripped query on success; raises ``UnsafeQueryError`` on
    violation.
    """
    stripped = query.strip().rstrip(";").strip()

    if not stripped:
        raise UnsafeQueryError("Empty query is not allowed.")

    # Reject multiple statements (semicolons inside string literals are
    # unlikely in agent-generated queries and worth blocking).
    if ";" in stripped:
        raise UnsafeQueryError(
            "Multiple statements are not allowed. Submit one SELECT at a time."
        )

    # Must start with SELECT or WITH (CTEs)
    first_word = stripped.split()[0].upper()
    if first_word not in ("SELECT", "WITH"):
        raise UnsafeQueryError(
            f"Only SELECT queries are allowed. Got: {first_word}"
        )

    # Scan for forbidden keywords anywhere in the query body
    match = _FORBIDDEN_PATTERN.search(stripped)
    if match:
        raise UnsafeQueryError(
            f"Query contains forbidden keyword: {match.group(0).upper()}"
        )

    logger.info("Query validated: %s", stripped[:120])
    return stripped


def sanitize_identifier(name: str) -> str:
    """
    Ensure *name* is a safe SQL identifier (table or column name).

    Only allows alphanumeric characters, underscores, and dots (for
    schema-qualified names).  Raises ``ValueError`` on bad input.
    """
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", name):
        raise ValueError(f"Invalid identifier: {name!r}")
    return name
