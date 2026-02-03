"""Login screen for authentication."""

import bcrypt
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Label, Static

from database.queries import authenticate_user, get_user_password_hash
from models import LoginCredentials


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class LoginScreen(Screen):
    """Login screen with email and password authentication."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("enter", "login", "Login"),
        ("alt+2", "go_signup", "Sign Up"),
    ]

    def __init__(self) -> None:
        self.error_label: Label | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        # Header
        with Container(classes="workspace-header"):
            yield Label("CTRL Market", classes="login-title")

        # Main content - centered login form
        with Container(classes="workspace-content"):
            with Container(classes="login-container"):
                yield Label("Smart Equipment Sales & Services", classes="login-title")
                yield Static("")
                yield Label("Email:")
                yield Input(placeholder="Enter your email", id="email")
                yield Label("Password:")
                yield Input(
                    placeholder="Enter your password", password=True, id="password"
                )
                yield Static("")
                yield Label(
                    "Don't have an account? Press \[Alt+2] to sign up",
                    classes="login-title",
                )
                self.error_label = Label("", classes="login-error")
                yield self.error_label

        # Shortcuts bar
        shortcuts_bar = ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")
        shortcuts_bar.shortcuts = "\[Enter]Login \[Alt+2]Sign Up"
        yield shortcuts_bar

    def action_login(self) -> None:
        """Handle login action."""
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

    def action_go_signup(self) -> None:
        """Navigate to signup screen."""
        self.app.push_screen("signup")

    def _on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in any input field."""
        self.action_login()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in any input field."""
        self.action_login()
