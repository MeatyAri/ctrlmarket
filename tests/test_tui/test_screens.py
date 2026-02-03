"""TUI application and screen tests."""

from textual.widgets import Input, Label

from tui.app import CtrlMarketApp
from tui.screens.login import LoginScreen
from tui.screens.signup import SignupScreen
from tui.screens.dashboard import DashboardScreen


class TestCtrlMarketApp:
    """Test main application functionality."""

    async def test_app_initialization(self):
        """Test app initializes correctly."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # App should start
            assert app.is_running

    async def test_app_has_screens_registered(self):
        """Test that all screens are registered."""
        app = CtrlMarketApp()
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

    async def test_app_current_user_starts_none(self):
        """Test that current_user is None at start."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            assert app.current_user is None

    async def test_app_mount_shows_login_screen(self):
        """Test that app shows login screen on mount."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Should be on login screen
            assert isinstance(app.screen, LoginScreen)


class TestLoginScreen:
    """Test login screen functionality."""

    async def test_login_screen_composition(self):
        """Test login screen has all required widgets."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Get login screen
            login_screen = app.screen
            assert isinstance(login_screen, LoginScreen)

            # Check for required widgets
            assert login_screen.query_one("#email", Input) is not None
            assert login_screen.query_one("#password", Input) is not None
            # Shortcuts bar should be present
            assert login_screen.query_one("#shortcuts-bar") is not None

    async def test_login_screen_title_labels(self):
        """Test login screen has title labels."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            login_screen = app.screen
            labels = list(login_screen.query(Label))
            # Should have multiple labels including title
            assert len(labels) >= 6

    async def test_login_action_shows_error_for_empty_fields(self):
        """Test login action with empty fields shows error."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Press Enter to trigger login
            await pilot.press("enter")
            await pilot.pause()

            # Check error message
            assert isinstance(app.screen, LoginScreen)
            login_screen = app.screen
            error_label = login_screen.error_label
            assert error_label is not None
            # Check that error label is visible (has error message)
            assert error_label.display is True

    async def test_signup_key_navigates_to_signup_screen(self):
        """Test pressing 's' key navigates to signup screen."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Unfocus any input by clicking on header, then press 's' to go to signup
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()
            assert isinstance(app.screen, SignupScreen)


class TestSignupScreen:
    """Test signup screen functionality."""

    async def test_signup_screen_composition(self):
        """Test signup screen has all required widgets."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Navigate to signup using keyboard shortcut
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            # Check for required input fields
            signup_screen = app.screen
            assert isinstance(signup_screen, SignupScreen)

            # Should have name, email, phone, password inputs
            assert signup_screen.query_one("#name", Input) is not None
            assert signup_screen.query_one("#email", Input) is not None
            assert signup_screen.query_one("#phone", Input) is not None
            assert signup_screen.query_one("#password", Input) is not None
            # Should have shortcuts bar
            assert signup_screen.query_one("#shortcuts-bar") is not None

    async def test_signup_alt1_returns_to_login(self):
        """Test Alt+1 key returns to login screen."""
        app = CtrlMarketApp()
        async with app.run_test(size=(120, 40)) as pilot:
            # Go to signup
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            # Press Alt+1 to go back
            await pilot.press("alt+1")
            await pilot.pause()

            # Should be back on login
            assert isinstance(app.screen, LoginScreen)


class TestDashboardScreen:
    """Test dashboard screen functionality."""

    async def test_dashboard_screen_composition(self):
        """Test dashboard screen composition."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Set a mock user to access dashboard
            from models import SessionUser

            app.current_user = SessionUser(
                user_id=1,
                name="Test User",
                email="test@example.com",
                role="Customer",
            )

            # Navigate to dashboard
            app.push_screen("dashboard")
            await pilot.pause()

            dashboard = app.screen
            assert isinstance(dashboard, DashboardScreen)

    async def test_dashboard_shows_role_appropriate_menu(self):
        """Test dashboard shows menu based on user role."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            from models import SessionUser

            # Test as Customer
            app.current_user = SessionUser(
                user_id=4,
                name="Customer User",
                email="customer@example.com",
                role="Customer",
            )
            app.push_screen("dashboard")
            await pilot.pause()

            dashboard = app.screen
            assert isinstance(dashboard, DashboardScreen)


class TestScreenNavigation:
    """Test navigation between screens."""

    async def test_login_to_signup_and_back(self):
        """Test navigation from login to signup and back."""
        app = CtrlMarketApp()
        async with app.run_test(size=(120, 40)) as pilot:
            # Start at login
            assert isinstance(app.screen, LoginScreen)

            # Go to signup using 's' key (unfocus input first)
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            # Should be on signup screen
            assert isinstance(app.screen, SignupScreen)

            # Go back to login using Alt+1 key
            await pilot.press("alt+1")
            await pilot.pause()
            assert isinstance(app.screen, LoginScreen)

    async def test_screen_stack_management(self):
        """Test that screen stack is managed properly."""
        app = CtrlMarketApp()
        async with app.run_test(size=(120, 40)) as pilot:
            # Initial screen
            initial_screen = app.screen

            # Navigate to signup using Alt+2 key
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            # Navigate back using Alt+1 key
            await pilot.press("alt+1")
            await pilot.pause()

            # Should be back at login
            assert isinstance(app.screen, LoginScreen)


class TestWidgetQueries:
    """Test widget querying functionality."""

    async def test_query_input_widgets(self):
        """Test querying input widgets."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            login_screen = app.screen

            # Query all inputs
            inputs = list(login_screen.query(Input))
            assert len(inputs) >= 2  # email and password

            # Query shortcuts bar
            shortcuts_bar = login_screen.query_one("#shortcuts-bar")
            assert shortcuts_bar is not None

    async def test_query_by_id(self):
        """Test querying widgets by ID."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            login_screen = app.screen

            # Query specific widgets
            email_input = login_screen.query_one("#email", Input)
            assert email_input is not None
            assert email_input.id == "email"

            password_input = login_screen.query_one("#password", Input)
            assert password_input is not None
            assert password_input.id == "password"


class TestAppCSS:
    """Test CSS loading and application."""

    async def test_css_path_exists(self):
        """Test that CSS path is configured."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            assert app.CSS_PATH is not None
            assert "main.tcss" in str(app.CSS_PATH)

    async def test_screen_css_paths(self):
        """Test that screens have CSS paths configured."""
        app = CtrlMarketApp()
        async with app.run_test() as pilot:
            # Login screen should have CSS
            login_screen = app.screen
            assert login_screen.CSS_PATH is not None
