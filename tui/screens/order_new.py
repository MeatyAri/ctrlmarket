"""Order creation screen with multi-product selection."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Select, Static

from database.queries import (
    create_order,
    get_product_by_id,
    list_customers,
    list_products,
)
from models import OrderCreate, OrderItemCreate


class OrderNewScreen(Screen):
    """Create new order with multiple products."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        self.cart: list[
            tuple[int, str, int, float]
        ] = []  # (product_id, name, qty, price)
        self.products: list = []
        self.current_user = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="sidebar"):
            yield Label("New Order", classes="sidebar-title")
            yield Static("─" * 18)
            with Container(classes="sidebar-menu"):
                yield Button("Back", id="btn-back", classes="sidebar-button")
                yield Button("Create Order", id="btn-create", variant="success")

        with Container(classes="main-content"):
            yield Label("Create New Order", classes="content-title")

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
            with Horizontal():
                yield Select([], id="product-select")
                yield Input(placeholder="Qty", id="qty-input", value="1")
                yield Button("Add", id="btn-add", variant="primary")

    def on_mount(self) -> None:
        """Load data when screen mounts."""
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-back":
            self.action_go_back()
        elif btn_id == "btn-add":
            self._handle_add()
        elif btn_id == "btn-create":
            self._handle_create()

    def _handle_add(self) -> None:
        """Add product to cart."""
        product_select = self.query_one("#product-select", Select)
        qty_input = self.query_one("#qty-input", Input)

        if product_select.value == Select.BLANK:
            return

        try:
            qty = int(qty_input.value)
            if qty < 1:
                return
        except ValueError:
            return

        product_id = int(product_select.value)
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

    def _handle_create(self) -> None:
        """Create the order."""
        customer_select = self.query_one("#customer-select", Select)

        if customer_select.value == Select.BLANK:
            return

        if not self.cart:
            return

        customer_id = int(customer_select.value)
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
