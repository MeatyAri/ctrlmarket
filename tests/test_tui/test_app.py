"""Test main application functionality."""

from textual.widgets import Input

from models import SessionUser
from tui.app import CtrlMarketApp
from tui.screens.dashboard import DashboardScreen
from tui.screens.login import LoginScreen


class TestCtrlMarketApp:
    """Test main application initialization."""

    async def test_app_initialization(self, app):
        """Test app initializes correctly."""
        async with app.run_test() as pilot:
            assert app.is_running

    async def test_app_has_screens_registered(self, app):
        """Test that all screens are registered."""
        async with app.run_test() as pilot:
            expected_screens = [
                "login",
                "signup",
                "dashboard",
                "workspace",
                "profile",
                "order_new",
                "product_new",
                "service_new",
                "user_new",
            ]
            for screen_name in expected_screens:
                assert screen_name in app.SCREENS

    async def test_app_current_user_starts_none(self, app):
        """Test that current_user is None at start."""
        async with app.run_test() as pilot:
            assert app.current_user is None

    async def test_app_mount_shows_login_screen(self, app):
        """Test that app shows login screen on mount."""
        async with app.run_test() as pilot:
            assert isinstance(app.screen, LoginScreen)


class TestAppCSS:
    """Test CSS loading and application."""

    async def test_css_path_exists(self, app):
        """Test that CSS path is configured."""
        async with app.run_test() as pilot:
            assert app.CSS_PATH is not None
            assert "main.tcss" in str(app.CSS_PATH)

    async def test_screen_css_paths(self, app):
        """Test that screens have CSS paths configured."""
        async with app.run_test() as pilot:
            login_screen = app.screen
            assert login_screen.CSS_PATH is not None


class TestLogoutFunctionality:
    """Test logout functionality across all screens."""

    async def test_app_has_logout_method(self, app):
        """Test that CtrlMarketApp has a logout method."""
        assert hasattr(app, "logout")
        assert callable(app.logout)

    async def test_logout_from_login_screen_does_nothing(self, app):
        """Test that calling logout on login screen doesn't cause errors."""
        async with app.run_test() as pilot:
            app.logout()
            await pilot.pause()
            assert isinstance(app.screen, LoginScreen)

    async def test_logout_clears_current_user(self, app, mock_test_user):
        """Test that logout clears the current_user."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            assert app.current_user is not None

            app.logout()
            await pilot.pause()

            assert app.current_user is None

    async def test_logout_shows_login_screen(self, app, mock_test_user):
        """Test that logout returns to login screen."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            app.push_screen("dashboard")
            await pilot.pause()

            assert isinstance(app.screen, DashboardScreen)

            app.logout()
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)

    async def test_logout_resets_screen_stack(self, app, mock_admin_user):
        """Test that logout resets the screen stack to just login."""
        async with app.run_test() as pilot:
            app.current_user = mock_admin_user
            app.push_screen("dashboard")
            await pilot.pause()
            app.push_screen("workspace")
            await pilot.pause()
            app.push_screen("profile")
            await pilot.pause()

            assert len(app.screen_stack) > 1

            app.logout()
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)

    async def test_logout_from_dashboard(self, app, mock_test_user):
        """Test logout action from dashboard screen."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            app.push_screen("dashboard")
            await pilot.pause()

            dashboard = app.screen
            assert isinstance(dashboard, DashboardScreen)

            await pilot.press("q")
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)
            assert app.current_user is None

    async def test_logout_from_workspace(self, app, mock_test_user):
        """Test logout action from workspace screen."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            app.push_screen("workspace")
            await pilot.pause()

            await pilot.press("q")
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)
            assert app.current_user is None

    async def test_logout_clears_login_inputs(self, app, mock_test_user):
        """Test that logout clears login screen input fields."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            app.push_screen("dashboard")
            await pilot.pause()

            app.logout()
            await pilot.pause()

            login_screen = app.screen
            assert isinstance(login_screen, LoginScreen)
            email_input = login_screen.query_one("#email", Input)
            password_input = login_screen.query_one("#password", Input)
            assert email_input.value == ""
            assert password_input.value == ""

    async def test_logout_does_not_cause_index_error(
        self, app, mock_test_user, mock_admin_user
    ):
        """Test that logout from any screen level doesn't cause IndexError."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            app.push_screen("dashboard")
            await pilot.pause()

            try:
                app.logout()
                await pilot.pause()
            except IndexError:
                assert False, "Logout should not raise IndexError"

            app.current_user = mock_admin_user
            app.push_screen("dashboard")
            await pilot.pause()
            app.push_screen("workspace")
            await pilot.pause()
            app.push_screen("profile")
            await pilot.pause()
            app.push_screen("user_new")
            await pilot.pause()

            try:
                app.logout()
                await pilot.pause()
            except IndexError:
                assert False, "Logout from nested screens should not raise IndexError"

    async def test_login_after_logout_works(self, app):
        """Test that user can login again after logout."""
        async with app.run_test() as pilot:
            first_user = SessionUser(
                user_id=1,
                name="First User",
                email="test@example.com",
                role="Customer",
            )
            app.current_user = first_user
            app.push_screen("dashboard")
            await pilot.pause()

            app.logout()
            await pilot.pause()

            second_user = SessionUser(
                user_id=2,
                name="Second User",
                email="other@example.com",
                role="Admin",
            )
            app.current_user = second_user
            app.push_screen("dashboard")
            await pilot.pause()

            assert isinstance(app.screen, DashboardScreen)
            assert app.current_user.user_id == 2
            assert app.current_user.name == "Second User"
