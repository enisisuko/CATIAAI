"""CATIA MCP Server - Main entry point.

This MCP server exposes CATIA V5/V6 automation capabilities to LLMs via the
Model Context Protocol. It supports:

- Part Design: Pad, Pocket, Shaft, Groove, Fillet, Chamfer, Shell, Hole, Pattern, Mirror
- Sketcher: Lines, Circles, Rectangles, Arcs, Splines, Constraints, Dimensions
- Assembly Design: Component insertion, Constraints (Coincidence, Contact, Offset, Angle, Fix)
- Drawing/Drafting: Views, Dimensions, Annotations
- Generative Shape Design: Extrude, Revolve, Sweep, Fill, Loft, Offset, Trim, Split, Join
- Measurement: Distance, Angle, Area, Volume, Inertia
- Vision/UI Automation: Screenshots, Click, Drag, Type, Keyboard shortcuts
- System: Document management, Feature tree, Parameters, VBA macros, Undo/Redo

On Windows with CATIA running, operations are performed via COM automation.
On other platforms or when CATIA is unavailable, a mock mode is used for development/testing.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from catia_mcp.tools import (
    assembly_tools,
    drawing_tools,
    measure_tools,
    part_tools,
    sketch_tools,
    surface_tools,
    system_tools,
    vision_tools,
)

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the CATIA MCP server with all tools registered."""
    mcp = FastMCP(
        "CATIA MCP Server",
        instructions=(
            "Automate CATIA V5/V6 CAD operations via cloud LLM. "
            "Supports Part Design, Sketcher, Assembly, Drawing, Surface Design, "
            "Measurement, and Vision-based UI automation."
        ),
    )

    system_tools.register(mcp)
    sketch_tools.register(mcp)
    part_tools.register(mcp)
    assembly_tools.register(mcp)
    drawing_tools.register(mcp)
    surface_tools.register(mcp)
    measure_tools.register(mcp)
    vision_tools.register(mcp)

    logger.info("CATIA MCP Server initialized with all tool modules")
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
