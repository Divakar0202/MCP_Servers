"""
Pydantic response / request schemas.

These models define the shape of every JSON body that leaves or enters the
API.  FastAPI uses them for automatic validation, serialization, and
OpenAPI-doc generation.
"""

from pydantic import BaseModel, Field
from typing import Any


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class TableListResponse(BaseModel):
    """List of all table names in the database."""
    tables: list[str]


class ColumnInfo(BaseModel):
    """Description of a single column."""
    name: str
    type: str
    nullable: bool
    default: str | None = None
    primary_key: bool = False


class TableSchemaResponse(BaseModel):
    """Full schema description of a table."""
    table_name: str
    columns: list[ColumnInfo]


class TableCountResponse(BaseModel):
    """Row count for a table."""
    table_name: str
    count: int


class TableDataResponse(BaseModel):
    """Paginated rows from a table."""
    table_name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total: int
    limit: int
    offset: int


class TableSampleResponse(BaseModel):
    """Sample rows from a table."""
    table_name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    limit: int


class SearchResponse(BaseModel):
    """Filtered rows from a table."""
    table_name: str
    column: str
    value: str
    columns: list[str]
    rows: list[dict[str, Any]]
    count: int


class QueryResult(BaseModel):
    """Result of a validated SELECT query."""
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Body for the POST /query endpoint."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="A SELECT-only SQL query.",
    )


# ---------------------------------------------------------------------------
# Error model
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope."""
    detail: str
