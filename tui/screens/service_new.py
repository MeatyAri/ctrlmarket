"""New service request screen."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, Select

from database.queries import create_service_request, list_customers
from models import ServiceRequestCreate


class ServiceNewScreen(Screen):
    """Create new service request screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        self.current_user = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="form-container"):
            yield Label("Create Service Request", classes="form-title")

            # Customer selection (hidden for customers)
            with Horizontal(classes="form-row"):
                yield Label("Customer:", classes="form-label", id="customer-label")
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

            with Horizontal(classes="form-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Create", id="btn-create", variant="primary")

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-cancel":
            self.action_go_back()
        elif btn_id == "btn-create":
            self._handle_create()

    def _handle_create(self) -> None:
        """Create the service request."""
        customer_select = self.query_one("#customer-select", Select)
        service_type_select = self.query_one("#service-type", Select)

        if customer_select.value == Select.BLANK:
            return

        customer_id = int(customer_select.value)
        service_type = (
            str(service_type_select.value)
            if service_type_select.value != Select.BLANK
            else "Installation"
        )

        request = ServiceRequestCreate(
            service_type=service_type, customer_id=customer_id
        )

        try:
            create_service_request(request)
            self.app.pop_screen()
        except Exception:
            pass

    def action_go_back(self) -> None:
        """Go back."""
        self.app.pop_screen()
