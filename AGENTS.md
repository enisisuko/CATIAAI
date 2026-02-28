# AGENTS.md

## Cursor Cloud specific instructions

This is a Python MCP server (v0.2) for CATIA V5/V6 CAD automation, integrating multiple open-source projects.

### Quick Reference
- **Run tests**: `pytest tests/ -v` (122 tests, all use mock — no Windows/CATIA needed)
- **Lint**: `ruff check src/ tests/` and `ruff format src/ tests/`
- **Run server**: `python main.py` (starts MCP server on stdio)
- **Install**: `pip install -e ".[dev]"` from repo root

### Architecture Notes
- Connection priority on Windows: pycatia → win32com → mock. On Linux: always mock.
- `pycatia_backend.py` contains the real CATIA API calls mapped to the pycatia library API. Only loaded on Windows.
- `smart_interaction.py` wraps pywinauto for intelligent UI automation. Only loaded on Windows.
- Agent tools (`plan_catia_task`, `analyze_current_state`, etc.) work in both mock and real mode.
- MCP Resources and Prompts are always available regardless of platform.
- `PATH` must include `~/.local/bin` for pip-installed commands to work.
- `pytest-asyncio` mode is set to `auto` in `pyproject.toml`.
