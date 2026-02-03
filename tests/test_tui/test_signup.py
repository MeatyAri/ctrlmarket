"""Test signup screen functionality."""

from textual.widgets import Input

from tui.screens.login import LoginScreen
from tui.screens.signup import SignupScreen


class TestSignupScreen:
    """Test signup screen functionality."""

    async def test_signup_screen_composition(self, app):
        """Test signup screen has all required widgets."""
        async with app.run_test() as pilot:
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            signup_screen = app.screen
            assert isinstance(signup_screen, SignupScreen)

            assert signup_screen.query_one("#name", Input) is not None
            assert signup_screen.query_one("#email", Input) is not None
            assert signup_screen.query_one("#phone", Input) is not None
            assert signup_screen.query_one("#password", Input) is not None
            assert signup_screen.query_one("#shortcuts-bar") is not None

    async def test_signup_alt1_returns_to_login(self, app):
        """Test Alt+1 key returns to login screen."""
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            await pilot.press("alt+1")
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)
