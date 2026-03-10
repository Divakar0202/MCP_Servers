"""PostgreSQL read-only MCP server entrypoint."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field

from data_tools import (
    execute_readonly_query as data_execute_readonly_query,
    get_table_row_count as data_get_table_row_count,
    get_table_sample_data as data_get_table_sample_data,
)
from db_connection import ConnectionManager, load_settings
from documentation_tools import DocumentationService
from schema_tools import (
    describe_table as schema_describe_table,
    get_foreign_keys as schema_get_foreign_keys,
    list_databases as schema_list_databases,
    list_schemas as schema_list_schemas,
    list_tables as schema_list_tables,
)
from utils import MCPToolError, error_response

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "MCP SDK is not available. Install dependencies from requirements.txt before running server."
    ) from exc


class SchemaInput(BaseModel):
    database_name: str = Field(description="Target PostgreSQL database name")


class TableInput(BaseModel):
    database_name: str
    schema_name: str


class DescribeTableInput(BaseModel):
    database_name: str
    schema_name: str
    table_name: str


class TableSampleInput(BaseModel):
    database_name: str
    schema_name: str
    table_name: str
    limit: int = 20


class QueryInput(BaseModel):
    database_name: str
    query: str
    limit: int = 100


class DocumentationSearchInput(BaseModel):
    keyword: str


class DocumentationReadInput(BaseModel):
    file_name: str


project_root = Path(__file__).resolve().parent.parent
try:
    settings = load_settings(project_root / "config" / "config.env")
    connection_manager = ConnectionManager(settings)
    configured_docs_path = Path(settings.documentation_path)
    if not configured_docs_path.is_absolute():
        configured_docs_path = (project_root / configured_docs_path).resolve()
    docs_service = DocumentationService(str(configured_docs_path))
except Exception as _init_err:
    import logging as _log
    _log.getLogger(__name__).warning(
        f"DB server starting without valid settings: {_init_err} — "
        "configure credentials via the MCP control panel and restart the server."
    )
    settings = None
    connection_manager = None
    docs_service = DocumentationService(".")


def safe_tool_call(func):
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            return error_response(exc)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


mcp_transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
mcp_port = int(os.getenv("MCP_PORT", "8613"))

mcp = FastMCP(
    name="postgres-readonly-server",
    instructions="MCP server providing safe read-only PostgreSQL access and documentation lookup tools.",
    host=mcp_host,
    port=mcp_port,
)


@mcp.tool()
@safe_tool_call
def list_databases() -> Dict[str, Any]:
    """Return all non-template databases on the PostgreSQL server."""
    return schema_list_databases(connection_manager)


@mcp.tool()
@safe_tool_call
def list_schemas(input: SchemaInput) -> Dict[str, Any]:
    """Return schemas inside a database."""
    return schema_list_schemas(connection_manager, input.database_name)


@mcp.tool()
@safe_tool_call
def list_tables(input: TableInput) -> Dict[str, Any]:
    """Return all tables in a schema."""
    return schema_list_tables(connection_manager, input.database_name, input.schema_name)


@mcp.tool()
@safe_tool_call
def describe_table(input: DescribeTableInput) -> Dict[str, Any]:
    """Return column metadata for a table."""
    return schema_describe_table(connection_manager, input.database_name, input.schema_name, input.table_name)


@mcp.tool()
@safe_tool_call
def get_table_sample_data(input: TableSampleInput) -> Dict[str, Any]:
    """Return sample rows from a table."""
    return data_get_table_sample_data(
        connection_manager,
        input.database_name,
        input.schema_name,
        input.table_name,
        input.limit,
    )


@mcp.tool()
@safe_tool_call
def get_table_row_count(input: DescribeTableInput) -> Dict[str, Any]:
    """Return row count for a table."""
    return data_get_table_row_count(connection_manager, input.database_name, input.schema_name, input.table_name)


@mcp.tool()
@safe_tool_call
def execute_readonly_query(input: QueryInput) -> Dict[str, Any]:
    """Execute validated read-only SQL query against a selected database."""
    return data_execute_readonly_query(connection_manager, input.database_name, input.query, input.limit)


@mcp.tool()
@safe_tool_call
def get_foreign_keys(input: DescribeTableInput) -> Dict[str, Any]:
    """Return foreign key relationships for a table."""
    return schema_get_foreign_keys(connection_manager, input.database_name, input.schema_name, input.table_name)


@mcp.tool()
@safe_tool_call
def search_documentation(input: DocumentationSearchInput) -> Dict[str, Any]:
    """Search configured documentation directory and return matching sections."""
    return docs_service.search_documentation(input.keyword)


@mcp.tool()
@safe_tool_call
def read_documentation_file(input: DocumentationReadInput) -> Dict[str, Any]:
    """Read a documentation file by name from configured documentation directory."""
    return docs_service.read_documentation_file(input.file_name)


def startup_checks() -> None:
    """Validate startup dependencies before exposing the MCP server."""
    connection_manager.test_connection(settings.default_database)
    docs_service.validate_docs_dir()


if __name__ == "__main__":
    try:
        startup_checks()
    except MCPToolError as exc:
        raise SystemExit(error_response(exc)) from exc

    allowed = {"stdio", "sse", "streamable-http"}
    selected_transport = mcp_transport if mcp_transport in allowed else "stdio"
    mcp.run(transport=selected_transport)
