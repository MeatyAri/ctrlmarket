"""Login screen for authentication."""

import bcrypt
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from database.queries import authenticate_user, get_user_password_hash
from models import LoginCredentials


class LoginScreen(Screen):
    """Login screen with email and password authentication."""

    CSS_PATH = "../css/main.tcss"

    def __init__(self) -> None:
        self.error_label: Label | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="login-container"):
            yield Label("CTRL Market", classes="login-title")
            yield Label("Smart Equipment Sales & Services", classes="login-title")
            yield Label("")
            yield Label("Email:")
            yield Input(placeholder="Enter your email", id="email")
            yield Label("Password:")
            yield Input(placeholder="Enter your password", password=True, id="password")
            yield Button("Login", variant="primary", id="login-btn")
            yield Label("")
            yield Label("Don't have an account?", classes="login-title")
            yield Button("Sign Up", id="signup-btn")
            self.error_label = Label("", classes="login-error")
            yield self.error_label

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            self._handle_login()
        elif event.button.id == "signup-btn":
            self.app.push_screen("signup")

    def _handle_login(self) -> None:
        email = self.query_one("#email", Input).value.strip()
        password = self.query_one("#password", Input).value

        if not email or not password:
            if self.error_label:
                self.error_label.update("Please enter both email and password")
            return

        # Get stored password hash
        stored_hash = get_user_password_hash(email)

        if not stored_hash:
            if self.error_label:
                self.error_label.update("Invalid email or password")
            return

        # Verify password with bcrypt
        if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
            if self.error_label:
                self.error_label.update("Invalid email or password")
            return

        # Authentication successful
        credentials = LoginCredentials(email=email, password=password)
        user = authenticate_user(credentials)

        if user:
            # Store user in app state
            self.app.current_user = user
            # Navigate to dashboard
            self.app.push_screen("dashboard")
        else:
            if self.error_label:
                self.error_label.update("Authentication failed")
