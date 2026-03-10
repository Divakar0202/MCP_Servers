"""
FastAPI application – read-only database tools for AI agents.

All endpoints are strictly read-only.  Write operations are rejected at
the security layer before they ever reach the database.
"""

import logging
import time

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import (
    NoSuchTableError,
    OperationalError,
    ProgrammingError,
)

from app.config import APP_TITLE, APP_VERSION, LOG_LEVEL
from app.database import get_db
from app.security import UnsafeQueryError
from app import db_tools, schemas

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=(
        "Read-only database access tools for AI agent platforms such as "
        "OpenClaw.  All write operations are blocked at the query-validation "
        "layer."
    ),
)


# ---------------------------------------------------------------------------
# Middleware – request timing
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_request_time(request, call_next):
    """Log the duration of every HTTP request."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info(
        "%s %s -> %d (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /tables
# ---------------------------------------------------------------------------

@app.get(
    "/tables",
    response_model=schemas.TableListResponse,
    tags=["tables"],
    summary="List all tables",
)
def list_tables(db: Session = Depends(get_db)):
    """Return every user-table name in the connected database."""
    try:
        tables = db_tools.list_tables(db)
        return schemas.TableListResponse(tables=tables)
    except OperationalError as exc:
        logger.error("Database error in list_tables: %s", exc)
        raise HTTPException(status_code=500, detail="Database connection error.")


# ---------------------------------------------------------------------------
# GET /tables/{table_name}/schema
# ---------------------------------------------------------------------------

@app.get(
    "/tables/{table_name}/schema",
    response_model=schemas.TableSchemaResponse,
    tags=["tables"],
    summary="Describe table schema",
)
def describe_table(table_name: str, db: Session = Depends(get_db)):
    """Return column metadata for a given table."""
    try:
        columns = db_tools.describe_table(db, table_name)
        return schemas.TableSchemaResponse(
            table_name=table_name,
            columns=[schemas.ColumnInfo(**c) for c in columns],
        )
    except (NoSuchTableError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=f"Table not found: {table_name}")
    except OperationalError as exc:
        logger.error("Database error in describe_table: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")


# ---------------------------------------------------------------------------
# GET /tables/{table_name}/count
# ---------------------------------------------------------------------------

@app.get(
    "/tables/{table_name}/count",
    response_model=schemas.TableCountResponse,
    tags=["tables"],
    summary="Get row count",
)
def table_count(table_name: str, db: Session = Depends(get_db)):
    """Return the total number of rows in a table."""
    try:
        count = db_tools.get_table_count(db, table_name)
        return schemas.TableCountResponse(table_name=table_name, count=count)
    except (ProgrammingError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=f"Table not found: {table_name}")
    except OperationalError as exc:
        logger.error("Database error in table_count: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")


# ---------------------------------------------------------------------------
# GET /tables/{table_name}/sample
# ---------------------------------------------------------------------------

@app.get(
    "/tables/{table_name}/sample",
    response_model=schemas.TableSampleResponse,
    tags=["tables"],
    summary="Get sample rows",
)
def table_sample(
    table_name: str,
    limit: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Return a few sample rows from a table."""
    try:
        data = db_tools.get_table_sample(db, table_name, limit=limit)
        return schemas.TableSampleResponse(
            table_name=table_name,
            columns=data["columns"],
            rows=data["rows"],
            limit=limit,
        )
    except (ProgrammingError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=f"Table not found: {table_name}")
    except OperationalError as exc:
        logger.error("Database error in table_sample: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")


# ---------------------------------------------------------------------------
# GET /tables/{table_name}/data
# ---------------------------------------------------------------------------

@app.get(
    "/tables/{table_name}/data",
    response_model=schemas.TableDataResponse,
    tags=["tables"],
    summary="Get paginated data",
)
def table_data(
    table_name: str,
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Return paginated rows from a table with total count."""
    try:
        data = db_tools.get_table_data(db, table_name, limit=limit, offset=offset)
        return schemas.TableDataResponse(
            table_name=table_name,
            columns=data["columns"],
            rows=data["rows"],
            total=data["total"],
            limit=limit,
            offset=offset,
        )
    except (ProgrammingError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=f"Table not found: {table_name}")
    except OperationalError as exc:
        logger.error("Database error in table_data: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")


# ---------------------------------------------------------------------------
# GET /tables/{table_name}/search
# ---------------------------------------------------------------------------

@app.get(
    "/tables/{table_name}/search",
    response_model=schemas.SearchResponse,
    tags=["tables"],
    summary="Search a table by column value",
)
def search_table(
    table_name: str,
    column: str = Query(..., description="Column to filter on."),
    value: str = Query(..., description="Value to search for (case-insensitive partial match)."),
    db: Session = Depends(get_db),
):
    """Filter rows where *column* contains *value* (ILIKE)."""
    try:
        data = db_tools.search_table(db, table_name, column=column, value=value)
        return schemas.SearchResponse(
            table_name=table_name,
            column=column,
            value=value,
            columns=data["columns"],
            rows=data["rows"],
            count=len(data["rows"]),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (ProgrammingError,) as exc:
        raise HTTPException(status_code=404, detail=f"Table or column not found.")
    except OperationalError as exc:
        logger.error("Database error in search_table: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")


# ---------------------------------------------------------------------------
# POST /query
# ---------------------------------------------------------------------------

@app.post(
    "/query",
    response_model=schemas.QueryResult,
    tags=["query"],
    summary="Execute a safe SELECT query",
)
def execute_query(body: schemas.QueryRequest, db: Session = Depends(get_db)):
    """
    Execute a user-supplied SQL query after validating that it is read-only.

    Rejects any query containing INSERT, UPDATE, DELETE, DROP, ALTER,
    TRUNCATE, or other write operations.
    """
    try:
        data = db_tools.execute_safe_query(db, body.query)
        return schemas.QueryResult(
            columns=data["columns"],
            rows=data["rows"],
            row_count=len(data["rows"]),
        )
    except UnsafeQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ProgrammingError as exc:
        logger.warning("Bad query: %s", exc)
        raise HTTPException(status_code=400, detail=f"Query error: {exc.orig}")
    except OperationalError as exc:
        logger.error("Database error in execute_query: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")
