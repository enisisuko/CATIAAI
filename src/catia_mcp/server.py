"""CATIA MCP Server - Main entry point.

This MCP server exposes CATIA V5/V6 automation capabilities to LLMs via the
Model Context Protocol. Integrates:

- pycatia (evereux/pycatia) for CATIA COM automation
- pywinauto for intelligent UI automation
- FastMCP for MCP protocol handling
- Agent workflow engine for CLINE-style thinking chains

Supports 90+ tools across 10 modules:
- System, Sketcher, Part Design, Assembly, Drawing, Surface Design,
  Measurement, Vision/UI, Smart UI (pywinauto), Agent Workflow
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from catia_mcp import prompts, resources
from catia_mcp.tools import (
    agent_tools,
    assembly_tools,
    drawing_tools,
    measure_tools,
    part_tools,
    sketch_tools,
    smart_ui_tools,
    surface_tools,
    system_tools,
    vision_tools,
)

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the CATIA MCP server with all modules registered."""
    mcp = FastMCP(
        "CATIA MCP Server",
        instructions=(
            "Automate CATIA V5/V6 CAD operations via cloud LLM. "
            "Supports Part Design, Sketcher, Assembly, Drawing, Surface Design, "
            "Measurement, Vision/UI automation, and Agent-guided workflows. "
            "Uses pycatia library for CATIA COM and pywinauto for smart UI interaction. "
            "Call connect_catia first, then use plan_catia_task for complex designs."
        ),
    )

    # Core tools
    system_tools.register(mcp)
    sketch_tools.register(mcp)
    part_tools.register(mcp)
    assembly_tools.register(mcp)
    drawing_tools.register(mcp)
    surface_tools.register(mcp)
    measure_tools.register(mcp)

    # Vision & UI automation
    vision_tools.register(mcp)
    smart_ui_tools.register(mcp)

    # Agent workflow engine
    agent_tools.register(mcp)

    # MCP Resources & Prompts
    resources.register(mcp)
    prompts.register(mcp)

    logger.info("CATIA MCP Server initialized with all modules")
    return mcp


server = create_server()


def main() -> None:
    """Run the MCP server via stdio transport."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Starting CATIA MCP Server...")
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
