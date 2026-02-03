"""Profile screen with user info, logout, and users management for admins."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from database.queries import delete_user, get_user_by_id, list_users


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts for current context."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class ProfileSection(Container):
    """Profile information section."""

    def compose(self) -> ComposeResult:
        yield Label("User Profile", classes="profile-title")
        yield Static("")
        with Horizontal(classes="profile-row"):
            yield Label("Name:", classes="profile-label")
            yield Label("", id="profile-name", classes="profile-value")
        with Horizontal(classes="profile-row"):
            yield Label("Email:", classes="profile-label")
            yield Label("", id="profile-email", classes="profile-value")
        with Horizontal(classes="profile-row"):
            yield Label("Phone:", classes="profile-label")
            yield Label("", id="profile-phone", classes="profile-value")
        with Horizontal(classes="profile-row"):
            yield Label("Role:", classes="profile-label")
            yield Label("", id="profile-role", classes="profile-value")
        yield Static("")
        yield Label("Press \\[q] to logout", classes="nav-hint")


class UsersSection(Container):
    """Users management section."""

    def compose(self) -> ComposeResult:
        yield Label("User Management", classes="users-title")
        # Filter bar
        with Container(classes="search-container"):
            yield Label("Role:", classes="form-label")
            yield Select(
                [
                    ("All", ""),
                    ("Admin", "Admin"),
                    ("Specialist", "Specialist"),
                    ("Customer", "Customer"),
                ],
                value="",
                id="role-filter",
            )
            yield Input(
                placeholder="Search users... (Press Enter)",
                id="users-search",
                classes="search-input",
            )
        # Users table
        table = DataTable(id="users-table")
        table.add_columns("ID", "Name", "Email", "Phone", "Role")
        table.cursor_type = "row"
        yield table


class ProfileScreen(Screen):
    """Profile screen with user info and admin users management."""

    CSS_PATH = "../css/main.tcss"

    BINDINGS = [
        ("alt+1", "switch_tab('profile')", "Profile"),
        ("alt+2", "switch_tab('users')", "Users"),
        ("escape", "go_back", "Back"),
        ("q", "logout", "Logout"),
        ("n", "new_user", "New User"),
        ("e", "edit_user", "Edit"),
        ("d", "delete_user", "Delete"),
        ("r", "refresh", "Refresh"),
        ("ctrl+s", "focus_search", "Focus Search"),
        ("/", "focus_search", "Focus Search"),
    ]

    def __init__(self) -> None:
        self.users: list = []
        self.selected_user_id: int | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="screen-layout"):
            with Container(classes="profile-header"):
                yield Label("CTRL Market - Profile", classes="workspace-title")

            with Container(classes="profile-content"):
                current_user = getattr(self.app, "current_user", None)
                is_admin = current_user and current_user.role == "Admin"

                if is_admin:
                    with TabbedContent(initial="profile"):
                        with TabPane("My Profile \\[1]", id="profile"):
                            yield ProfileSection(classes="profile-container")

                        with TabPane("Users \\[2]", id="users"):
                            yield UsersSection(classes="users-section")
                else:
                    yield ProfileSection(classes="profile-container")

            yield ShortcutsBar(id="shortcuts-bar", classes="shortcuts-bar")

    def on_mount(self) -> None:
        """Load data when screen mounts."""
        self._load_profile()
        current_user = getattr(self.app, "current_user", None)
        is_admin = current_user and current_user.role == "Admin"
        if is_admin:
            self._load_users()
        self._update_shortcuts()

    def on_screen_resume(self) -> None:
        """Reload profile data when screen is resumed (e.g., after login/logout)."""
        self._load_profile()
        current_user = getattr(self.app, "current_user", None)
        is_admin = current_user and current_user.role == "Admin"
        if is_admin:
            self._load_users()
        self._update_shortcuts()

    def _load_profile(self) -> None:
        """Load current user profile."""
        current_user = getattr(self.app, "current_user", None)
        if current_user:
            # Get fresh data from database
            user = get_user_by_id(current_user.user_id)
            if user:
                self.query_one("#profile-name", Label).update(user.name)
                self.query_one("#profile-email", Label).update(user.email)
                self.query_one("#profile-phone", Label).update(user.phone or "N/A")
                self.query_one("#profile-role", Label).update(user.role)

    def _load_users(self, role: str = "", search: str = "") -> None:
        """Load users into table."""
        table = self.query_one("#users-table", DataTable)
        if table:
            table.clear()

            role_filter = role if role else None
            self.users = list_users(role=role_filter, search=search if search else None)

            for user in self.users:
                table.add_row(
                    str(user.user_id), user.name, user.email, user.phone, user.role
                )

    def _update_shortcuts(self) -> None:
        """Update shortcuts bar based on current tab and role."""
        current_user = getattr(self.app, "current_user", None)
        is_admin = current_user and current_user.role == "Admin"

        shortcuts = []

        if is_admin:
            shortcuts.append("\\[Alt+1]Profile \\[Alt+2]Users")
        shortcuts.append("\\[Esc]Back \\[q]Logout")

        if is_admin:
            # Check if on users tab
            try:
                tabbed = self.query_one(TabbedContent)
                if tabbed.active == "users":
                    shortcuts.append("\\[n]New \\[e]Edit \\[d]Delete \\[/]Search")
            except Exception:
                pass
            shortcuts.append("\\[r]Refresh")

        shortcuts_bar = self.query_one("#shortcuts-bar", ShortcutsBar)
        shortcuts_bar.shortcuts = "  |  ".join(shortcuts)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        if event.data_table.id == "users-table":
            row_data = event.data_table.get_row(event.row_key)
            self.selected_user_id = int(row_data[0])

    def on_tabbed_content_tab_activated(self) -> None:
        """Update shortcuts when tab changes."""
        self._update_shortcuts()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "users-search":
            search = event.value
            role_filter = self.query_one("#role-filter", Select)
            role = str(role_filter.value) if role_filter.value != Select.BLANK else ""
            self._load_users(role=role, search=search)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter change."""
        if event.select.id == "role-filter":
            value = event.value
            role = str(value) if value != Select.BLANK else ""
            search_input = self.query_one("#users-search", Input)
            search = search_input.value if search_input else ""
            self._load_users(role=role, search=search)

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to specified tab."""
        current_user = getattr(self.app, "current_user", None)
        is_admin = current_user and current_user.role == "Admin"

        if is_admin:
            tabbed = self.query_one(TabbedContent)
            tabbed.active = tab_id

    def action_go_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        self.app.logout()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        current_user = getattr(self.app, "current_user", None)
        is_admin = current_user and current_user.role == "Admin"

        if is_admin:
            # Check if on users tab
            try:
                tabbed = self.query_one(TabbedContent)
                if tabbed.active == "users":
                    search_input = self.query_one("#users-search", Input)
                    search_input.focus()
            except Exception:
                pass

    def action_new_user(self) -> None:
        """Open new user dialog."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role != "Admin":
            return

        self.app.push_screen("user_new")

    def action_edit_user(self) -> None:
        """Edit selected user."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role != "Admin":
            return

        if self.selected_user_id:
            self.app.push_screen(f"user_edit:{self.selected_user_id}")

    def action_delete_user(self) -> None:
        """Delete selected user."""
        current_user = getattr(self.app, "current_user", None)
        if not current_user or current_user.role != "Admin":
            return

        user_id = self.selected_user_id
        if not user_id:
            return

        if delete_user(user_id):
            self._load_users()
            self.selected_user_id = None

    def action_refresh(self) -> None:
        """Refresh data."""
        self._load_profile()
        current_user = getattr(self.app, "current_user", None)
        is_admin = current_user and current_user.role == "Admin"
        if is_admin:
            self._load_users()
