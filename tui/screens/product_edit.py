"""Product edit screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Input, Label, Static

from database.queries import get_product_by_id, update_product
from models import ProductUpdate


class ProductEditScreen(Screen):
    """Edit existing product screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("c", "save_product", "Save"),
        ("q", "logout", "Logout"),
    ]

    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        self.product = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="workspace-header"):
            yield Label("CTRL Market - Edit Product", classes="workspace-title")

        with Container(classes="workspace-content"):
            with Container(classes="form-container"):
                yield Label("Edit Product", classes="form-title")

                yield Label(
                    "Access Denied: Only Admins and Specialists can edit products.",
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

        shortcuts_bar = Static(
            "\\[Esc]Back \\[c]Save Product", id="shortcuts-bar", classes="shortcuts-bar"
        )
        yield shortcuts_bar

    def on_mount(self) -> None:
        """Load product data and check permissions."""
        current_user = getattr(self.app, "current_user", None)

        if not current_user or current_user.role not in ("Specialist", "Admin"):
            self.query_one("#form-content", Container).display = False
            self.query_one("#access-denied", Label).display = True
            return

        self.product = get_product_by_id(self.product_id)
        if self.product:
            self.query_one("#name", Input).value = self.product.name
            self.query_one("#category", Input).value = self.product.category
            self.query_one("#price", Input).value = str(self.product.price)

    def action_save_product(self) -> None:
        """Save the product changes."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role not in ("Specialist", "Admin"):
            return

        if not self.product:
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

        update_data = ProductUpdate(
            name=name if name != self.product.name else None,
            category=category if category != self.product.category else None,
            price=price if price != self.product.price else None,
        )

        try:
            if update_product(self.product_id, update_data):
                self.app.pop_screen()
        except Exception:
            pass

    def action_go_back(self) -> None:
        """Go back."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()
