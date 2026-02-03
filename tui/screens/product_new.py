"""New product creation screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Label, Static

from database.queries import create_product
from models import ProductCreate


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class ProductNewScreen(Screen):
    """Create new product screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("c", "create_product", "Create"),
        ("q", "logout", "Logout"),
    ]

    def compose(self) -> ComposeResult:
        # Header
        with Container(classes="workspace-header"):
            yield Label("CTRL Market - New Product", classes="workspace-title")

        # Main content
        with Container(classes="workspace-content"):
            with Container(classes="form-container"):
                yield Label("Create New Product", classes="form-title")

                # Access denied message (hidden by default)
                yield Label(
                    "Access Denied: Only Admins and Specialists can create products.",
                    id="access-denied",
                    classes="login-error",
                )

                # Form container
                with Container(id="form-content"):
                    with Horizontal(classes="form-row"):
                        yield Label("Name:", classes="form-label")
                        yield Input(placeholder="Product name", id="name")

                    with Horizontal(classes="form-row"):
                        yield Label("Category:", classes="form-label")
                        yield Input(placeholder="Category", id="category")

                    with Horizontal(classes="form-row"):
                        yield Label("Price:", classes="form-label")
                        yield Input(placeholder="0.00", id="price")

        # Shortcuts bar
        shortcuts_bar = ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")
        shortcuts_bar.shortcuts = "\[Esc]Back \[c]Create Product"
        yield shortcuts_bar

    def on_mount(self) -> None:
        """Check permissions when screen mounts."""
        current_user = getattr(self.app, "current_user", None)

        if not current_user or current_user.role == "Customer":
            # Customers cannot access this screen
            self.query_one("#form-content", Container).display = False
            self.query_one("#access-denied", Label).display = True
        else:
            # Admins and specialists can create products
            self.query_one("#form-content", Container).display = True
            self.query_one("#access-denied", Label).display = False

    def action_create_product(self) -> None:
        """Create the product."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role == "Customer":
            return

        name = self.query_one("#name", Input).value.strip()
        category = self.query_one("#category", Input).value.strip()
        price_str = self.query_one("#price", Input).value.strip()

        if not all([name, category, price_str]):
            return

        try:
            price = float(price_str)
            if price < 0:
                return
        except ValueError:
            return

        product = ProductCreate(name=name, category=category, price=price)

        try:
            create_product(product)
            self.app.pop_screen()
        except Exception:
            pass

    def action_go_back(self) -> None:
        """Go back."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.current_user = None
        while len(self.app.screen_stack) > 1:
            self.app.pop_screen()
        self.app.switch_screen("login")
