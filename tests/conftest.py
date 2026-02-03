"""Test configuration and shared fixtures."""

import sqlite3
import sys
from pathlib import Path
from typing import Generator

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import bcrypt  # noqa: E402
import pytest  # noqa: E402

from database.connection import SCHEMA_PATH, SEED_DATA_PATH  # noqa: E402


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary database path for isolated tests."""
    temp_path = tmp_path / "test_ctrlmarket.db"
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def test_db_connection(temp_db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Create a test database with schema and seed data."""
    # Create connection
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Create schema
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    # Insert seed data
    with open(SEED_DATA_PATH, "r") as f:
        conn.executescript(f.read())

    yield conn

    # Cleanup
    conn.close()


@pytest.fixture
def mock_db_path(monkeypatch, temp_db_path: Path) -> Path:
    """Mock the database path to use temporary database."""
    import importlib
    import database.connection as conn_module

    # Store original path
    original_path = conn_module.DB_PATH

    # Set temporary path
    conn_module.DB_PATH = temp_db_path

    # Initialize the temp database
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Create schema
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    # Insert seed data
    with open(SEED_DATA_PATH, "r") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()

    # Reload connection module to ensure fresh imports
    importlib.reload(conn_module)
    conn_module.DB_PATH = temp_db_path

    yield temp_db_path

    # Restore original path
    conn_module.DB_PATH = original_path


@pytest.fixture
def test_queries(mock_db_path):
    """Provide a fresh queries module with mocked DB."""
    import importlib
    import database.queries as queries_module

    importlib.reload(queries_module)
    return queries_module


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "09123456789",
        "role": "Customer",
        "password": "password123",
    }


@pytest.fixture
def sample_product_data() -> dict:
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "category": "Test Category",
        "price": 99.99,
    }


@pytest.fixture
def sample_order_data() -> dict:
    """Sample order data for testing."""
    return {
        "user_id": 4,  # Mohammad Karimi from seed data
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1},
        ],
    }


@pytest.fixture
def sample_service_request_data() -> dict:
    """Sample service request data for testing."""
    return {
        "service_type": "Installation",
        "customer_id": 4,  # Mohammad Karimi from seed data
    }


@pytest.fixture
def hash_password():
    """Helper to hash passwords for testing."""

    def _hash(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    return _hash
