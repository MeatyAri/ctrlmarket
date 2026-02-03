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
        ("1", "go_workspace", "Workspace"),
        ("4", "go_profile", "Profile"),
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
                nav_workspace.update(
                    "\[1] Workspace - Browse products, view orders and services"
                )
            elif is_specialist:
                nav_workspace.update(
                    "\[1] Workspace - Manage orders and service requests"
                )
            else:
                nav_workspace.update(
                    "\[1] Workspace - Manage products, orders, and services"
                )

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
                    "\[1] Workspace - Browse products, view orders and services",
                    id="nav-workspace",
                )
                yield Label("\[4] Profile - View your profile and logout")
                yield Static("")
                yield Label("Press \[q] to logout", classes="nav-hint")

    def action_go_workspace(self) -> None:
        """Navigate to workspace."""
        self.app.push_screen("workspace")

    def action_go_profile(self) -> None:
        """Navigate to profile."""
        self.app.push_screen("profile")

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.current_user = None
        while len(self.app.screen_stack) > 1:
            self.app.pop_screen()
        self.app.switch_screen("login")
