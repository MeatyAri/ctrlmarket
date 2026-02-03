"""Test profile screen functionality."""

from textual.widgets import DataTable, TabbedContent

from tui.screens.profile import ProfileScreen


class TestProfileScreen:
    """Test profile screen functionality."""

    async def test_profile_screen_non_admin_mount(self, app, mock_customer_user):
        """Test that non-admin users can mount profile screen without errors."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user

            app.push_screen("profile")
            await pilot.pause()

            assert isinstance(app.screen, ProfileScreen)

    async def test_profile_screen_admin_mount(self, app, mock_admin_user):
        """Test that admin users can mount profile screen with users table."""
        async with app.run_test() as pilot:
            app.current_user = mock_admin_user

            app.push_screen("profile")
            await pilot.pause()

            assert isinstance(app.screen, ProfileScreen)

            users_table = app.screen.query_one("#users-table", DataTable)
            assert users_table is not None

    async def test_profile_screen_non_admin_no_users_table(
        self, app, mock_specialist_user
    ):
        """Test that non-admin users do NOT have users table."""
        async with app.run_test() as pilot:
            app.current_user = mock_specialist_user

            app.push_screen("profile")
            await pilot.pause()

            users = list(app.screen.query(DataTable))
            users_tables = [w for w in users if w.id == "users-table"]
            assert len(users_tables) == 0

    async def test_profile_screen_non_admin_refresh(self, app, mock_customer_user):
        """Test that refresh action works for non-admin users without errors."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user

            app.push_screen("profile")
            await pilot.pause()

            profile_screen = app.screen
            assert isinstance(profile_screen, ProfileScreen)

            profile_screen.action_refresh()
            await pilot.pause()

    async def test_profile_screen_admin_refresh(self, app, mock_admin_user):
        """Test that refresh action works for admin users."""
        async with app.run_test() as pilot:
            app.current_user = mock_admin_user

            app.push_screen("profile")
            await pilot.pause()

            profile_screen = app.screen
            assert isinstance(profile_screen, ProfileScreen)

            profile_screen.action_refresh()
            await pilot.pause()

    async def test_profile_screen_specialist_can_access(
        self, app, mock_specialist_user
    ):
        """Test that specialist users can access profile screen without errors."""
        async with app.run_test() as pilot:
            app.current_user = mock_specialist_user

            app.push_screen("profile")
            await pilot.pause()

            assert isinstance(app.screen, ProfileScreen)

    async def test_profile_screen_admin_has_tabbed_content(self, app, mock_admin_user):
        """Test that admin users see tabbed content with two tabs."""
        async with app.run_test() as pilot:
            app.current_user = mock_admin_user

            app.push_screen("profile")
            await pilot.pause()

            tabbed = app.screen.query_one(TabbedContent)
            assert tabbed is not None
            assert tabbed.active == "profile"

    async def test_profile_screen_non_admin_no_tabbed_content(
        self, app, mock_customer_user
    ):
        """Test that non-admin users do NOT see tabbed content."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user

            app.push_screen("profile")
            await pilot.pause()

            tabbed_content = list(app.screen.query(TabbedContent))
            assert len(tabbed_content) == 0
