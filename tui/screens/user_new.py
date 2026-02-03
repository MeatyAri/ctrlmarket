"""New user creation screen."""

from typing import Literal, cast

import bcrypt
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Label, Select, Static

from database.queries import create_user
from models import UserCreate


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class UserNewScreen(Screen):
    """Create new user screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("c", "create_user", "Create"),
        ("q", "logout", "Logout"),
    ]

    def compose(self) -> ComposeResult:
        # Header
        with Container(classes="workspace-header"):
            yield Label("CTRL Market - New User", classes="workspace-title")

        # Main content
        with Container(classes="workspace-content"):
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

        # Shortcuts bar
        shortcuts_bar = ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")
        shortcuts_bar.shortcuts = "\[Esc]Back \[c]Create User"
        yield shortcuts_bar

    def action_create_user(self) -> None:
        """Create the user."""
        name = self.query_one("#name", Input).value.strip()
        email = self.query_one("#email", Input).value.strip()
        phone = self.query_one("#phone", Input).value.strip()
        role_select = self.query_one("#role", Select)
        password = self.query_one("#password", Input).value

        if not all([name, email, phone, password]):
            return

        role_value = role_select.value
        if role_value == Select.BLANK:
            role: Literal["Customer", "Specialist", "Admin"] = "Customer"
        else:
            role = cast(Literal["Customer", "Specialist", "Admin"], str(role_value))

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

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.current_user = None
        while len(self.app.screen_stack) > 1:
            self.app.pop_screen()
        self.app.switch_screen("login")
