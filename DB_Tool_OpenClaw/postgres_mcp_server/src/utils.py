"""Utility helpers shared by MCP server modules."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Dict, List


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class MCPToolError(Exception):
    """Base exception for structured tool errors."""

    def __init__(self, code: str, message: str, details: Dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def success_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a stable success envelope."""
    return {"success": True, **payload}


def error_response(exc: Exception) -> Dict[str, Any]:
    """Convert exceptions into stable JSON-serializable error payloads."""
    if isinstance(exc, MCPToolError):
        return {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        }

    return {
        "success": False,
        "error": {
            "code": "internal_error",
            "message": str(exc),
            "details": {},
        },
    }


def ensure_identifier(value: str, field_name: str) -> str:
    """Validate SQL identifiers used for schema/table/database names."""
    if not value or not IDENTIFIER_PATTERN.match(value):
        raise MCPToolError(
            code="invalid_identifier",
            message=f"Invalid {field_name}: '{value}'.",
            details={"field": field_name, "value": value},
        )
    return value


def ensure_file_in_directory(file_path: Path, directory: Path) -> Path:
    """Ensure a file path resolves under a base directory (path traversal protection)."""
    try:
        resolved_file = file_path.resolve(strict=False)
        resolved_dir = directory.resolve(strict=True)
    except FileNotFoundError:
        raise MCPToolError(
            code="documentation_directory_missing",
            message=f"Documentation directory not found: {directory}",
        )

    if resolved_dir not in resolved_file.parents and resolved_file != resolved_dir:
        raise MCPToolError(
            code="invalid_documentation_path",
            message="Requested file is outside the documentation directory.",
        )

    return resolved_file


def rows_to_dicts(columns: List[str], rows: List[tuple]) -> List[Dict[str, Any]]:
    """Convert DB row tuples into list-of-dicts shape."""
    return [dict(zip(columns, row)) for row in rows]
