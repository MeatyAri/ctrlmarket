"""Dashboard screen with welcome message and navigation hints."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label, Static

from models import SessionUser


class DashboardScreen(Screen):
    """Main dashboard with welcome message and navigation."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("alt+1", "go_workspace", "Workspace"),
        ("alt+2", "go_workspace_orders", "Orders"),
        ("alt+3", "go_workspace_services", "Services"),
        ("alt+4", "go_profile", "Profile"),
        ("q", "logout", "Logout"),
    ]

    def __init__(self) -> None:
        self.user: SessionUser | None = None
        super().__init__()

    def on_mount(self) -> None:
        """Load user data when screen is mounted."""
        self.user = getattr(self.app, "current_user", None)
        self._update_content()

    def _update_content(self) -> None:
        """Update content with user info and role-specific text."""
        if self.user:
            self.query_one("#user-info", Label).update(
                f"Welcome, {self.user.name} ({self.user.role})"
            )

            # Update navigation hints based on role
            is_customer = self.user.role == "Customer"
            is_specialist = self.user.role == "Specialist"

            nav_workspace = self.query_one("#nav-workspace", Label)
            if is_customer:
                nav_workspace.update("\\[Alt+1] Workspace - Browse products")
            elif is_specialist:
                nav_workspace.update("\\[Alt+1] Workspace - Manage orders and services")
            else:
                nav_workspace.update("\\[Alt+1] Workspace - Manage products")

            nav_orders = self.query_one("#nav-orders", Label)
            if is_customer:
                nav_orders.update("\\[Alt+2] Orders - View your orders")
            elif is_specialist:
                nav_orders.update("\\[Alt+2] Orders - Manage orders")
            else:
                nav_orders.update("\\[Alt+2] Orders - Manage orders")

            nav_services = self.query_one("#nav-services", Label)
            if is_customer:
                nav_services.update("\\[Alt+3] Services - View service requests")
            elif is_specialist:
                nav_services.update("\\[Alt+3] Services - Manage service requests")
            else:
                nav_services.update("\\[Alt+3] Services - Manage service requests")

    def compose(self) -> ComposeResult:
        # Header
        with Container(classes="dashboard-header"):
            yield Label("CTRL Market", classes="dashboard-title")

        # Main content
        with Container(classes="dashboard-content"):
            with Container(classes="welcome-container"):
                yield Label("Welcome to CTRL Market", classes="welcome-title")
                yield Label("User", id="user-info")
                yield Static("")
                yield Label("Smart Equipment Sales & Services Platform")
                yield Static("")
                yield Label("Navigation:", classes="content-title")
                yield Label(
                    "\\[Alt+1] Workspace - Manage products",
                    id="nav-workspace",
                )
                yield Label("\\[Alt+2] Orders - Manage orders", id="nav-orders")
                yield Label("\\[Alt+3] Services - Manage services", id="nav-services")
                yield Label("\\[Alt+4] Profile - View your profile and logout")
                yield Static("")
                yield Label("Press \\[q] to logout", classes="nav-hint")

    def action_go_workspace(self) -> None:
        """Navigate to workspace."""
        from tui.screens.workspace import WorkspaceScreen

        self.app.push_screen(WorkspaceScreen(initial_tab="products"))

    def action_go_workspace_orders(self) -> None:
        """Navigate to workspace with orders tab."""
        from tui.screens.workspace import WorkspaceScreen

        self.app.push_screen(WorkspaceScreen(initial_tab="orders"))

    def action_go_workspace_services(self) -> None:
        """Navigate to workspace with services tab."""
        from tui.screens.workspace import WorkspaceScreen

        self.app.push_screen(WorkspaceScreen(initial_tab="services"))

    def action_go_profile(self) -> None:
        """Navigate to profile."""
        self.app.push_screen("profile")

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()
