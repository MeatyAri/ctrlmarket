"""New product creation screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from database.queries import create_product
from models import ProductCreate


class ProductNewScreen(Screen):
    """Create new product screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        with Container(classes="form-container"):
            yield Label("Create New Product", classes="form-title")

            # Access denied message (hidden by default)
            yield Label(
                "Access Denied: Only Admins and Specialists can create products.",
                id="access-denied",
                classes="error-message",
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

                with Horizontal(classes="form-buttons"):
                    yield Button("Cancel", id="btn-cancel")
                    yield Button("Create", id="btn-create", variant="primary")

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-cancel":
            self.action_go_back()
        elif btn_id == "btn-create":
            self._handle_create()

    def _handle_create(self) -> None:
        """Create the product."""
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
