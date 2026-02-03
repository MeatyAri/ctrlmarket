"""Test workspace screen functionality."""

from textual.widgets import Input, Select

from tui.screens.workspace import WorkspaceScreen


class TestWorkspaceScreen:
    """Test workspace screen functionality."""

    async def test_workspace_screen_composition(self, app, mock_test_user):
        """Test workspace screen composes correctly."""
        async with app.run_test() as pilot:
            app.current_user = mock_test_user
            app.push_screen("workspace")
            await pilot.pause()

            workspace = app.screen
            assert isinstance(workspace, WorkspaceScreen)

    async def test_workspace_customer_access(self, app, mock_customer_user):
        """Test that customer can access workspace."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user
            app.push_screen("workspace")
            await pilot.pause()

            assert isinstance(app.screen, WorkspaceScreen)

    async def test_workspace_specialist_access(self, app, mock_specialist_user):
        """Test that specialist can access workspace."""
        async with app.run_test() as pilot:
            app.current_user = mock_specialist_user
            app.push_screen("workspace")
            await pilot.pause()

            assert isinstance(app.screen, WorkspaceScreen)

    async def test_workspace_admin_access(self, app, mock_admin_user):
        """Test that admin can access workspace."""
        async with app.run_test() as pilot:
            app.current_user = mock_admin_user
            app.push_screen("workspace")
            await pilot.pause()

            assert isinstance(app.screen, WorkspaceScreen)

    async def test_customer_can_see_products_search(self, app, mock_customer_user):
        """Test that customers can see the products search input."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user
            app.push_screen("workspace")
            await pilot.pause()

            search_input = app.screen.query_one("#products-search", Input)
            assert search_input.display

    async def test_customer_can_see_products_category_select(
        self, app, mock_customer_user
    ):
        """Test that customers can see the products category select."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user
            app.push_screen("workspace")
            await pilot.pause()

            category_select = app.screen.query_one("#products-category", Select)
            assert category_select.display

    async def test_customer_can_see_orders_search(self, app, mock_customer_user):
        """Test that customers can see the orders search input."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user
            app.push_screen("workspace")
            await pilot.pause()

            search_input = app.screen.query_one("#orders-search", Input)
            assert search_input.display

    async def test_customer_can_see_services_search(self, app, mock_customer_user):
        """Test that customers can see the services search input."""
        async with app.run_test() as pilot:
            app.current_user = mock_customer_user
            app.push_screen("workspace")
            await pilot.pause()

            search_input = app.screen.query_one("#services-search", Input)
            assert search_input.display
