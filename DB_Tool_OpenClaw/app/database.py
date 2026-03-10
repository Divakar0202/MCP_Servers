"""
SQLAlchemy engine and session factory.

Provides a pooled, reusable database connection.  Every request obtains a
session through the ``get_db`` dependency, which is automatically closed when
the request finishes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from collections.abc import Generator

from app.config import (
    DATABASE_URL,
    DB_POOL_SIZE,
    DB_MAX_OVERFLOW,
    DB_POOL_TIMEOUT,
)

# Create the engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # verify connections before checkout
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
