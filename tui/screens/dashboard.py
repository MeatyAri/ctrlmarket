"""Dashboard screen with sidebar navigation."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Label, Static

from models import SessionUser


class DashboardScreen(Screen):
    """Main dashboard with sidebar navigation."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("q", "logout", "Logout"),
    ]

    def __init__(self) -> None:
        self.user: SessionUser | None = None
        super().__init__()

    def on_mount(self) -> None:
        """Load user data when screen is mounted."""
        self.user = getattr(self.app, "current_user", None)
        self._update_sidebar()

    def _update_sidebar(self) -> None:
        """Update sidebar with user info and menu."""
        user_label = self.query_one(".sidebar-user", Label)
        if self.user:
            user_label.update(f"{self.user.name} ({self.user.role})")

        # Show/hide admin-only buttons based on role
        is_admin = self.user and self.user.role == "Admin"
        is_customer = self.user and self.user.role == "Customer"
        is_specialist = self.user and self.user.role == "Specialist"

        users_btn = self.query_one("#btn-users", Button)
        users_btn.display = is_admin

        # Update welcome text based on role
        nav_products = self.query_one("#nav-products", Label)
        nav_orders = self.query_one("#nav-orders", Label)
        nav_services = self.query_one("#nav-services", Label)
        nav_users = self.query_one("#nav-users", Label)

        if is_customer:
            nav_products.update("• Products - Browse product catalog (view only)")
            nav_orders.update("• Orders - View and manage your orders")
            nav_services.update("• Service Requests - View your service requests")
            nav_users.display = False
        elif is_specialist:
            nav_products.update("• Products - Browse product catalog (view only)")
            nav_orders.update("• Orders - View all orders")
            nav_services.update("• Service Requests - Manage assigned requests")
            nav_users.display = False
        else:
            # Admin sees all
            nav_products.update("• Products - Manage product catalog")
            nav_orders.update("• Orders - View and manage all orders")
            nav_services.update("• Service Requests - Manage all service requests")
            nav_users.display = True

    def compose(self) -> ComposeResult:
        # Sidebar
        with Container(classes="sidebar"):
            yield Label("CTRL Market", classes="sidebar-title")
            yield Label("User", classes="sidebar-user")
            yield Static("─" * 18)

            with Container(classes="sidebar-menu"):
                yield Button("Products", id="btn-products", classes="sidebar-button")
                yield Button("Orders", id="btn-orders", classes="sidebar-button")
                yield Button(
                    "Service Requests", id="btn-services", classes="sidebar-button"
                )
                yield Button("Users", id="btn-users", classes="sidebar-button")
                yield Static("")
                yield Button("Logout", id="btn-logout", variant="error")

        # Main content area - will be updated based on role
        with Container(classes="main-content"):
            yield Label("Welcome to CTRL Market", classes="content-title")
            yield Label("Smart Equipment Sales & Services Platform")
            yield Static("")
            yield Label("Use the sidebar to navigate:", id="nav-label")
            yield Label("• Products - Browse product catalog", id="nav-products")
            yield Label("• Orders - View and manage orders", id="nav-orders")
            yield Label(
                "• Service Requests - Manage service requests", id="nav-services"
            )
            yield Label("• Users - User management (Admin only)", id="nav-users")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle sidebar button presses."""
        button_id = event.button.id

        if button_id == "btn-products":
            self.app.push_screen("products")
        elif button_id == "btn-orders":
            self.app.push_screen("orders")
        elif button_id == "btn-services":
            self.app.push_screen("services")
        elif button_id == "btn-users":
            if self.user and self.user.role == "Admin":
                self.app.push_screen("users")
        elif button_id == "btn-logout":
            self.action_logout()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.current_user = None
        self.app.pop_screen()
