"""Main Textual application for CTRL Market."""

from textual.app import App

from database.connection import init_database
from models import SessionUser
from tui.screens.dashboard import DashboardScreen
from tui.screens.login import LoginScreen
from tui.screens.order_new import OrderNewScreen
from tui.screens.product_edit import ProductEditScreen
from tui.screens.product_new import ProductNewScreen
from tui.screens.profile import ProfileScreen
from tui.screens.service_new import ServiceNewScreen
from tui.screens.signup import SignupScreen
from tui.screens.user_new import UserNewScreen
from tui.screens.workspace import WorkspaceScreen


class CtrlMarketApp(App):
    """Main application for Smart Equipment Sales & Services."""

    CSS_PATH = "css/main.tcss"

    SCREENS = {
        "login": LoginScreen,
        "signup": SignupScreen,
        "dashboard": DashboardScreen,
        "workspace": WorkspaceScreen,
        "profile": ProfileScreen,
        "order_new": OrderNewScreen,
        "product_edit": ProductEditScreen,
        "product_new": ProductNewScreen,
        "service_new": ServiceNewScreen,
        "user_new": UserNewScreen,
    }

    def __init__(self) -> None:
        self.current_user: SessionUser | None = None
        super().__init__()

    def on_mount(self) -> None:
        """Initialize database and show login screen."""
        init_database()
        self.push_screen("login")

    def logout(self) -> None:
        """Logout the current user and return to login screen."""
        self.current_user = None
        self._screen_stack.clear()
        self.push_screen("login")


def main():
    """Run the application."""
    app = CtrlMarketApp()
    app.run()


if __name__ == "__main__":
    main()
