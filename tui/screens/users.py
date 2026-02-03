"""Users management screen (Admin only)."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Select, Static

from database.queries import (
    delete_user,
    list_users,
)


class UsersScreen(Screen):
    """Users management screen."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("n", "new_user", "New User"),
        ("q", "logout", "Logout"),
    ]

    def __init__(self) -> None:
        self.users: list = []
        self.selected_user_id: int | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="sidebar"):
            yield Label("Users", classes="sidebar-title")
            yield Static("─" * 18)
            with Container(classes="sidebar-menu"):
                yield Button("Back", id="btn-back", classes="sidebar-button")
                yield Button("Refresh", id="btn-refresh", classes="sidebar-button")
                yield Button("New User", id="btn-new", variant="primary")
                yield Button("Edit", id="btn-edit", classes="sidebar-button")
                yield Button("Delete", id="btn-delete", variant="error")

        with Container(classes="main-content"):
            yield Label("User Management", classes="content-title")

            # Filter
            with Horizontal():
                yield Label("Role:", classes="form-label")
                yield Select(
                    [
                        ("All", ""),
                        ("Admin", "Admin"),
                        ("Specialist", "Specialist"),
                        ("Customer", "Customer"),
                    ],
                    id="role-filter",
                    value="",
                )

            with Container(classes="search-container"):
                yield Input(
                    placeholder="Search users...",
                    id="search-input",
                    classes="search-input",
                )
                yield Button("Search", id="btn-search", variant="primary")

            # Users table
            table = DataTable(id="users-table")
            table.add_columns("ID", "Name", "Email", "Phone", "Role")
            table.cursor_type = "row"
            yield table

    def on_mount(self) -> None:
        """Load users when screen mounts."""
        self._load_users()

    def _load_users(self, role: str = "", search: str = "") -> None:
        """Load users into table."""
        table = self.query_one("#users-table", DataTable)
        table.clear()

        role_filter = role if role else None
        self.users = list_users(role=role_filter, search=search if search else None)

        for user in self.users:
            table.add_row(
                str(user.user_id), user.name, user.email, user.phone, user.role
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        row_data = event.data_table.get_row(event.row_key)
        self.selected_user_id = int(row_data[0])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "btn-back":
            self.action_go_back()
        elif btn_id == "btn-refresh":
            self._load_users()
        elif btn_id == "btn-new":
            self.action_new_user()
        elif btn_id == "btn-search":
            self._handle_search()
        elif btn_id == "btn-edit":
            self._handle_edit()
        elif btn_id == "btn-delete":
            self._handle_delete()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter change."""
        if event.select.id == "role-filter":
            value = event.value
            role = str(value) if value != Select.BLANK else ""
            self._load_users(role=role)

    def _handle_search(self) -> None:
        """Handle search."""
        search = self.query_one("#search-input", Input).value
        role_filter = self.query_one("#role-filter", Select)
        role = str(role_filter.value) if role_filter.value != Select.BLANK else ""
        self._load_users(role=role, search=search)

    def _handle_edit(self) -> None:
        """Handle edit button."""
        if self.selected_user_id:
            self.app.push_screen(f"user_edit:{self.selected_user_id}")

    def _handle_delete(self) -> None:
        """Delete selected user."""
        if not self.selected_user_id:
            return

        if delete_user(self.selected_user_id):
            self._load_users()
            self.selected_user_id = None

    def action_go_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.current_user = None
        while len(self.app.screen_stack) > 1:
            self.app.pop_screen()
        self.app.switch_screen("login")

    def action_new_user(self) -> None:
        """Open new user dialog."""
        self.app.push_screen("user_new")
