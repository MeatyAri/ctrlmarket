"""Database connection management module."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


# Database file path
DB_PATH = Path(__file__).parent / "ctrlmarket.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED_DATA_PATH = Path(__file__).parent / "seed_data.sql"


@contextmanager
def get_db_connection():
    """Get a database connection with proper configuration."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize the database with schema and seed data."""
    # Check if database already exists and has data
    if DB_PATH.exists():
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='User'"
            )
            if cursor.fetchone():
                # Check if there's data
                cursor = conn.execute("SELECT COUNT(*) as count FROM User")
                if cursor.fetchone()["count"] > 0:
                    return False  # Database already initialized

    # Create schema
    with get_db_connection() as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())

    # Insert seed data
    with get_db_connection() as conn:
        with open(SEED_DATA_PATH, "r") as f:
            conn.executescript(f.read())

    return True


def reset_database():
    """Reset the database (delete and reinitialize)."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    return init_database()
