"""Pytest configuration and shared fixtures for TUI tests."""

import pytest
from textual.widgets import Input

from models import SessionUser
from tui.app import CtrlMarketApp


@pytest.fixture
def app():
    """Create a CtrlMarketApp instance for testing."""
    return CtrlMarketApp()


@pytest.fixture
async def pilot(app):
    """Create an async pilot for testing the app."""
    async with app.run_test() as pilot:
        yield pilot


@pytest.fixture
def mock_customer_user():
    """Create a mock customer user."""
    return SessionUser(
        user_id=4,
        name="Customer User",
        email="customer@example.com",
        role="Customer",
    )


@pytest.fixture
def mock_specialist_user():
    """Create a mock specialist user."""
    return SessionUser(
        user_id=3,
        name="Specialist User",
        email="specialist@example.com",
        role="Specialist",
    )


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user."""
    return SessionUser(
        user_id=1,
        name="Admin User",
        email="admin@example.com",
        role="Admin",
    )


@pytest.fixture
def mock_test_user():
    """Create a generic test user."""
    return SessionUser(
        user_id=2,
        name="Test User",
        email="test@example.com",
        role="Customer",
    )
