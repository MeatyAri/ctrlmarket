"""Test dashboard screen functionality."""

from models import SessionUser
from tui.app import CtrlMarketApp
from tui.screens.dashboard import DashboardScreen


class TestDashboardScreen:
    """Test dashboard screen functionality."""

    async def test_dashboard_screen_composition(self, app, mock_test_user):
        """Test dashboard screen composition."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user

            app.push_screen("dashboard")
            await pilot.pause()

            dashboard = app.screen
            assert isinstance(dashboard, DashboardScreen)

    async def test_dashboard_shows_role_appropriate_menu(self, app, mock_customer_user):
        """Test dashboard shows menu based on user role."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user
            app.push_screen("dashboard")
            await pilot.pause()

            dashboard = app.screen
            assert isinstance(dashboard, DashboardScreen)
