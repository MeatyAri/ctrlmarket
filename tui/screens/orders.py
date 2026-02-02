"""Orders management screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Label, Select, Static

from database.queries import (
    cancel_order,
    get_order_by_id,
    list_orders,
    update_order_status,
)
from models import OrderUpdateStatus, OrderWithItems


class OrdersScreen(Screen):
    """Orders management screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("n", "new_order", "New Order"),
    ]

    def __init__(self) -> None:
        self.orders: list[OrderWithItems] = []
        self.selected_order_id: int | None = None
        self.current_status_filter: str | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="sidebar"):
            yield Label("Orders", classes="sidebar-title")
            yield Static("─" * 18)
            with Container(classes="sidebar-menu"):
                yield Button("Back", id="btn-back", classes="sidebar-button")
                yield Button("Refresh", id="btn-refresh", classes="sidebar-button")
                yield Button("New Order", id="btn-new", variant="primary")
                yield Button("View Details", id="btn-view", classes="sidebar-button")
                yield Button("Cancel Order", id="btn-cancel", variant="error")
                yield Button("Mark Completed", id="btn-complete", variant="success")

        with Container(classes="main-content"):
            yield Label("Order Management", classes="content-title")

            # Status filter
            with Horizontal(classes="search-container"):
                yield Select(
                    [
                        ("All Statuses", None),
                        ("Pending", "Pending"),
                        ("Completed", "Completed"),
                        ("Cancelled", "Cancelled"),
                    ],
                    value=None,
                    id="status-filter",
                )
                yield Button("Filter", id="btn-filter", classes="search-button")

            # Orders table
            table = DataTable(id="orders-table")
            table.add_columns("ID", "Date", "Customer", "Total", "Items", "Status")
            table.cursor_type = "row"
            yield table

    def on_mount(self) -> None:
        """Load orders when screen mounts."""
        self._update_ui_for_role()
        self._load_orders()

    def _update_ui_for_role(self) -> None:
        """Update UI based on user role."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        is_customer = current_user.role == "Customer"
        is_specialist = current_user.role == "Specialist"
        is_admin = current_user.role == "Admin"

        if is_customer:
            # Customers can view their own orders, create new ones, and cancel them
            # Hide Mark Completed button for customers
            self.query_one("#btn-complete", Button).display = False
        elif is_specialist:
            # Specialists can view all orders and mark them as completed
            # Cannot create or cancel orders
            self.query_one("#btn-new", Button).display = False
            self.query_one("#btn-cancel", Button).display = False
        elif is_admin:
            # Admins have full access - all buttons visible
            pass

    def _load_orders(self) -> None:
        """Load orders into table."""
        table = self.query_one("#orders-table", DataTable)
        table.clear()

        current_user = getattr(self.app, "current_user", None)

        # Filter orders based on role and status filter
        user_id = None
        if current_user and current_user.role == "Customer":
            # Customers only see their own orders
            user_id = current_user.user_id

        self.orders = list_orders(
            user_id=user_id,
            status=self.current_status_filter,
        )

        for order in self.orders:
            item_count = len(order.items)
            table.add_row(
                str(order.order_id),
                str(order.order_date)[:16] if order.order_date else "",
                order.customer_name or "Unknown",
                f"${order.total_price:.2f}" if order.total_price else "$0.00",
                f"{item_count} items",
                order.status,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        row_data = event.data_table.get_row(event.row_key)
        self.selected_order_id = int(row_data[0])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-back":
            self.action_go_back()
        elif btn_id == "btn-refresh":
            self._load_orders()
        elif btn_id == "btn-new":
            self.action_new_order()
        elif btn_id == "btn-view":
            self._handle_view()
        elif btn_id == "btn-cancel":
            self._handle_cancel()
        elif btn_id == "btn-complete":
            self._handle_complete()
        elif btn_id == "btn-filter":
            self._handle_filter()

    def _handle_filter(self) -> None:
        """Apply status filter."""
        status_filter = self.query_one("#status-filter", Select)
        selected_value = status_filter.value
        # Handle NoSelection case
        if selected_value is None or str(selected_value) == "NoSelection":
            self.current_status_filter = None
        else:
            self.current_status_filter = str(selected_value) if selected_value else None
        self._load_orders()

    def _handle_view(self) -> None:
        """View order details."""
        if self.selected_order_id:
            self.app.push_screen(f"order_view:{self.selected_order_id}")

    def _handle_cancel(self) -> None:
        """Cancel selected order (customers can only cancel their own pending orders)."""
        if not self.selected_order_id:
            return

        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        # Check if customer is cancelling their own order
        if current_user.role == "Customer":
            order = get_order_by_id(self.selected_order_id)
            if not order or order.user_id != current_user.user_id:
                return  # Can't cancel other users' orders
            if order.status != "Pending":
                return  # Can only cancel pending orders

        if cancel_order(self.selected_order_id):
            self._load_orders()
            self.selected_order_id = None

    def _handle_complete(self) -> None:
        """Mark selected order as completed (specialists/admins only)."""
        if not self.selected_order_id:
            return

        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        # Only specialists and admins can mark orders as completed
        if current_user.role not in ["Specialist", "Admin"]:
            return

        order = get_order_by_id(self.selected_order_id)
        if not order or order.status != "Pending":
            return  # Can only complete pending orders

        update = OrderUpdateStatus(status="Completed")
        if update_order_status(self.selected_order_id, update):
            self._load_orders()
            self.selected_order_id = None

    def action_go_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()

    def action_new_order(self) -> None:
        """Open new order screen."""
        self.app.push_screen("order_new")
