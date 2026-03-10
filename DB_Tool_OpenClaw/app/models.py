"""
Placeholder models module.

In a typical project this file would contain SQLAlchemy ORM model classes
that map to database tables.  Because this tool introspects an *existing*
database at runtime (via ``inspect``), no ORM models are defined here.

The module is kept as a structural placeholder so the project layout
matches the documented structure and new ORM models can be added later if
needed.
"""

from app.database import Base  # noqa: F401 – re-export for convenience
