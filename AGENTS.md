# AGENTS.md

## Cursor Cloud specific instructions

This is a Python MCP server for CATIA CAD automation. Key development notes:

- **Run tests**: `pytest tests/ -v` (85 tests, all use mock CATIA — no Windows/CATIA needed)
- **Lint**: `ruff check src/ tests/` and `ruff format src/ tests/`
- **Run server**: `python main.py` (starts MCP server on stdio transport)
- **Install**: `pip install -e ".[dev]"` from repo root
- The MCP server auto-detects platform — uses COM on Windows, mock mode elsewhere (Linux/macOS). All tests pass on Linux.
- `pytest-asyncio` is required but tests are sync; the async mode is set to `auto` in `pyproject.toml`.
- CATIA COM operations (`pywin32`) only work on Windows with CATIA running. The `[windows]` optional deps are not needed for development/testing on Linux.
- The `PATH` must include `~/.local/bin` for `pytest`, `ruff`, and `catia-mcp` commands to work after `pip install --user`.
