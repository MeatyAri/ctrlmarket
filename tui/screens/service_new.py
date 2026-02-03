"""New service request screen."""

from typing import Literal

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Label, Select, Static

from database.queries import create_service_request, list_customers
from models import ServiceRequestCreate


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class ServiceNewScreen(Screen):
    """Create new service request screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("q", "logout", "Logout"),
        ("ctrl+enter", "create_service", "Submit"),
    ]

    def __init__(self) -> None:
        self.current_user = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="screen-layout"):
            # Header
            with Container(classes="workspace-header"):
                yield Label(
                    "CTRL Market - New Service Request", classes="workspace-title"
                )

            # Main content
            with Container(classes="workspace-content"):
                with Container(classes="form-container"):
                    yield Label("Create Service Request", classes="form-title")

                    # Customer selection (hidden for customers)
                    with Horizontal(classes="form-row"):
                        yield Label(
                            "Customer:", classes="form-label", id="customer-label"
                        )
                        yield Select([], id="customer-select")

                    with Horizontal(classes="form-row"):
                        yield Label("Service Type:", classes="form-label")
                        yield Select(
                            [
                                ("Installation", "Installation"),
                                ("Support", "Support"),
                            ],
                            id="service-type",
                            value="Installation",
                        )

            # Shortcuts bar
            shortcuts_bar = ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")
            shortcuts_bar.shortcuts = "\\[Esc]Back \\[ctrl+enter]Submit"
            yield shortcuts_bar

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields."""
        self.action_create_service()

    def on_mount(self) -> None:
        """Load customers when screen mounts."""
        self.current_user = getattr(self.app, "current_user", None)
        self._setup_customer_selection()

    def _setup_customer_selection(self) -> None:
        """Setup customer selection based on user role."""
        customer_select = self.query_one("#customer-select", Select)
        customer_label = self.query_one("#customer-label", Label)

        if self.current_user and self.current_user.role == "Customer":
            # Customers can only create requests for themselves
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

    def action_create_service(self) -> None:
        """Create the service request."""
        customer_select = self.query_one("#customer-select", Select)
        service_type_select = self.query_one("#service-type", Select)

        if customer_select.value == Select.BLANK:
            return

        customer_id = int(str(customer_select.value))

        # Get service type with proper typing
        service_type_value = service_type_select.value
        if service_type_value == Select.BLANK:
            service_type: Literal["Installation", "Support"] = "Installation"
        else:
            service_type_str = str(service_type_value)
            if service_type_str not in ("Installation", "Support"):
                return
            service_type = service_type_str  # type: ignore[assignment]

        request = ServiceRequestCreate(
            service_type=service_type,
            customer_id=customer_id,
        )

        try:
            create_service_request(request)
            self.app.pop_screen()
        except Exception:
            pass

    def action_go_back(self) -> None:
        """Go back."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()
