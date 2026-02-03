"""Service requests management screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Select, Static

from database.queries import (
    assign_specialist,
    list_service_requests,
    list_service_requests_for_specialist,
    update_service_request_status,
)
from models import ServiceRequestUpdateStatus


class ServicesScreen(Screen):
    """Service requests management screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("n", "new_request", "New Request"),
        ("q", "logout", "Logout"),
    ]

    def __init__(self) -> None:
        self.requests: list = []
        self.selected_request_id: int | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="sidebar"):
            yield Label("Services", classes="sidebar-title")
            yield Static("─" * 18)
            with Container(classes="sidebar-menu"):
                yield Button("Back", id="btn-back", classes="sidebar-button")
                yield Button("Refresh", id="btn-refresh", classes="sidebar-button")
                yield Button("New Request", id="btn-new", variant="primary")
                yield Static("")
                yield Button("Assign to Me", id="btn-assign", variant="primary")
                yield Button("Complete", id="btn-complete", variant="success")
                yield Button("Cancel", id="btn-cancel", variant="error")

        with Container(classes="main-content"):
            yield Label("Service Requests", classes="content-title")

            # Filter
            with Horizontal(classes="search-container"):
                yield Input(
                    placeholder="Search by customer name or service type...",
                    id="search-input",
                    classes="search-input",
                )
                yield Label("Filter:", classes="form-label")
                yield Select(
                    [
                        ("All", ""),
                        ("Pending", "Pending"),
                        ("In Progress", "In Progress"),
                        ("Completed", "Completed"),
                        ("Cancelled", "Cancelled"),
                    ],
                    id="status-filter",
                    value="",
                )
                yield Button("Search", id="btn-search", classes="search-button")

            # Requests table
            table = DataTable(id="requests-table")
            table.add_columns("ID", "Date", "Type", "Status", "Customer", "Specialist")
            table.cursor_type = "row"
            yield table

    def on_mount(self) -> None:
        """Load requests when screen mounts."""
        self._update_ui_for_role()
        self._load_requests()

    def _update_ui_for_role(self) -> None:
        """Update UI based on user role."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        is_customer = current_user.role == "Customer"
        is_specialist = current_user.role == "Specialist"

        if is_customer:
            # Customers can only view their own requests and create new ones
            self.query_one("#btn-assign", Button).display = False
            self.query_one("#btn-complete", Button).display = False
            self.query_one("#btn-cancel", Button).display = False
        elif is_specialist:
            # Specialists can manage requests but not create new ones
            self.query_one("#btn-new", Button).display = False

    def _load_requests(self, status: str = "", search: str = "") -> None:
        """Load service requests based on user role."""
        table = self.query_one("#requests-table", DataTable)
        table.clear()

        current_user = getattr(self.app, "current_user", None)
        status_filter = status if status else None

        # Filter requests based on role
        if current_user:
            if current_user.role == "Customer":
                # Customers only see their own requests
                self.requests = list_service_requests(
                    status=status_filter,
                    customer_id=current_user.user_id,
                    search=search if search else None,
                )
            elif current_user.role == "Specialist":
                # Specialists see unassigned and their assigned requests
                self.requests = list_service_requests_for_specialist(
                    current_user.user_id
                )
                # Apply status filter manually for specialists
                if status_filter:
                    self.requests = [
                        r for r in self.requests if r.status == status_filter
                    ]
            else:
                # Admins see all requests
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

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        row_data = event.data_table.get_row(event.row_key)
        self.selected_request_id = int(row_data[0])

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter change."""
        if event.select.id == "status-filter":
            value = event.value
            status = str(value) if value != Select.BLANK else ""
            self._load_requests(status=status)

    def _handle_search(self) -> None:
        """Apply search filter."""
        search = self.query_one("#search-input", Input).value
        status_filter = self.query_one("#status-filter", Select)
        status = str(status_filter.value) if status_filter.value != Select.BLANK else ""
        self._load_requests(status=status, search=search)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-back":
            self.action_go_back()
        elif btn_id == "btn-refresh":
            self._load_requests()
        elif btn_id == "btn-new":
            self.action_new_request()
        elif btn_id == "btn-assign":
            self._handle_assign()
        elif btn_id == "btn-complete":
            self._handle_complete()
        elif btn_id == "btn-cancel":
            self._handle_cancel()
        elif btn_id == "btn-search":
            self._handle_search()

    def _handle_assign(self) -> None:
        """Assign request to current user (specialist)."""
        if not self.selected_request_id:
            return

        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role != "Specialist":
            return

        assign_specialist(self.selected_request_id, current_user.user_id)
        self._load_requests()

    def _handle_complete(self) -> None:
        """Mark request as completed."""
        if not self.selected_request_id:
            return

        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        # Only specialists and admins can complete requests
        if current_user.role not in ("Specialist", "Admin"):
            return

        update_service_request_status(
            self.selected_request_id, ServiceRequestUpdateStatus(status="Completed")
        )
        self._load_requests()

    def _handle_cancel(self) -> None:
        """Cancel request."""
        if not self.selected_request_id:
            return

        current_user = getattr(self.app, "current_user", None)
        if not current_user:
            return

        # Only specialists and admins can cancel requests
        if current_user.role not in ("Specialist", "Admin"):
            return

        update_service_request_status(
            self.selected_request_id, ServiceRequestUpdateStatus(status="Cancelled")
        )
        self._load_requests()

    def action_go_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()

    def action_new_request(self) -> None:
        """Open new request dialog."""
        self.app.push_screen("service_new")
