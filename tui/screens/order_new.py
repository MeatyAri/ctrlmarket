"""Order creation screen with multi-product selection."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Input, Label, Select, Static

from database.queries import (
    create_order,
    get_product_by_id,
    list_customers,
    list_products,
)
from models import OrderCreate, OrderItemCreate


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class OrderNewScreen(Screen):
    """Create new order with multiple products."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("a", "add_item", "Add to Cart"),
        ("r", "remove_last", "Remove Last"),
        ("q", "logout", "Logout"),
        ("ctrl+enter", "create_order", "Submit"),
    ]

    def __init__(self) -> None:
        self.cart: list[
            tuple[int, str, int, float]
        ] = []  # (product_id, name, qty, price)
        self.products: list = []
        self.current_user = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="screen-layout"):
            # Header
            with Container(classes="workspace-header"):
                yield Label("CTRL Market - New Order", classes="workspace-title")

            # Main content
            with Container(classes="workspace-content"):
                # Customer selection (hidden for customers)
                yield Label("Select Customer:", id="customer-label")
                yield Select([], id="customer-select")

                # Cart display
                with Container(classes="order-cart"):
                    yield Label("Order Items", classes="order-cart-title")
                    cart_table = DataTable(id="cart-table")
                    cart_table.add_columns("Product", "Qty", "Price", "Subtotal")
                    yield cart_table
                    yield Label("Total: $0.00", id="cart-total", classes="order-total")

                # Product selection
                yield Label("Add Products:")
                with Horizontal(classes="search-container"):
                    yield Select([], id="product-select")
                    yield Input(placeholder="Qty", id="qty-input", value="1")

            # Shortcuts bar
            shortcuts_bar = ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")
            shortcuts_bar.shortcuts = (
                "\[Esc]Back \[a]Add to Cart \[r]Remove Last \[ctrl+enter]Submit"
            )
            yield shortcuts_bar

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields."""
        self.action_create_order()

    def on_mount(self) -> None:
        self.current_user = getattr(self.app, "current_user", None)
        self._setup_customer_selection()
        self._load_products()
        self._update_cart()

    def _setup_customer_selection(self) -> None:
        """Setup customer selection based on user role."""
        customer_select = self.query_one("#customer-select", Select)
        customer_label = self.query_one("#customer-label", Label)

        if self.current_user and self.current_user.role == "Customer":
            # Customers can only create orders for themselves
            # Auto-select current user and hide the dropdown
            customer_select.set_options(
                [(f"{self.current_user.name} (You)", self.current_user.user_id)]
            )
            customer_select.value = self.current_user.user_id
            customer_select.display = False
            customer_label.display = False
        else:
            # Admins and specialists can select any customer
            customers = list_customers()
            options = [(f"{c.name} ({c.email})", c.user_id) for c in customers]
            customer_select.set_options(options)

    def _load_products(self) -> None:
        """Load products into dropdown."""
        self.products = list_products()
        select = self.query_one("#product-select", Select)
        options = [(f"{p.name} - ${p.price:.2f}", p.product_id) for p in self.products]
        select.set_options(options)

    def _update_cart(self) -> None:
        """Update cart display."""
        table = self.query_one("#cart-table", DataTable)
        table.clear()

        total = 0.0
        for product_id, name, qty, price in self.cart:
            subtotal = qty * price
            total += subtotal
            table.add_row(name, str(qty), f"${price:.2f}", f"${subtotal:.2f}")

        total_label = self.query_one("#cart-total", Label)
        total_label.update(f"Total: ${total:.2f}")

    def action_add_item(self) -> None:
        """Add product to cart."""
        product_select = self.query_one("#product-select", Select)
        qty_input = self.query_one("#qty-input", Input)

        if product_select.value == Select.BLANK or product_select.value is None:
            return

        try:
            qty = int(qty_input.value)
            if qty < 1:
                return
        except ValueError:
            return

        product_id = int(str(product_select.value))
        product = get_product_by_id(product_id)

        if product:
            # Check if already in cart
            for i, (pid, name, q, p) in enumerate(self.cart):
                if pid == product_id:
                    # Update quantity
                    self.cart[i] = (pid, name, q + qty, p)
                    break
            else:
                # Add new item
                self.cart.append((product_id, product.name, qty, product.price))

            self._update_cart()
            qty_input.value = "1"

    def action_remove_last(self) -> None:
        """Remove last item from cart."""
        if self.cart:
            self.cart.pop()
            self._update_cart()

    def action_create_order(self) -> None:
        """Create the order."""
        customer_select = self.query_one("#customer-select", Select)
        customer_value = customer_select.value

        if customer_value == Select.BLANK or customer_value is None:
            return

        if not self.cart:
            return

        # Extract the actual value from the Select
        if hasattr(customer_value, "value"):
            customer_id = int(customer_value.value)
        else:
            customer_id = int(str(customer_value))
        items = [
            OrderItemCreate(product_id=pid, quantity=qty)
            for pid, _, qty, _ in self.cart
        ]

        try:
            order = create_order(OrderCreate(user_id=customer_id, items=items))
            if order:
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
