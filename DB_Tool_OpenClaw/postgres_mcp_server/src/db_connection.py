"""Database configuration and SQLAlchemy connection management."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError

from utils import MCPToolError


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[tuple]


class Settings(BaseModel):
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(alias="POSTGRES_PORT")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    default_database: str = Field(alias="DEFAULT_DATABASE")
    documentation_path: str = Field(default="../documentation", alias="DOCUMENTATION_PATH")
    max_returned_rows: int = Field(default=100, alias="MAX_RETURNED_ROWS")


class ConnectionManager:
    """Create and cache per-database SQLAlchemy engines with pooling."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._engines: Dict[str, Engine] = {}

    def _build_engine(self, database_name: str) -> Engine:
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=self.settings.postgres_user,
            password=self.settings.postgres_password,
            host=self.settings.postgres_host,
            port=self.settings.postgres_port,
            database=database_name,
        )
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
            future=True,
        )

    def get_engine(self, database_name: Optional[str] = None) -> Engine:
        db = database_name or self.settings.default_database
        if db not in self._engines:
            self._engines[db] = self._build_engine(db)
        return self._engines[db]

    def test_connection(self, database_name: Optional[str] = None) -> None:
        engine = self.get_engine(database_name)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise MCPToolError(
                code="database_connection_error",
                message="Failed to connect to PostgreSQL.",
                details={"database": database_name or self.settings.default_database, "reason": str(exc)},
            )

    def execute_query(
        self,
        sql: str,
        database_name: Optional[str] = None,
        params: Optional[dict] = None,
        fetch_limit: Optional[int] = None,
    ) -> QueryResult:
        engine = self.get_engine(database_name)
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                columns = list(result.keys())
                rows = result.fetchmany(fetch_limit) if fetch_limit else result.fetchall()
                return QueryResult(columns=columns, rows=rows)
        except SQLAlchemyError as exc:
            raise MCPToolError(
                code="database_query_error",
                message="Database query failed.",
                details={"database": database_name or self.settings.default_database, "reason": str(exc)},
            )


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """Load environment values from config file and process environment."""
    if config_path:
        load_dotenv(dotenv_path=config_path)
    else:
        # Fallback to repo-local default config path.
        default_path = Path(__file__).resolve().parent.parent / "config" / "config.env"
        load_dotenv(dotenv_path=default_path)

    import os

    raw_values = {
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "DEFAULT_DATABASE": os.getenv("DEFAULT_DATABASE"),
        "DOCUMENTATION_PATH": os.getenv("DOCUMENTATION_PATH", "../documentation"),
        "MAX_RETURNED_ROWS": os.getenv("MAX_RETURNED_ROWS", "100"),
    }

    try:
        return Settings.model_validate(raw_values)
    except ValidationError as exc:
        raise MCPToolError(
            code="invalid_configuration",
            message="Configuration values are missing or invalid.",
            details={"reason": str(exc)},
        )
