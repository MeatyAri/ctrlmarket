"""Unified workspace screen with tabbed interface for Products, Orders, and Services."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Input,
    Label,
    Select,
    TabbedContent,
    TabPane,
)

from database.queries import (
    assign_specialist,
    cancel_order,
    delete_product,
    get_order_by_id,
    get_product_by_id,
    get_service_request_by_id,
    list_orders,
    list_product_categories,
    list_products,
    list_service_requests,
    list_service_requests_for_specialist,
    update_order_status,
    update_service_request_status,
)
from models import OrderUpdateStatus, ServiceRequestUpdateStatus
from tui.dialogs import ConfirmDialog, ShortcutsBar
from tui.screens.product_edit import ProductEditScreen


class WorkspaceScreen(Screen):
    """Unified workspace with Products, Orders, and Services tabs."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("alt+1", "switch_tab('products')", "Products"),
        ("alt+2", "switch_tab('orders')", "Orders"),
        ("alt+3", "switch_tab('services')", "Services"),
        ("alt+4", "go_profile", "Profile"),
        ("escape", "go_back", "Back"),
        ("q", "logout", "Logout"),
        ("n", "new_item", "New"),
        ("e", "edit_item", "Edit"),
        ("d", "delete_item", "Delete"),
        ("r", "refresh", "Refresh"),
        ("x", "cancel_item", "Cancel"),
        ("c", "complete_item", "Complete"),
        ("a", "assign_request", "Assign"),
        ("ctrl+s", "focus_search", "Focus Search"),
        ("/", "focus_search", "Focus Search"),
    ]

    def __init__(self, initial_tab: str = "products") -> None:
        self.products: list = []
        self.orders: list = []
        self.requests: list = []
        self.categories: list[str] = []
        self.selected_product_id: int | None = None
        self.selected_order_id: int | None = None
        self.selected_request_id: int | None = None
        self.current_status_filter: str | None = None
        self._initial_tab = initial_tab
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="screen-layout"):
            with Container(classes="workspace-header"):
                yield Label("CTRL Market - Workspace", classes="workspace-title")

            with Container(classes="workspace-content"):
                with TabbedContent(initial=self._initial_tab):
                    with TabPane("Products \\[1]", id="products"):
                        with Container(classes="tab-pane-container"):
                            with Container(classes="search-container"):
                                yield Input(
                                    placeholder="Search products... (Press Enter to search)",
                                    id="products-search",
                                    classes="search-input",
                                )
                                yield Select(
                                    [(c, c) for c in ["All Categories"]],
                                    id="products-category",
                                    classes="search-select",
                                )

                            table = DataTable(id="products-table")
                            table.add_columns("ID", "Name", "Category", "Price")
                            table.cursor_type = "row"
                            yield table

                    with TabPane("Orders \\[2]", id="orders"):
                        with Container(classes="tab-pane-container"):
                            with Container(classes="search-container"):
                                yield Input(
                                    placeholder="Search by customer name or order ID...",
                                    id="orders-search",
                                    classes="search-input",
                                )
                                yield Select(
                                    [
                                        ("All Statuses", None),
                                        ("Pending", "Pending"),
                                        ("Completed", "Completed"),
                                        ("Cancelled", "Cancelled"),
                                    ],
                                    value=None,
                                    id="orders-status",
                                    classes="search-select",
                                )

                            table = DataTable(id="orders-table")
                            table.add_columns(
                                "ID", "Date", "Customer", "Total", "Items", "Status"
                            )
                            table.cursor_type = "row"
                            yield table

                    with TabPane("Services \\[3]", id="services"):
                        with Container(classes="tab-pane-container"):
                            with Container(classes="search-container"):
                                yield Input(
                                    placeholder="Search by customer name or service type...",
                                    id="services-search",
                                    classes="search-input",
                                )
                                yield Select(
                                    [
                                        ("All Statuses", ""),
                                        ("Pending", "Pending"),
                                        ("In Progress", "In Progress"),
                                        ("Completed", "Completed"),
                                        ("Cancelled", "Cancelled"),
                                    ],
                                    value="",
                                    id="services-status",
                                    classes="search-select",
                                )

                            table = DataTable(id="services-table")
                            table.add_columns(
                                "ID", "Date", "Type", "Status", "Customer", "Specialist"
                            )
                            table.cursor_type = "row"
                            yield table

            yield ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")

    def on_mount(self) -> None:
        """Load data when screen mounts."""
        self._load_categories()
        self._load_products()
        self._load_orders()
        self._load_requests()
        self._update_ui_for_role()
        self._update_shortcuts()

    def _update_ui_for_role(self) -> None:
        """Update UI based on user role."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        _ = current_user.role

    def _update_shortcuts(self) -> None:
        """Update shortcuts bar based on current tab and role."""
        current_user = getattr(self.app, "current_user", None)
        is_customer = current_user and current_user.role == "Customer"
        is_specialist = current_user and current_user.role == "Specialist"

        # Get active tab
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active

        shortcuts = []
        shortcuts.append(
            "\\[Alt+1]Products \\[Alt+2]Orders \\[Alt+3]Services \\[Alt+4]Profile"
        )
        shortcuts.append("\\[Esc]Back \\[/]Search")

        if active_tab == "products":
            if not is_customer:
                shortcuts.append("\\[n]New \\[e]Edit \\[d]Delete")
            shortcuts.append("\\[r]Refresh")
        elif active_tab == "orders":
            if not is_specialist:
                shortcuts.append("\\[n]New")
            if not is_customer:
                shortcuts.append("\\[c]Complete")
            if not is_specialist:
                shortcuts.append("\\[x]Cancel")
            shortcuts.append("\\[r]Refresh")
        elif active_tab == "services":
            if not is_specialist:
                shortcuts.append("\\[n]New")
            if is_specialist:
                shortcuts.append("\\[c]Complete \\[a]Assign")
            elif not is_customer:
                shortcuts.append("\\[c]Complete")
            shortcuts.append("\\[r]Refresh")

        shortcuts_bar = self.query_one("#shortcuts-bar", ShortcutsBar)
        shortcuts_bar.shortcuts = "  |  ".join(shortcuts)

    def _load_categories(self) -> None:
        """Load product categories for dropdown."""
        self.categories = ["All Categories"] + list_product_categories()
        select = self.query_one("#products-category", Select)
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

    def _load_orders(self, search: str = "") -> None:
        """Load orders into table."""
        table = self.query_one("#orders-table", DataTable)
        table.clear()

        current_user = getattr(self.app, "current_user", None)
        user_id = None
        if current_user and current_user.role == "Customer":
            user_id = current_user.user_id

        self.orders = list_orders(
            user_id=user_id,
            status=self.current_status_filter,
            search=search if search else None,
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

    def _load_requests(self, status: str = "", search: str = "") -> None:
        """Load service requests based on user role."""
        table = self.query_one("#services-table", DataTable)
        table.clear()

        current_user = getattr(self.app, "current_user", None)
        status_filter = status if status else None

        if current_user:
            if current_user.role == "Customer":
                self.requests = list_service_requests(
                    status=status_filter,
                    customer_id=current_user.user_id,
                    search=search if search else None,
                )
            elif current_user.role == "Specialist":
                self.requests = list_service_requests_for_specialist(
                    current_user.user_id
                )
                if status_filter:
                    self.requests = [
                        r for r in self.requests if r.status == status_filter
                    ]
            else:
                self.requests = list_service_requests(
                    status=status_filter, search=search if search else None
                )
        else:
            self.requests = []

        for req in self.requests:
            specialist = req.specialist_name or "Unassigned"
            table.add_row(
                str(req.request_id),
                str(req.request_date)[:16] if req.request_date else "",
                req.service_type,
                req.status,
                req.customer_name,
                specialist,
            )

    def _get_selected_id_from_table(self, table_id: str) -> int | None:
        """Get ID from currently highlighted row in specified table."""
        table = self.query_one(f"#{table_id}", DataTable)
        if table.cursor_row is None:
            return None
        try:
            row_data = table.get_row_at(table.cursor_row)
            return int(row_data[0])
        except (IndexError, ValueError):
            return None

    def _get_selected_product_id(self) -> int | None:
        """Get product ID from currently highlighted row."""
        return self._get_selected_id_from_table("products-table")

    def _get_selected_order_id(self) -> int | None:
        """Get order ID from currently highlighted row."""
        return self._get_selected_id_from_table("orders-table")

    def _get_selected_request_id(self) -> int | None:
        """Get request ID from currently highlighted row."""
        return self._get_selected_id_from_table("services-table")

    @on(DataTable.RowHighlighted, "#products-table")
    def on_products_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track cursor movement in products table."""
        self.selected_product_id = self._get_selected_product_id()

    @on(DataTable.RowHighlighted, "#orders-table")
    def on_orders_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track cursor movement in orders table."""
        self.selected_order_id = self._get_selected_order_id()

    @on(DataTable.RowHighlighted, "#services-table")
    def on_services_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track cursor movement in services table."""
        self.selected_request_id = self._get_selected_request_id()

    def on_tabbed_content_tab_activated(self) -> None:
        """Update shortcuts when tab changes."""
        self._update_shortcuts()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "products-search":
            search = event.value
            category_select = self.query_one("#products-category", Select)
            category = (
                str(category_select.value)
                if category_select.value != Select.BLANK
                else ""
            )
            self._load_products(search=search, category=category)
        elif event.input.id == "orders-search":
            search = event.value
            self._load_orders(search=search)
        elif event.input.id == "services-search":
            search = event.value
            status_select = self.query_one("#services-status", Select)
            status = (
                str(status_select.value) if status_select.value != Select.BLANK else ""
            )
            self._load_requests(status=status, search=search)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter changes."""
        if event.select.id == "orders-status":
            selected_value = event.value
            if selected_value is None or str(selected_value) == "NoSelection":
                self.current_status_filter = None
            else:
                self.current_status_filter = (
                    str(selected_value) if selected_value else None
                )
            self._load_orders()
        elif event.select.id == "services-status":
            value = event.value
            status = str(value) if value != Select.BLANK else ""
            self._load_requests(status=status)

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to specified tab."""
        tabbed = self.query_one(TabbedContent)
        tabbed.active = tab_id

    def action_go_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()

    def action_go_profile(self) -> None:
        """Go to profile screen."""
        self.app.push_screen("profile")

    def action_focus_search(self) -> None:
        """Focus the search input of current tab."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active

        if active_tab == "products":
            search_input = self.query_one("#products-search", Input)
            search_input.focus()
        elif active_tab == "orders":
            search_input = self.query_one("#orders-search", Input)
            search_input.focus()
        elif active_tab == "services":
            search_input = self.query_one("#services-search", Input)
            search_input.focus()

    def action_new_item(self) -> None:
        """Create new item based on current tab."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active

        current_user = getattr(self.app, "current_user", None)
        is_specialist = current_user and current_user.role == "Specialist"

        if active_tab == "products":
            if not current_user or current_user.role == "Customer":
                return
            self.app.push_screen("product_new")
        elif active_tab == "orders":
            if is_specialist:
                return
            self.app.push_screen("order_new")
        elif active_tab == "services":
            if is_specialist:
                return
            self.app.push_screen("service_new")

    def action_edit_item(self) -> None:
        """Edit selected item."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active

        if active_tab == "products" and self.selected_product_id:
            current_user = getattr(self.app, "current_user", None)
            if not current_user or current_user.role == "Customer":
                return
            self.app.push_screen(ProductEditScreen(self.selected_product_id))

    def action_delete_item(self) -> None:
        """Delete selected item."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active

        if active_tab == "products" and self.selected_product_id:
            current_user = getattr(self.app, "current_user", None)
            if not current_user or current_user.role == "Customer":
                return

            product_id = self.selected_product_id
            product = get_product_by_id(product_id)
            if not product:
                return

            def confirm_delete(confirmed: bool) -> None:
                if confirmed:
                    if delete_product(product_id):
                        self._load_products()
                        self.selected_product_id = None

            # Use a simple confirmation approach
            self.app.push_screen(
                ConfirmDialog(
                    title="Confirm Delete",
                    message=f"Delete product '{product.name}'?",
                    on_confirm=confirm_delete,
                )
            )

    def action_refresh(self) -> None:
        """Refresh current tab data."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active

        if active_tab == "products":
            self._load_products()
        elif active_tab == "orders":
            self._load_orders()
        elif active_tab == "services":
            self._load_requests()

    def action_cancel_item(self) -> None:
        """Cancel selected item based on context."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active
        current_user = getattr(self.app, "current_user", None)

        if not current_user:
            return

        if active_tab == "orders" and self.selected_order_id:
            self._handle_order_cancel(current_user)
        elif active_tab == "services" and self.selected_request_id:
            self._handle_service_cancel(current_user)

    def action_complete_item(self) -> None:
        """Complete selected item based on context."""
        tabbed = self.query_one(TabbedContent)
        active_tab = tabbed.active
        current_user = getattr(self.app, "current_user", None)

        if not current_user:
            return

        if active_tab == "orders" and self.selected_order_id:
            self._handle_order_complete(current_user)
        elif active_tab == "services" and self.selected_request_id:
            self._handle_service_complete(current_user)

    def _handle_order_cancel(self, current_user) -> None:
        """Cancel selected order."""
        order_id = self.selected_order_id
        if order_id is None:
            return

        order = get_order_by_id(order_id)
        if not order:
            return

        if current_user.role == "Customer":
            if order.user_id != current_user.user_id or order.status != "Pending":
                return
            if cancel_order(order_id):
                self._load_orders()
                self.selected_order_id = None
        elif current_user.role in ["Specialist", "Admin"]:
            if order.status != "Pending":
                return
            if cancel_order(order_id):
                self._load_orders()
                self.selected_order_id = None

    def _handle_order_complete(self, current_user) -> None:
        """Complete selected order."""
        order_id = self.selected_order_id
        if order_id is None:
            return

        order = get_order_by_id(order_id)
        if not order:
            return

        if current_user.role not in ["Specialist", "Admin"]:
            return
        if order.status != "Pending":
            return
        update = OrderUpdateStatus(status="Completed")
        if update_order_status(order_id, update):
            self._load_orders()
            self.selected_order_id = None

    def _handle_service_cancel(self, current_user) -> None:
        """Cancel selected service request."""
        request_id = self.selected_request_id
        if request_id is None:
            self.notify("No service request selected", severity="error")
            return

        if current_user.role not in ("Specialist", "Admin"):
            self.notify("Permission denied", severity="error")
            return

        request = get_service_request_by_id(request_id)
        if not request:
            self.notify("Service request not found", severity="error")
            return

        if request.status not in ("Pending", "In Progress"):
            self.notify(
                "Can only cancel Pending or In Progress requests", severity="error"
            )
            return
        success = update_service_request_status(
            request_id, ServiceRequestUpdateStatus(status="Cancelled")
        )
        if success:
            self.notify("Service request cancelled", severity="information")
        else:
            self.notify("Failed to cancel service request", severity="error")
        self._load_requests()
        self.selected_request_id = None

    def _handle_service_complete(self, current_user) -> None:
        """Complete selected service request."""
        request_id = self.selected_request_id
        if request_id is None:
            self.notify("No service request selected", severity="error")
            return

        if current_user.role not in ("Specialist", "Admin"):
            self.notify("Permission denied", severity="error")
            return

        request = get_service_request_by_id(request_id)
        if not request:
            self.notify("Service request not found", severity="error")
            return

        if request.status not in ("Pending", "In Progress"):
            self.notify(
                "Can only complete Pending or In Progress requests",
                severity="error",
            )
            return
        success = update_service_request_status(
            request_id, ServiceRequestUpdateStatus(status="Completed")
        )
        if success:
            self.notify("Service request completed", severity="information")
        else:
            self.notify("Failed to complete service request", severity="error")
        self._load_requests()
        self.selected_request_id = None

    def action_assign_request(self) -> None:
        """Assign service request to current specialist."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role != "Specialist":
            return

        if self.selected_request_id:
            assign_specialist(self.selected_request_id, current_user.user_id)
            self._load_requests()
