"""New product creation screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Input, Label

from database.queries import create_product
from models import ProductCreate
from tui.dialogs import ShortcutsBar


class ProductNewScreen(Screen):
    """Create new product screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("ctrl+enter", "create_product", "Create Product"),
        ("q", "logout", "Logout"),
    ]

    def compose(self) -> ComposeResult:
        with Container(classes="screen-layout"):
            with Container(classes="workspace-header"):
                yield Label("CTRL Market - New Product", classes="workspace-title")

            with Container(classes="workspace-content"):
                with Container(classes="form-container"):
                    yield Label("Create New Product", classes="form-title")

                    yield Label(
                        "Access Denied: Only Admins and Specialists can create products.",
                        id="access-denied",
                        classes="login-error",
                    )

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

            yield ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")

    def on_mount(self) -> None:
        """Check permissions when screen mounts."""
        current_user = getattr(self.app, "current_user", None)

        if not current_user or current_user.role not in ("Specialist", "Admin"):
            self.query_one("#form-content", Container).display = False
            self.query_one("#access-denied", Label).display = True
        else:
            self.query_one("#form-content", Container).display = True
            self.query_one("#access-denied", Label).display = False

        shortcuts_bar = self.query_one("#shortcuts-bar", ShortcutsBar)
        shortcuts_bar.shortcuts = (
            "\\[Ctrl+Enter]Create Product  \\[Esc]Back  \\[q]Logout"
        )

    def action_create_product(self) -> None:
        """Create the product."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role not in ("Specialist", "Admin"):
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
        self.app.logout()
