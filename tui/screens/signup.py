"""Signup screen for user registration."""

import bcrypt
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Select

from database.queries import create_user, get_user_by_email
from models import SessionUser, UserCreate


class SignupScreen(Screen):
    """Signup screen for new user registration."""

    CSS_PATH = "../css/main.tcss"

    def __init__(self) -> None:
        self.error_label: Label | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="login-container"):
            yield Label("Create Account", classes="login-title")
            yield Label(
                "CTRL Market - Smart Equipment Sales & Services", classes="login-title"
            )
            yield Label("")

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
                placeholder="Enter password (min 6 chars)", password=True, id="password"
            )

            yield Label("Confirm Password:")
            yield Input(
                placeholder="Confirm your password",
                password=True,
                id="confirm_password",
            )

            with Horizontal(classes="form-buttons"):
                yield Button("Sign Up", variant="primary", id="signup-btn")
                yield Button("Back to Login", id="back-btn")

            self.error_label = Label("", classes="login-error")
            yield self.error_label

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "signup-btn":
            self._handle_signup()
        elif event.button.id == "back-btn":
            self.app.push_screen("login")

    def _handle_signup(self) -> None:
        name = self.query_one("#name", Input).value.strip()
        email = self.query_one("#email", Input).value.strip()
        phone = self.query_one("#phone", Input).value.strip()
        role = self.query_one("#role", Select).value
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
        session_user = SessionUser(
            user_id=new_user.user_id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
        )

        self.app.current_user = session_user
        self.app.push_screen("dashboard")
