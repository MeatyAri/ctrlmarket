"""Signup screen for user registration."""

import bcrypt
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Label, Select, Static

from database.queries import create_user, get_user_by_email
from models import SessionUser, UserCreate


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class SignupScreen(Screen):
    """Signup screen for new user registration."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("enter", "signup", "Sign Up"),
        ("alt+1", "go_back", "Back to Login"),
    ]

    def __init__(self) -> None:
        self.error_label: Label | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        # Header
        with Container(classes="workspace-header"):
            yield Label("CTRL Market", classes="login-title")

        # Main content
        with Container(classes="workspace-content"):
            with Container(classes="login-container"):
                yield Label("Create Account", classes="login-title")
                yield Label("Smart Equipment Sales & Services", classes="login-title")
                yield Static("")

                yield Label("Name:")
                yield Input(placeholder="Enter your full name", id="name")

                yield Label("Email:")
                yield Input(placeholder="Enter your email", id="email")

                yield Label("Phone:")
                yield Input(placeholder="Enter your phone number", id="phone")

                yield Label("Role:")
                yield Select(
                    [
                        ("Customer", "Customer"),
                        ("Specialist", "Specialist"),
                        ("Admin", "Admin"),
                    ],
                    allow_blank=False,
                    value="Customer",
                    id="role",
                )

                yield Label("Password:")
                yield Input(
                    placeholder="Enter password (min 6 chars)",
                    password=True,
                    id="password",
                )

                yield Label("Confirm Password:")
                yield Input(
                    placeholder="Confirm your password",
                    password=True,
                    id="confirm_password",
                )

                yield Static("")
                yield Label(
                    "Press \[Enter] to sign up, \[Alt+1] to go back",
                    classes="login-title",
                )
                self.error_label = Label("", classes="login-error")
                yield self.error_label

        # Shortcuts bar
        shortcuts_bar = ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")
        shortcuts_bar.shortcuts = "\\[Enter\\]Sign Up \\[Alt+1\\]Back to Login"
        yield shortcuts_bar

    def action_signup(self) -> None:
        """Handle signup action."""
        name = self.query_one("#name", Input).value.strip()
        email = self.query_one("#email", Input).value.strip()
        phone = self.query_one("#phone", Input).value.strip()
        role_select = self.query_one("#role", Select)
        password = self.query_one("#password", Input).value
        confirm_password = self.query_one("#confirm_password", Input).value

        # Validate required fields
        if not all([name, email, phone, password]):
            if self.error_label:
                self.error_label.update("Please fill in all required fields")
            return

        # Validate password match
        if password != confirm_password:
            if self.error_label:
                self.error_label.update("Passwords do not match")
            return

        # Validate password length
        if len(password) < 6:
            if self.error_label:
                self.error_label.update("Password must be at least 6 characters")
            return

        # Get role value safely
        role_value = role_select.value
        if role_value is None or role_value == Select.BLANK:
            role: str = "Customer"
        elif hasattr(role_value, "value"):
            role = role_value.value
        else:
            role = str(role_value)

        # Check for duplicate email
        existing_user = get_user_by_email(email)
        if existing_user:
            if self.error_label:
                self.error_label.update("Email already registered")
            return

        # Create user with Pydantic validation
        try:
            user_data = UserCreate(
                name=name,
                email=email,
                phone=phone,
                role=role,
                password=password,
            )
        except Exception as e:
            if self.error_label:
                self.error_label.update(f"Validation error: {e}")
            return

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Create user in database
        try:
            new_user = create_user(user_data, password_hash)
        except Exception as e:
            if self.error_label:
                self.error_label.update(f"Failed to create account: {e}")
            return

        # Auto-login: Create session user and navigate to dashboard
        user_id = new_user.user_id
        if user_id is None:
            if self.error_label:
                self.error_label.update("Failed to create user")
            return

        session_user = SessionUser(
            user_id=user_id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
        )

        self.app.current_user = session_user
        self.app.push_screen("dashboard")

    def action_go_back(self) -> None:
        """Navigate back to login screen."""
        self.app.pop_screen()

    def _on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in any input field."""
        self.action_signup()
