"""Products management screen."""

from textual import on
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
from tui.dialogs import ConfirmDialog, ShortcutsBar
from tui.screens.product_edit import ProductEditScreen


class ProductsScreen(Screen):
    """Products management screen with search and CRUD."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("n", "new_product", "New Product"),
        ("e", "edit_product", "Edit Product"),
        ("d", "delete_product", "Delete Product"),
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

            table = DataTable(id="products-table")
            table.add_columns("ID", "Name", "Category", "Price")
            table.cursor_type = "row"
            yield table

        yield ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")

    def on_mount(self) -> None:
        """Load data when screen mounts."""
        self._load_categories()
        self._load_products()
        self._update_ui_for_role()

    def _update_ui_for_role(self) -> None:
        """Update UI based on user role."""
        current_user = getattr(self.app, "current_user", None)
        if current_user and current_user.role == "Customer":
            self.query_one("#btn-new", Button).display = False
            self.query_one("#btn-edit", Button).display = False
            self.query_one("#btn-delete", Button).display = False
        self._update_shortcuts()

    def _update_shortcuts(self) -> None:
        """Update shortcuts bar based on user role."""
        current_user = getattr(self.app, "current_user", None)
        is_customer = current_user and current_user.role == "Customer"

        shortcuts = []
        shortcuts.append("\\[Esc]Back")
        if is_customer:
            shortcuts.append("\\[q]Logout")
        else:
            shortcuts.append("\\[n]New \\[e]Edit \\[d]Delete \\[q]Logout")
        shortcuts.append("\\[r]Refresh")

        shortcuts_bar = self.query_one("#shortcuts-bar", ShortcutsBar)
        shortcuts_bar.shortcuts = "  |  ".join(shortcuts)

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

    def _get_selected_product_id(self) -> int | None:
        """Get product ID from currently highlighted row."""
        table = self.query_one("#products-table", DataTable)
        if table.cursor_row is None:
            return None
        try:
            row_data = table.get_row_at(table.cursor_row)
            return int(row_data[0])
        except (IndexError, ValueError):
            return None

    @on(DataTable.RowHighlighted, "#products-table")
    def on_datatable_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track cursor movement to auto-select highlighted row."""
        self.selected_product_id = self._get_selected_product_id()

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
            self.notify("No product selected", severity="warning")
            return
        self.app.push_screen(ProductEditScreen(self.selected_product_id))

    def _handle_delete(self) -> None:
        """Handle delete button."""
        if not self.selected_product_id:
            self.notify("No product selected", severity="warning")
            return

        product = get_product_by_id(self.selected_product_id)
        if not product:
            self.notify("Product not found", severity="error")
            return

        def confirm_delete(confirmed: bool) -> None:
            if confirmed:
                if delete_product(self.selected_product_id):
                    self.notify(
                        f"Product '{product.name}' deleted successfully",
                        severity="information",
                    )
                    self._load_products()
                    self.selected_product_id = None
                else:
                    self.notify(
                        f"Cannot delete '{product.name}': product is referenced in existing orders",
                        severity="error",
                    )

        self.app.push_screen(
            ConfirmDialog(
                title="Confirm Delete",
                message=f"Delete product '{product.name}'?",
                on_confirm=confirm_delete,
            )
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

    def action_edit_product(self) -> None:
        """Edit selected product."""
        if not self.selected_product_id:
            self.notify("No product selected", severity="warning")
            return
        self.app.push_screen(ProductEditScreen(self.selected_product_id))

    def action_delete_product(self) -> None:
        """Delete selected product."""
        self._handle_delete()
