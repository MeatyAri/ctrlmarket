"""Shared dialog and UI components for the TUI."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ShortcutsBar(Static):
    """Bar at bottom showing keyboard shortcuts for current context."""

    shortcuts = reactive("")

    def watch_shortcuts(self, shortcuts: str) -> None:
        """Update display when shortcuts change."""
        self.update(shortcuts)


class ConfirmDialog(ModalScreen[bool]):
    """Simple confirmation dialog."""

    def __init__(self, title: str, message: str, on_confirm) -> None:
        self.dialog_title = title
        self.dialog_message = message
        self.on_confirm_callback = on_confirm
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(classes="dialog-container"):
            yield Label(self.dialog_title, classes="dialog-title")
            yield Label(self.dialog_message, classes="dialog-message")
            with Container(classes="dialog-buttons"):
                yield Button("Yes", id="btn-yes", variant="primary")
                yield Button("No", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-yes":
            self.on_confirm_callback(True)
            self.dismiss(True)
        elif event.button.id == "btn-no":
            self.on_confirm_callback(False)
            self.dismiss(False)

    def on_key(self, event) -> None:
        """Handle key press."""
        if event.key == "y":
            yes_btn = self.query_one("#btn-yes", Button)
            self.on_button_pressed(Button.Pressed(yes_btn))
        elif event.key == "n":
            no_btn = self.query_one("#btn-no", Button)
            self.on_button_pressed(Button.Pressed(no_btn))
