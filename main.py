"""Entry point for CTRL Market TUI application."""

from tui.app import CtrlMarketApp


def main():
    """Run the application."""
    app = CtrlMarketApp()
    app.run()


if __name__ == "__main__":
    main()
