# PostgreSQL Read-Only MCP Server

Python MCP server that exposes safe read-only PostgreSQL tools for AI agents.

## Features

- Strict read-only SQL validation (`SELECT`, `WITH`, `EXPLAIN` only)
- Database exploration tools (`list_databases`, `list_schemas`, `list_tables`)
- Table metadata and relationship tools (`describe_table`, `get_foreign_keys`)
- Data retrieval tools (`get_table_sample_data`, `get_table_row_count`, `execute_readonly_query`)
- External documentation tools (`search_documentation`, `read_documentation_file`)
- SQLAlchemy connection pooling and per-database engine switching
- Structured JSON responses for success and errors

## Project Structure

```text
postgres_mcp_server/
  config/
    config.env
  src/
    server.py
    db_connection.py
    query_validator.py
    schema_tools.py
    data_tools.py
    documentation_tools.py
    utils.py
  requirements.txt
  README.md
```

## Configuration

Update `config/config.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DEFAULT_DATABASE=postgres
DOCUMENTATION_PATH=../documentation
MAX_RETURNED_ROWS=100
```

You can also set these values in environment variables.

## Installation

```bash
cd postgres_mcp_server
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
python src/server.py
```

On startup the server:

1. Loads configuration.
2. Validates database connectivity.
3. Verifies documentation folder exists.
4. Starts MCP server.

## Tool Contracts

All tools return JSON objects.

Success example:

```json
{
  "success": true,
  "tables": ["users", "orders"]
}
```

Error example:

```json
{
  "success": false,
  "error": {
    "code": "read_only_violation",
    "message": "Only SELECT, WITH, or EXPLAIN queries are allowed.",
    "details": {}
  }
}
```

## Security Notes

- DDL/DML keywords are blocked by `query_validator.py`.
- Multi-statement SQL is rejected.
- Schema/table/database identifiers are validated.
- Documentation file access is restricted to configured docs directory.
