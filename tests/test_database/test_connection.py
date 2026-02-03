"""Database connection and initialization tests."""

import sqlite3
from pathlib import Path


from database.connection import (
    DB_PATH,
    SCHEMA_PATH,
    SEED_DATA_PATH,
    get_db_connection,
    init_database,
    reset_database,
)


class TestDatabaseConnection:
    """Test database connection management."""

    def test_db_paths_exist(self):
        """Test that database file paths exist."""
        assert DB_PATH is not None
        assert SCHEMA_PATH.exists(), f"Schema file not found: {SCHEMA_PATH}"
        assert SEED_DATA_PATH.exists(), f"Seed data file not found: {SEED_DATA_PATH}"

    def test_get_db_connection_returns_valid_connection(self, mock_db_path):
        """Test that get_db_connection returns a valid SQLite connection."""
        with get_db_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            # Test that we can execute a query
            cursor = conn.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1

    def test_connection_has_row_factory(self, mock_db_path):
        """Test that connection has Row factory enabled."""
        with get_db_connection() as conn:
            assert conn.row_factory == sqlite3.Row

    def test_connection_has_foreign_keys_enabled(self, mock_db_path):
        """Test that foreign keys are enabled."""
        with get_db_connection() as conn:
            cursor = conn.execute("PRAGMA foreign_keys")
            assert cursor.fetchone()[0] == 1

    def test_connection_auto_commit_on_success(self, mock_db_path):
        """Test that connection commits on successful exit."""
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                ("Test", "test_commit@example.com", "09123456789", "Customer", "hash"),
            )

        # Verify data was committed
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM User WHERE email = ?", ("test_commit@example.com",)
            )
            assert cursor.fetchone() is not None

    def test_connection_rollback_on_exception(self, mock_db_path):
        """Test that connection rolls back on exception."""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                    (
                        "Test",
                        "test_rollback@example.com",
                        "09123456789",
                        "Customer",
                        "hash",
                    ),
                )
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify data was not committed
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM User WHERE email = ?", ("test_rollback@example.com",)
            )
            assert cursor.fetchone() is None


class TestDatabaseInitialization:
    """Test database initialization functions."""

    def test_init_database_creates_schema(self, tmp_path: Path):
        """Test that init_database creates the schema."""
        import database.connection as conn_module

        # Use temporary path
        original_path = conn_module.DB_PATH
        temp_db = tmp_path / "init_test.db"
        conn_module.DB_PATH = temp_db

        try:
            result = init_database()
            assert result is True

            # Verify tables exist
            conn = sqlite3.connect(temp_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row["name"] for row in cursor.fetchall()}

            assert "User" in tables
            assert "Product" in tables
            assert "Order" in tables
            assert "OrderItem" in tables
            assert "ServiceRequest" in tables
            conn.close()
        finally:
            conn_module.DB_PATH = original_path
            if temp_db.exists():
                temp_db.unlink()

    def test_init_database_skips_if_already_initialized(self, tmp_path: Path):
        """Test that init_database skips if data exists."""
        import database.connection as conn_module

        original_path = conn_module.DB_PATH
        temp_db = tmp_path / "init_skip_test.db"
        conn_module.DB_PATH = temp_db

        try:
            # First initialization
            result1 = init_database()
            assert result1 is True

            # Second initialization should skip
            result2 = init_database()
            assert result2 is False
        finally:
            conn_module.DB_PATH = original_path
            if temp_db.exists():
                temp_db.unlink()

    def test_reset_database_deletes_and_reinitializes(self, tmp_path: Path):
        """Test that reset_database deletes and reinitializes."""
        import database.connection as conn_module

        original_path = conn_module.DB_PATH
        temp_db = tmp_path / "reset_test.db"
        conn_module.DB_PATH = temp_db

        try:
            # Initialize first
            init_database()

            # Add custom data
            conn = sqlite3.connect(temp_db)
            conn.execute(
                "INSERT INTO User (name, email, phone, role, password_hash) VALUES (?, ?, ?, ?, ?)",
                ("Custom", "custom@example.com", "09123456789", "Customer", "hash"),
            )
            conn.commit()
            conn.close()

            # Reset
            result = reset_database()
            assert result is True

            # Verify custom data is gone but seed data exists
            conn = sqlite3.connect(temp_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM User WHERE email = ?", ("custom@example.com",)
            )
            assert cursor.fetchone() is None

            # Check seed data exists
            cursor = conn.execute(
                "SELECT * FROM User WHERE email = ?", ("admin@ctrlmarket.com",)
            )
            assert cursor.fetchone() is not None
            conn.close()
        finally:
            conn_module.DB_PATH = original_path
            if temp_db.exists():
                temp_db.unlink()


class TestDatabaseSchema:
    """Test database schema constraints and indexes."""

    def test_foreign_keys_enabled(self, mock_db_path):
        """Test that foreign keys are properly enabled."""
        with get_db_connection() as conn:
            cursor = conn.execute("PRAGMA foreign_keys")
            assert cursor.fetchone()[0] == 1

    def test_required_indexes_exist(self, mock_db_path):
        """Test that required indexes are created."""
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = {row["name"] for row in cursor.fetchall()}

            assert "idx_order_user" in indexes
            assert "idx_order_status" in indexes
            assert "idx_orderitem_order" in indexes
            assert "idx_orderitem_product" in indexes
            assert "idx_servicereq_customer" in indexes
            assert "idx_servicereq_specialist" in indexes
            assert "idx_servicereq_status" in indexes
            assert "idx_product_category" in indexes
