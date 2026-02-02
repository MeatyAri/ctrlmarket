# AGENTS.md - Coding Guidelines for ctrlmarket

## Build & Test Commands
- `uv run main.py` - Run the application
- `uv add <package>` - Add dependencies
- `uv sync` - Sync dependencies from lock file
- `pytest tests/` - Run all tests
- `pytest tests/test_file.py::test_function` - Run single test
- `ruff check .` - Lint code
- `ruff format .` - Format code

## Code Style Guidelines
- **Python**: Use Python 3.12+ syntax, type hints everywhere
- **Imports**: Group: stdlib → third-party → local; use absolute imports
- **Formatting**: 4 spaces, 88 char line limit (Black-compatible)
- **Naming**: snake_case for functions/vars, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use Pydantic v2 models for all data structures
- **Database**: Use raw SQL with sqlite3 (NO ORM allowed), use parameterized queries
- **Error Handling**: Use try/except with specific exceptions, log errors
- **TUI**: Use Textual framework patterns, reactive widgets, CSS styling in .tcss files

## Project Context
Smart Equipment Sales & Services TUI app with SQLite backend.
Entities: User (Customer/Specialist/Admin), Product, Order, OrderItem, ServiceRequest.
All database operations must use raw SQL with proper foreign key constraints.
