"""Products management screen."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Select, Static

from database.queries import (
    delete_product,
    get_product_by_id,
    list_product_categories,
    list_products,
)


class ProductsScreen(Screen):
    """Products management screen with search and CRUD."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("n", "new_product", "New Product"),
        ("q", "logout", "Logout"),
    ]

    def __init__(self) -> None:
        self.products: list = []
        self.categories: list[str] = []
        self.selected_product_id: int | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="sidebar"):
            yield Label("Products", classes="sidebar-title")
            yield Static("─" * 18)
            with Container(classes="sidebar-menu"):
                yield Button("Back", id="btn-back", classes="sidebar-button")
                yield Button("Refresh", id="btn-refresh", classes="sidebar-button")
                yield Button("New Product", id="btn-new", variant="primary")
                yield Button("Edit", id="btn-edit", classes="sidebar-button")
                yield Button("Delete", id="btn-delete", variant="error")

        with Container(classes="main-content"):
            yield Label("Product Catalog", classes="content-title")

            # Search bar
            with Container(classes="search-container"):
                yield Input(
                    placeholder="Search products...",
                    id="search-input",
                    classes="search-input",
                )
                yield Select(
                    [(c, c) for c in ["All Categories"]],
                    id="category-select",
                    classes="search-input",
                )
                yield Button("Search", id="btn-search", variant="primary")

            # Products table
            table = DataTable(id="products-table")
            table.add_columns("ID", "Name", "Category", "Price")
            table.cursor_type = "row"
            yield table

    def on_mount(self) -> None:
        """Load data when screen mounts."""
        self._load_categories()
        self._load_products()
        self._update_ui_for_role()

    def _update_ui_for_role(self) -> None:
        """Update UI based on user role."""
        current_user = getattr(self.app, "current_user", None)
        if current_user and current_user.role == "Customer":
            # Customers can only view products
            self.query_one("#btn-new", Button).display = False
            self.query_one("#btn-edit", Button).display = False
            self.query_one("#btn-delete", Button).display = False

    def _load_categories(self) -> None:
        """Load product categories for dropdown."""
        self.categories = ["All Categories"] + list_product_categories()
        select = self.query_one("#category-select", Select)
        select.set_options([(c, c) for c in self.categories])

    def _load_products(self, search: str = "", category: str = "") -> None:
        """Load products into table."""
        table = self.query_one("#products-table", DataTable)
        table.clear()

        cat_filter = None if category in ("", "All Categories") else category
        self.products = list_products(
            category=cat_filter, search=search if search else None
        )

        for product in self.products:
            table.add_row(
                str(product.product_id),
                product.name,
                product.category,
                f"${product.price:.2f}",
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        row_data = event.data_table.get_row(event.row_key)
        self.selected_product_id = int(row_data[0])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-back":
            self.action_go_back()
        elif btn_id == "btn-refresh":
            self._load_products()
        elif btn_id == "btn-new":
            self.action_new_product()
        elif btn_id == "btn-search":
            self._handle_search()
        elif btn_id == "btn-edit":
            self._handle_edit()
        elif btn_id == "btn-delete":
            self._handle_delete()

    def _handle_search(self) -> None:
        """Handle search."""
        search = self.query_one("#search-input", Input).value
        category = self.query_one("#category-select", Select).value
        cat_str = category if category != Select.BLANK else ""
        self._load_products(search=search, category=cat_str)

    def _handle_edit(self) -> None:
        """Handle edit button."""
        if not self.selected_product_id:
            return
        self.app.push_screen(f"product_edit:{self.selected_product_id}")

    def _handle_delete(self) -> None:
        """Handle delete button."""
        if not self.selected_product_id:
            return

        product = get_product_by_id(self.selected_product_id)
        if not product:
            return

        def confirm_delete(confirmed: bool) -> None:
            if confirmed:
                if delete_product(self.selected_product_id):
                    self._load_products()
                    self.selected_product_id = None

        self.app.push_screen(
            "confirm_dialog",
            {
                "title": "Confirm Delete",
                "message": f"Delete product '{product.name}'?",
                "on_confirm": confirm_delete,
            },
        )

    def action_go_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()

    def action_new_product(self) -> None:
        """Open new product dialog."""
        self.app.push_screen("product_new")
