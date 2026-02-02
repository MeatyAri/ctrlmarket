"""New user creation screen."""

import bcrypt
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Select

from database.queries import create_user
from models import UserCreate


class UserNewScreen(Screen):
    """Create new user screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        with Container(classes="form-container"):
            yield Label("Create New User", classes="form-title")

            with Horizontal(classes="form-row"):
                yield Label("Name:", classes="form-label")
                yield Input(placeholder="Full name", id="name")

            with Horizontal(classes="form-row"):
                yield Label("Email:", classes="form-label")
                yield Input(placeholder="Email address", id="email")

            with Horizontal(classes="form-row"):
                yield Label("Phone:", classes="form-label")
                yield Input(placeholder="Phone number", id="phone")

            with Horizontal(classes="form-row"):
                yield Label("Role:", classes="form-label")
                yield Select(
                    [
                        ("Customer", "Customer"),
                        ("Specialist", "Specialist"),
                        ("Admin", "Admin"),
                    ],
                    id="role",
                    value="Customer",
                )

            with Horizontal(classes="form-row"):
                yield Label("Password:", classes="form-label")
                yield Input(placeholder="Password", password=True, id="password")

            with Horizontal(classes="form-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Create", id="btn-create", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-cancel":
            self.action_go_back()
        elif btn_id == "btn-create":
            self._handle_create()

    def _handle_create(self) -> None:
        """Create the user."""
        name = self.query_one("#name", Input).value.strip()
        email = self.query_one("#email", Input).value.strip()
        phone = self.query_one("#phone", Input).value.strip()
        role_select = self.query_one("#role", Select)
        password = self.query_one("#password", Input).value

        if not all([name, email, phone, password]):
            return

        role = (
            str(role_select.value) if role_select.value != Select.BLANK else "Customer"
        )

        # Hash password with bcrypt
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = UserCreate(
            name=name, email=email, phone=phone, role=role, password=password
        )

        try:
            create_user(user, password_hash)
            self.app.pop_screen()
        except Exception:
            pass

    def action_go_back(self) -> None:
        """Go back."""
        self.app.pop_screen()
