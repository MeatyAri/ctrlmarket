"""Test navigation between screens."""

from tui.screens.login import LoginScreen
from tui.screens.signup import SignupScreen


class TestScreenNavigation:
    """Test navigation between screens."""

    async def test_login_to_signup_and_back(self, app):
        """Test navigation from login to signup and back."""
        async with app.run_test(size=(120, 40)) as pilot:
            assert isinstance(app.screen, LoginScreen)

            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            assert isinstance(app.screen, SignupScreen)

            await pilot.press("alt+1")
            await pilot.pause()
            assert isinstance(app.screen, LoginScreen)

    async def test_screen_stack_management(self, app):
        """Test that screen stack is managed properly."""
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.click(".workspace-header")
            await pilot.press("alt+2")
            await pilot.pause()

            await pilot.press("alt+1")
            await pilot.pause()

            assert isinstance(app.screen, LoginScreen)
