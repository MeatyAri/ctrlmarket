"""Test login screen functionality."""

from textual.widgets import Input, Label

from tui.screens.login import LoginScreen
from tui.screens.signup import SignupScreen


class TestLoginScreen:
    """Test login screen functionality."""

    async def test_login_screen_composition(self, app):
        """Test login screen has all required widgets."""
        async with app.run_test():
            login_screen = app.screen
            assert isinstance(login_screen, LoginScreen)

            assert login_screen.query_one("#email", Input) is not None
            assert login_screen.query_one("#password", Input) is not None
            assert login_screen.query_one("#shortcuts-bar") is not None

    async def test_login_screen_title_labels(self, app):
        """Test login screen has title labels."""
        async with app.run_test():
            login_screen = app.screen
            labels = list(login_screen.query(Label))
            assert len(labels) >= 6

    async def test_login_action_shows_error_for_empty_fields(self, app):
        """Test login action with empty fields shows error."""
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)
            login_screen = app.screen
            error_label = login_screen.error_label
            assert error_label is not None
            assert error_label.display is True

    async def test_signup_key_navigates_to_signup_screen(self, app):
        """Test pressing 's' key navigates to signup screen."""
        async with app.run_test() as pilot:
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()
            assert isinstance(app.screen, SignupScreen)


class TestWidgetQueries:
    """Test widget querying functionality."""

    async def test_query_input_widgets(self, app):
        """Test querying input widgets."""
        async with app.run_test():
            login_screen = app.screen

            inputs = list(login_screen.query(Input))
            assert len(inputs) >= 2

            shortcuts_bar = login_screen.query_one("#shortcuts-bar")
            assert shortcuts_bar is not None

    async def test_query_by_id(self, app):
        """Test querying widgets by ID."""
        async with app.run_test():
            login_screen = app.screen

            email_input = login_screen.query_one("#email", Input)
            assert email_input is not None
            assert email_input.id == "email"

            password_input = login_screen.query_one("#password", Input)
            assert password_input is not None
            assert password_input.id == "password"
