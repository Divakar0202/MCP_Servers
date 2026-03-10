"""
Application configuration.

Loads settings from environment variables or a .env file using python-dotenv.
All configuration is centralized here to keep other modules clean.
"""

import os
from dotenv import load_dotenv

# Load .env file if present (no-op if the file doesn't exist)
load_dotenv()

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/dbname",
)

# Connection-pool tunables
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
APP_TITLE: str = os.getenv("APP_TITLE", "DB Tool OpenClaw")
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
